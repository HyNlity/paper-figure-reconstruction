#!/usr/bin/env python3
"""Local, deterministic helpers. Requires numpy/Pillow only for comparisons."""
import argparse, json, sys, os, subprocess, shlex, shutil, hashlib, platform
from pathlib import Path
import xml.etree.ElementTree as ET

def write_json(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def spec_read(p):
 p=Path(p).resolve(); s=json.loads(p.read_text());assert s['version']==1,'Unsupported spec version'
 assert all(isinstance(s['canvas'][k],int) and s['canvas'][k]>0 for k in ('width','height'))
 cs=s.get('components',[]);ids=[c['id'] for c in cs];assert len(ids)==len(set(ids)),'Duplicate component IDs'
 by={c['id']:c for c in cs}
 for c in cs:
  seen={c['id']};parent=c.get('parent')
  while parent:
   assert parent in by and by[parent]['type']=='group','Parent must be a group'
   assert parent not in seen,'Cyclic hierarchy';seen.add(parent);parent=by[parent].get('parent')
 return p,s

def svg_build(a):
 p,s=spec_read(a.spec);w,h=s['canvas']['width'],s['canvas']['height'];ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
 root=ET.Element('{'+ns+'}svg',{'width':str(w),'height':str(h),'viewBox':f'0 0 {w} {h}'})
 ET.SubElement(root,'metadata').text=json.dumps({'source':s.get('source'), 'generator':'paper-figure-reconstruction'})
 ET.SubElement(root,'rect',{'width':str(w),'height':str(h),'fill':s['canvas'].get('background','#ffffff')})
 defs=ET.SubElement(root,'defs'); nodes={};cs={c['id']:c for c in s.get('components',[])}
 def add(c):
  if c['id'] in nodes:return nodes[c['id']]
  parent=add(cs[c['parent']]) if c.get('parent') else root;t=c['type'];attrs={'id':c['id']}
  for k in ['fill','stroke','opacity','stroke_width','font_family','font_size','text_anchor']:
   if k in c:attrs[k.replace('_','-')]=str(c[k])
  if t=='group':tag='g'
  elif t=='text':
   tag='text';attrs.update(x=str(c['x']*w),y=str(c['y']*h));attrs.setdefault('font-family','Arial');attrs.setdefault('font-size','20')
  elif t in ('rect','image'):
   tag=t;attrs.update(x=str(c['x']*w),y=str(c['y']*h),width=str(c['w']*w),height=str(c['h']*h))
   if t=='image':
    assert c.get('provenance')=='own_blender_render' and c.get('source_blend'),'Undeclared image provenance'
    src=(p.parent/c['path']).resolve();assert src.is_file(),src;assert (p.parent/c['source_blend']).is_file(),'Missing source blend'
    import base64,mimetypes
    attrs['href']='data:'+ (mimetypes.guess_type(src)[0] or 'image/png')+';base64,'+base64.b64encode(src.read_bytes()).decode();attrs['data-provenance']='own_blender_render'
  elif t=='ellipse':
   tag=t;attrs.update({k:str(c[k]*(w if k in ('cx','rx') else h)) for k in ('cx','cy','rx','ry')})
  elif t=='line':
   tag=t;attrs.update({k:str(c[k]*(w if k.startswith('x') else h)) for k in ('x1','y1','x2','y2')})
   if c.get('arrow'):
    # Explicit editable shaft/head avoids Illustrator dropping marker-bearing shafts.
    import math
    x1,y1,x2,y2=c['x1']*w,c['y1']*h,c['x2']*w,c['y2']*h
    le=math.hypot(x2-x1,y2-y1);assert le>0,'Zero-length arrow'
    ux,uy=(x2-x1)/le,(y2-y1)/le;q=4*float(c.get('stroke_width',1))/10
    pts=[(x2+ux*xx*q-uy*yy*q,y2+uy*xx*q+ux*yy*q) for xx,yy in [(-9,-5),(1,0),(-9,5)]]
    group=ET.SubElement(parent,'g',{'id':c['id']});attrs['id']=c['id']+'-shaft';ET.SubElement(group,'line',attrs)
    ET.SubElement(group,'path',{'id':c['id']+'-head','d':'M '+' L '.join(f'{x},{y}' for x,y in pts)+' Z','fill':c.get('stroke','#000')})
    nodes[c['id']]=group;return group
  elif t=='path':tag=t;attrs.update(d=c['d'],transform=f'scale({w},{h})');attrs['vector-effect']='non-scaling-stroke'
  else:raise ValueError('Unsupported 2D type '+t)
  e=ET.SubElement(parent,tag,attrs);nodes[c['id']]=e
  if t=='text':
   e.text=c.get('text','')
   for sp in c.get('spans',[]):
    at={k.replace('_','-'):str(v) for k,v in sp.items() if k!='text'};ET.SubElement(e,'tspan',at).text=sp['text']
  return e
 for c in s.get('components',[]):add(c)
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);ET.ElementTree(root).write(out,encoding='utf-8',xml_declaration=True);print(out)

def audit(a):
 r=ET.parse(a.svg).getroot();counts={};images=[];issues=[];ids=[]
 for e in r.iter():
  tag=e.tag.split('}')[-1];counts[tag]=counts.get(tag,0)+1
  if 'id'in e.attrib:ids.append(e.attrib['id'])
  if tag=='script' or tag=='foreignObject' or any(k.lower().startswith('on') for k in e.attrib):issues.append('active content: '+tag)
  if tag=='image':
   href=e.get('href',e.get('{http://www.w3.org/1999/xlink}href',''));images.append({'id':e.get('id'),'provenance':e.get('data-provenance'),'embedded':href.startswith('data:')})
   if e.get('data-provenance')!='own_blender_render':issues.append('unverified raster '+str(e.get('id')))
   if not href.startswith('data:'):issues.append('external image resource')
 if len(ids)!=len(set(ids)):issues.append('duplicate IDs')
 if not r.get('viewBox'):issues.append('missing viewBox')
 result={'counts':counts,'images':images,'issues':issues,'native_text':counts.get('text',0),'note':'DOM inspection; perform edit/rerender tests separately'}
 if a.out:write_json(a.out,result)
 print(json.dumps(result,indent=2));return bool(issues)

def doctor(a):
 import importlib.util,plistlib
 apps={}
 for name,path in [('blender','/Applications/Blender.app'),('illustrator','/Applications/Adobe Illustrator 2026/Adobe Illustrator.app')]:
  p=Path(path);d={'path':path,'installed':p.exists(),'runtime_verified':False}
  if p.exists():
   try:d['version']=plistlib.loads((p/'Contents/Info.plist').read_bytes()).get('CFBundleShortVersionString')
   except Exception:pass
  apps[name]=d
 config=Path.home()/'.codex/config.toml';mcp=[]
 if config.exists():
  import re
  mcp=[name for name in re.findall(r'^\[mcp_servers\.([^\]]+)\]',config.read_text(),re.M) if not name.endswith('.env')]
 d={'python':sys.executable,'python_version':platform.python_version(),'packages':{k:bool(importlib.util.find_spec(k)) for k in ['numpy','PIL']},'executables':{k:shutil.which(k) for k in ['node','pdftoppm','pdftotext','inkscape']},'apps':apps,'mcp_config_sections':mcp,'mcp_scope':'Only ~/.codex/config.toml; inspect session tool catalog separately. No credentials read into report.'}
 if a.out:write_json(a.out,d)
 print(json.dumps(d,indent=2))

def compare(a):
 import numpy as np
 from PIL import Image
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 def read(p):
  im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,a.background);return np.asarray(Image.alpha_composite(bg,im).convert('RGB'),dtype=float)/255
 x,y=read(a.reference),read(a.candidate);assert x.shape==y.shape,'Canvas mismatch: resize/crop explicitly and record transform'
 def gray(z):return z@np.array([.2126,.7152,.0722])
 def metrics(x,y):
  gx,gy=gray(x),gray(y);n=min(11,*gx.shape);n-=1-n%2
  def avg(z):
   q=np.pad(z,((1,0),(1,0))).cumsum(0).cumsum(1);return (q[n:,n:]-q[:-n,n:]-q[n:,:-n]+q[:-n,:-n])/(n*n)
  ux,uy=avg(gx),avg(gy);vx=np.maximum(0,avg(gx*gx)-ux*ux);vy=np.maximum(0,avg(gy*gy)-uy*uy);cov=avg(gx*gy)-ux*uy
  ss=((2*ux*uy+.01**2)*(2*cov+.03**2))/((ux*ux+uy*uy+.01**2)*(vx+vy+.03**2))
  def edges(g):
   dx=np.zeros_like(g);dy=dx.copy();dx[:,1:]=abs(np.diff(g,axis=1));dy[1:,:]=abs(np.diff(g,axis=0));return np.argwhere(np.hypot(dx,dy)>.08)
  ea,eb=edges(gx),edges(gy)
  def near(aa,bb):
   result=[]
   for i in range(0,len(aa),256):
    lo=np.full(min(256,len(aa)-i),np.inf)
    for j in range(0,len(bb),2048):
     d=aa[i:i+256,None,:]-bb[None,j:j+2048,:];lo=np.minimum(lo,(d*d).sum(2).min(1))
    result.extend(np.sqrt(lo).tolist())
   return result
  if len(ea) and len(eb):
   ds=near(ea,eb)+near(eb,ea);cont={'status':'ok','mean_px':float(np.mean(ds)),'p95_px':float(np.percentile(ds,95))}
  else:cont={'status':'both_empty' if not len(ea) and not len(eb) else 'missing_contour','mean_px':0 if not len(ea) and not len(eb) else None,'p95_px':None}
  return {'ssim':float(ss.mean()),'mae_rgb_0_1':float(abs(x-y).mean()),'contour':cont}
 d={'method':{'ssim':'local uniform window <=11, population covariance, grayscale, K1=.01 K2=.03','contour':'symmetric nearest gradient pixels, threshold .08; exact blocked search','alignment':'none','background':a.background},'reference_sha256':hashlib.sha256(Path(a.reference).read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(Path(a.candidate).read_bytes()).hexdigest(),'full':metrics(x,y),'regions':{}}
 if a.spec:
  _,s=spec_read(a.spec);h,w=x.shape[:2]
  for p in s.get('panels',[])+s.get('protected_regions',[]):
   xx,yy,ww,hh=p['bbox'];l,t,r,b=round(xx*w),round(yy*h),round((xx+ww)*w),round((yy+hh)*h);assert 0<=l<r<=w and 0<=t<b<=h
   d['regions'][p['id']]=metrics(x[t:b,l:r],y[t:b,l:r]);d['regions'][p['id']]['pixel_identical']=bool(np.array_equal(x[t:b,l:r],y[t:b,l:r]))
 Image.fromarray(np.uint8(np.clip((x+y)/2,0,1)*255)).save(out/'overlay.png')
 Image.fromarray(np.uint8(np.clip(abs(x-y)*4,0,1)*255)).save(out/'difference_x4.png')
 write_json(out/'metrics.json',d);print(json.dumps(d,indent=2))

def blender(a):
 p,s=spec_read(a.spec);script=Path(a.script).resolve() if a.script else Path(__file__).with_name('blender_scene.py').resolve()
 cmd=[a.executable,'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',str(script),'--','--spec',str(p),'--out',str(Path(a.out).resolve())]
 if a.dry_run:print(shlex.join(cmd))
 else:raise SystemExit('Execute the dry-run command through the host approval mechanism; runner does not bypass permissions.')

def illustrator(a):
 p,s=spec_read(a.spec);svg=Path(a.svg).resolve();assert svg.is_file();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 # Audit before creating any application document.
 if audit(argparse.Namespace(svg=str(svg),out=None)):raise ValueError('SVG audit failed')
 tree=ET.parse(svg);root=tree.getroot();by={c['id']:c for c in s.get('components',[])};placements=[]
 for node in list(root.iter()):
  if node.tag.split('}')[-1]!='image':continue
  c=by.get(node.get('id'));assert c and c['type']=='image' and c.get('provenance')=='own_blender_render','Image needs corresponding own-render spec component'
  src=(p.parent/c['path']).resolve();blend=(p.parent/c['source_blend']).resolve();assert src.is_file() and blend.is_file(),'Missing own-render source'
  assert 'transform' not in node.attrib,'Transformed images need a custom Illustrator adapter'
  placements.append({'id':c['id'],'path':str(src),'source_blend':str(blend)})
  attrs={k:v for k,v in node.attrib.items() if k in ('id','x','y','width','height')};attrs['fill']='#ff00ff';node.tag='{http://www.w3.org/2000/svg}rect';node.attrib.clear();node.attrib.update(attrs)
 # Avoid Illustrator's SVG data-URI import path; place PNGs through its native API.
 import_svg=out/'illustrator-vectors.svg';ET.register_namespace('','http://www.w3.org/2000/svg');tree.write(import_svg,encoding='utf-8',xml_declaration=True)
 template=Path(__file__).with_name('illustrator_import.jsx').read_text();template=template.replace('__SVG_PATH__',json.dumps(str(import_svg))).replace('__OUTPUT_DIR__',json.dumps(str(out))).replace('__PLACEMENTS__',json.dumps(placements))
 (out/'import.jsx').write_text(template);print(out/'import.jsx')

def main():
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 q=sub.add_parser('doctor');q.add_argument('--out');q.set_defaults(func=doctor)
 q=sub.add_parser('svg');q.add_argument('--spec',required=True);q.add_argument('--out',required=True);q.set_defaults(func=svg_build)
 q=sub.add_parser('audit-svg');q.add_argument('--svg',required=True);q.add_argument('--out');q.set_defaults(func=audit)
 q=sub.add_parser('compare');q.add_argument('--reference',required=True);q.add_argument('--candidate',required=True);q.add_argument('--out',required=True);q.add_argument('--spec');q.add_argument('--background',default='#ffffff');q.set_defaults(func=compare)
 q=sub.add_parser('blender');q.add_argument('--spec',required=True);q.add_argument('--out',required=True);q.add_argument('--script');q.add_argument('--executable',default='/Applications/Blender.app/Contents/MacOS/Blender');q.add_argument('--dry-run',action='store_true');q.set_defaults(func=blender)
 q=sub.add_parser('illustrator');q.add_argument('--spec',required=True);q.add_argument('--svg',required=True);q.add_argument('--out',required=True);q.set_defaults(func=illustrator)
 a=p.parse_args();return a.func(a)
if __name__=='__main__':sys.exit(main() or 0)
