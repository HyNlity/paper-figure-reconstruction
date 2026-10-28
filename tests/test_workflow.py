import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/figure.py'
INSTALL = ROOT / 'scripts/install_skill.py'

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.p = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result
    def spec(self):
        return {'version':1, 'canvas':{'width':200, 'height':120}, 'components':[
            {'id':'panel','type':'group'},
            {'id':'label','parent':'panel','type':'text','x':.1,'y':.2,'text':'Pump'},
            {'id':'arrow','parent':'panel','type':'line','x1':.1,'y1':.5,'x2':.8,'y2':.5,'stroke':'#333333','stroke_width':3,'arrow':True}]}
    def save_spec(self, value):
        p=self.p/'figure-spec.json';p.write_text(json.dumps(value));return p
    def test_native_arrow_text_and_actual_edit(self):
        value=self.spec();spec=self.save_spec(value);out=self.p/'figure.svg'
        self.run_cli('svg','--spec',spec,'--out',out)
        root=ET.parse(out).getroot();ns={'s':'http://www.w3.org/2000/svg'}
        self.assertEqual(root.find('.//s:text',ns).text,'Pump')
        self.assertIsNotNone(root.find('.//s:line[@id="arrow-shaft"]',ns))
        self.assertIsNotNone(root.find('.//s:path[@id="arrow-head"]',ns))
        self.assertEqual(len(root.findall('.//s:image',ns)),0)
        value['components'][1]['text']='Probe';self.save_spec(value)
        self.run_cli('svg','--spec',spec,'--out',out)
        self.assertEqual(ET.parse(out).find('.//s:text',ns).text,'Probe')
        self.run_cli('audit-svg','--svg',out)
    def test_reference_raster_and_duplicate_id_rejected(self):
        s=self.spec();s['components'].append({'id':'reference','type':'image','x':0,'y':0,'w':1,'h':1,'path':'paper.png'})
        self.run_cli('svg','--spec',self.save_spec(s),'--out',self.p/'bad.svg',ok=False)
        s=self.spec();s['components'][1]['id']='panel'
        self.run_cli('svg','--spec',self.save_spec(s),'--out',self.p/'bad.svg',ok=False)
    def compare(self, reference, candidate, label):
        out=self.p/label
        self.run_cli('compare','--reference',reference,'--candidate',candidate,'--out',out)
        return json.loads((out/'metrics.json').read_text())['full']
    def test_identity_translation_and_missing_structure(self):
        im=Image.new('RGB',(96,64),'white');draw=ImageDraw.Draw(im);draw.rectangle((15,15,40,40),fill='navy');draw.line((45,28,80,28),fill='black',width=3)
        a=self.p/'a.png';im.save(a)
        same=self.compare(a,a,'same');self.assertAlmostEqual(same['ssim'],1,places=7);self.assertEqual(same['contour']['mean_px'],0)
        shifted=Image.new('RGB',im.size,'white');shifted.paste(im,(6,4));b=self.p/'b.png';shifted.save(b)
        moved=self.compare(a,b,'moved');self.assertLess(moved['ssim'],same['ssim']);self.assertGreater(moved['contour']['mean_px'],0)
        missing=im.copy();ImageDraw.Draw(missing).rectangle((44,25,84,31),fill='white');missing.save(b)
        gone=self.compare(a,b,'missing');self.assertGreater(gone['mae_rgb_0_1'],0)
        blank=Image.new('RGB',im.size,'white');blank.save(b);absent=self.compare(a,b,'absent');self.assertEqual(absent['contour']['status'],'missing_contour')
        Image.new('RGB',(20,20),'white').save(b)
        self.run_cli('compare','--reference',a,'--candidate',b,'--out',self.p/'mismatch',ok=False)
    def test_install_update_retains_local_backup(self):
        target=self.p/'codex/skills/paper-figure-reconstruction'
        def run(*args):
            return subprocess.run([sys.executable,str(INSTALL),'--target',str(target),*args],capture_output=True,text=True)
        first=run();self.assertEqual(first.returncode,0,first.stderr)
        (target/'local-note.txt').write_text('preserve me')
        self.assertNotEqual(run().returncode,0)
        update=run('--update');self.assertEqual(update.returncode,0,update.stderr)
        backup=Path(json.loads(update.stdout)['backup']);self.assertEqual((backup/'local-note.txt').read_text(),'preserve me')
        self.assertFalse((target/'local-note.txt').exists());self.assertTrue((target/'SKILL.md').exists())
        self.assertFalse((target/'README.md').exists())

if __name__=='__main__':unittest.main()
