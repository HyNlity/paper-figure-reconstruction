const path=require('path'),fs=require('fs'),os=require('os');
let sharp;
for(const root of [process.env.PFR_NODE_MODULES, null, path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]){
 try{sharp=require(root?path.join(root,'sharp'):'sharp');break}catch(e){}
}
if(!sharp)throw Error('Sharp missing. Set PFR_NODE_MODULES to an existing node_modules directory; no installation attempted.');
(async()=>{const [src,dst]=process.argv.slice(2);if(!src||!dst)throw Error('Usage: render_svg.cjs input.svg output.png');fs.mkdirSync(path.dirname(path.resolve(dst)),{recursive:true});await sharp(src,{density:72}).png().toFile(dst);console.log(JSON.stringify(await sharp(dst).metadata()));})().catch(e=>{console.error(e);process.exitCode=1});
