#target illustrator
(function(){
 var input=new File(__SVG_PATH__),out=new Folder(__OUTPUT_DIR__),placements=__PLACEMENTS__;
 for(var pi=0;pi<placements.length;pi++)if(!(new File(placements[pi].path)).exists)throw new Error('Missing render asset');
 if(!input.exists||!out.exists)throw new Error('Missing validated input/output directory');
 for(var k=0;k<app.documents.length;k++){try{if(app.documents[k].fullName.fsName===input.fsName)throw new Error('Input already open; use a distinct copy');}catch(e){if(e.message.indexOf('already open')>=0)throw e;}}
 var prev=app.userInteractionLevel,doc=null;
 try{
  app.userInteractionLevel=UserInteractionLevel.DONTDISPLAYALERTS;doc=app.open(input);
  // Replace semantic placeholders in place, retaining paint order and bounds.
  for(var pi=0;pi<placements.length;pi++){
   var item=placements[pi],anchor=null;
   for(var j=0;j<doc.pathItems.length;j++)if(doc.pathItems[j].name===item.id){anchor=doc.pathItems[j];break;}
   if(!anchor)throw new Error('Missing render placeholder '+item.id);
   var bounds=anchor.geometricBounds,placed=doc.placedItems.add();placed.file=new File(item.path);
   placed.position=[bounds[0],bounds[1]];placed.width=bounds[2]-bounds[0];placed.height=bounds[1]-bounds[3];placed.name=item.id+' own Blender render';
   placed.move(anchor,ElementPlacement.PLACEBEFORE);anchor.remove();placed.embed();
  }
  // Promote SVG top-level groups to editable Illustrator layers.
  var groups=[];for(var i=0;i<doc.groupItems.length;i++){var g=doc.groupItems[i];if(g.parent.typename==='Layer')groups.push(g);}
  for(var i=groups.length-1;i>=0;i--){var l=doc.layers.add();l.name=groups[i].name||('Component '+i);groups[i].move(l,ElementPlacement.PLACEATEND);}
  for(var i=doc.placedItems.length-1;i>=0;i--)doc.placedItems[i].embed();
  var ai=new IllustratorSaveOptions();ai.pdfCompatible=true;ai.embedLinkedFiles=true;doc.saveAs(new File(out.fsName+'/figure.ai'),ai);
  var png=new ExportOptionsPNG24();png.antiAliasing=true;png.artBoardClipping=true;png.transparency=false;png.horizontalScale=100;png.verticalScale=100;doc.exportFile(new File(out.fsName+'/figure'),ExportType.PNG24,png);
  var f=new File(out.fsName+'/illustrator-manifest.json');if(!f.open('w'))throw new Error('Cannot write manifest');f.write('{"version":"'+app.version+'","native_text":'+doc.textFrames.length+',"paths":'+doc.pathItems.length+',"layers":'+doc.layers.length+',"rasters":'+doc.rasterItems.length+',"links":'+doc.placedItems.length+'}');f.close();
  if(!(new File(out.fsName+'/figure.ai')).exists||!(new File(out.fsName+'/figure.png')).exists)throw new Error('Missing export');
 }finally{try{if(doc)doc.close(SaveOptions.DONOTSAVECHANGES);}finally{app.userInteractionLevel=prev;}}
})();
