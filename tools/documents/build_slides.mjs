import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=process.argv[2];
const skill=process.env.PRESENTATION_TOOLS_ROOT;
if(!skill) throw new Error('Set PRESENTATION_TOOLS_ROOT to the presentation validation utilities directory.');
const python=process.env.PYTHON || 'python';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const tmp=path.join(root,'tmp/slides');const out=path.join(root,'deliverables/slides');await fs.mkdir(tmp,{recursive:true});await fs.mkdir(out,{recursive:true});
const bench=JSON.parse(await fs.readFile(path.join(root,'evidence/benchmarks/summary.json'),'utf8'));
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={bg:'#101722',ink:'#F2EBDD',muted:'#B5BCCC',gold:'#D9B36B',line:'#384657',red:'#E45E4D'};
let index=0;const notes=[];
function text(s,t,x,y,w,h,size=27,color=C.ink,bold=false){
 const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 a.text=t;a.text.style={typeface:'Arial',fontSize:size,bold,color,wrap:'square',autoFit:'none',insets:0};return a;
}
function shape(s,g,x,y,w,h,fill,line=C.line,rotation=0){return s.shapes.add({geometry:g,position:{left:x,top:y,width:w,height:h,rotation},fill,line:{fill:line,width:1.5}});}
async function img(s,name,x,y,w,h,fit='contain'){
 const b=await fs.readFile(path.join(root,'evidence/screenshots',name+'.png'));
 s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:name.replaceAll('-',' '),position:{left:x,top:y,width:w,height:h},fit});
}
function slide(title,note,seconds=50){
 const s=P.slides.add();s.background.fill=C.bg;index++;
 if(title)text(s,title,58,44,1164,84,44,C.ink,true);
 text(s,'LASER VAULT HEIST  /  COMPUTER GRAPHICS',58,676,1050,22,15,C.muted);
 text(s,String(index).padStart(2,'0'),1168,674,55,26,17,C.gold);
 s.speakerNotes.text=`Target speaking time: ${seconds} seconds.\n\n${note}`;
 notes.push({slide:index,seconds,title:title||'Laser Vault Heist',notes:note});return s;
}
function block(s,t,x,y,w=230,h=84){shape(s,'rect',x,y,w,h,'#1B2736');const a=text(s,t,x+10,y+15,w-20,h-24,25,C.ink,true);a.text.style={typeface:'Arial',fontSize:25,bold:true,color:C.ink,alignment:'center',insets:0};}
function arrow(s,x,y,w=65){shape(s,'rightArrow',x,y,w,22,C.gold,C.gold);}
// 1
let s=slide('',`Introduce Laser Vault Heist as topic 12, a single-room first-person game for Computer Graphics Fundamentals. The goal is a complete, inspectable implementation using C++17 and OpenGL 3.3 core. The room and thief were made in Blender, including UVs, rig and actions. Introduce the three students and group, with Nurbek leading visual design and animation, and Makhmet and Nurassyl responsible for gameplay mechanics. Explain that the presentation will connect the visible game to its collision, shading and render pipeline, then show a real-time demo. Source: project README and the supplied topic brief.`,35);
await img(s,'room-world-final',505,134,725,408);
text(s,'LASER\nVAULT HEIST',58,152,430,175,64,C.ink,true);
text(s,'C++17 / OpenGL 3.3 core',60,361,430,40,27,C.gold);
text(s,'Students: Nurbek Yerbulekov, Makhmet Demesh, Nurassyl Nygmet\nGroup: SE-2428',60,420,500,155,24,C.ink);
text(s,'Topic 12',60,582,430,40,25,C.muted);
// 2
s=slide('The heist and its constraints',`Describe the playable loop: observe six moving or rotating lasers, walk through the vault, crouch under the final low beam and interact with the safe. A real contact triggers red illumination and ends the attempt; retry resets position, phases and the mechanism. There are three useful interactions: lamp, CCTV and safe. Scope is deliberately one room with no guard NPC, combat or multiplayer. The controller, collision body and rendered thief must agree about crouching. The final demo uses the same Game rules through deterministic input, so it is repeatable automated evidence rather than a claimed human playtest. Sources: game.cpp, director.cpp, README.`,45);
await img(s,'start-menu',470,170,752,423);
text(s,'6 laser barriers',58,180,370,56,34,C.gold,true);
text(s,'Walk, wait, crouch\nand reach the safe.',58,260,360,105,30);
text(s,'Lamp  /  CCTV  /  safe\nThree meaningful interactions',58,409,380,100,26,C.muted);
text(s,'Failure -> retry -> victory',58,563,390,55,26,C.ink);
// 3 native editable pipeline
s=slide('Architecture and frame pipeline',`Trace input from GLFW into the fixed-step accumulator. Game updates at 240 Hz, retaining short interaction edges until a step consumes them. World applies game state to node transforms and animation. Assets enter through documented native formats exported from Blender, then Scene builds its parent-first hierarchy and static batches. Rendering uses a moon depth pass, a separate CCTV framebuffer, the main HDR target, post-processing and UI. Explain that static matrices and meshes upload once; only dynamic values and bone palettes change each frame. All GL objects are destroyed before the context. The separation makes rule tests independent of the GPU. Sources: main.cpp, fixed_step.hpp, scene.cpp, renderer.cpp, graphics.cpp.`,65);
block(s,'GLFW input',58,165);arrow(s,302,196);block(s,'Game at 240 Hz',382,165);arrow(s,626,196);block(s,'World + Animator',706,165,300);
block(s,'Blender exports',58,320);arrow(s,302,351);block(s,'Scene + instances',382,320);arrow(s,626,351);block(s,'Own renderer',706,320,300);
text(s,'Retained input edges; pause stops simulation',58,440,1100,40,25,C.muted);
const xs=[58,366,674,982],labels=['Moon depth','CCTV FBO','Main HDR','Post + UI'];
xs.forEach((x,i)=>{block(s,labels[i],x,520,240,70);if(i<3)arrow(s,x+250,545,46);});
// 4 native algorithm diagram
s=slide('Collision in the laser’s local space',`Explain the equation q=inverse(M)*p: moving a world-space player sample into beam-local coordinates makes the oriented-box test three scalar comparisons. The long thin rectangle and its dashed enclosing world box illustrate a false positive that a world AABB would create. Rendering and contact share M. The implementation samples the upright body every 0.08 metres with a conservative local margin, plus the exact head point. The final beam is at 1.42 metres; standing body height is 1.90 and crouching is 1.29. A 240 Hz step reduces ordinary tunneling, but is not exact continuous collision for arbitrary speed. Show the short code and explain every term. Scientific comparison: Klosowski et al., DOI 10.1109/2945.675649; Jimenez et al., DOI 10.1016/S0097-8493(00)00130-8. Implementation: game.cpp.`,75);
text(s,'q = inverse(M) * vec4(p, 1)',58,150,1120,54,38,C.gold,true);
shape(s,'rect',75,270,350,150,'none',C.muted);shape(s,'rect',78,328,344,28,C.red,C.red,-21);shape(s,'ellipse',100,281,14,14,C.gold,C.gold);
text(s,'World AABB can be too large',58,445,470,42,25,C.muted);arrow(s,483,336,100);
shape(s,'rect',660,325,500,35,C.red,C.red);text(s,'Beam-local box',682,265,470,45,27,C.ink);
text(s,'abs(q.x) <= half.x\nabs(q.y) <= half.y\nabs(q.z) <= half.z',682,390,480,142,30);
text(s,'Same model matrix for the visible beam and contact test',58,593,1150,40,26,C.muted);
//5
s=slide('Per-fragment lighting',`Describe the Blinn-Phong fragment shader using the surface normal, light vector and half-vector. Diffuse is clamped N dot L; the specular lobe is a shininess power of N dot H. Local light power is attenuated by distance; spotlights use smooth cone edges. Their directions follow the same rotating mounts seen in the screenshot. Six local lights, two spots and a directional moon are recolored on alarm. Only the moon has a 2048-square PCF shadow map. Visible dust cones are additive meshes, not a claim of physical volumetric transport. Explain linear lighting followed by the credited filmic fit and gamma. Sources: surface.frag, post.frag; Phong DOI 10.1145/360825.360839; Cook-Torrance DOI 10.1145/357290.357293; Narkowicz, https://knarkowicz.wordpress.com/2016/01/06/aces-filmic-tone-mapping-curve/ (CC0).`,60);
await img(s,'spotlights',58,172,748,421);
text(s,'H = normalize(L + V)',838,181,390,84,30,C.gold,true);
text(s,'Diffuse: max(N·L, 0)\nSpecular: max(N·H, 0)^s',838,290,380,114,26);
text(s,'Attenuation + soft cones\nInverse-transpose normals\nOne PCF shadow map',838,448,380,145,25,C.muted);
//6
s=slide('Original character and animation',`The thief is original Blender geometry rather than an imported animation package. Show the neutral face view and crouch pose, then state the measured 21,782 triangles and 20 bones. Five clips cover idle, walk, crouched idle, crouched walk and interaction. Local TRS interpolates with quaternion slerp for rotations; skinning blends global bone matrices times inverse binds. Clips are in-place and stride phase follows travelled distance. Pose checks verify normalized weights and a 1.2755 metre crouched mesh maximum against a 1.29 metre body. The corrected arm pose compensates for torso lean. Linear blend skinning remains a simple approximation; dual quaternions could better preserve joint volume. Source: character_rig.py, animation.cpp, surface.vert; Kavan et al., DOI 10.1145/1409625.1409627.`,55);
await img(s,'character-crouch-final',58,166,435,435);await img(s,'character-face-final',518,166,435,435);
text(s,'20 bones',982,190,240,55,34,C.gold,true);text(s,'21,782\ntriangles',982,285,240,95,29);
text(s,'5 clips\n0.2 s blends\nLerp + slerp',982,438,240,125,27,C.muted);
text(s,'p′ = Σ wᵢ Gᵢ(t) Bᵢ⁻¹ p',58,617,1100,40,28,C.ink);
//7
s=slide('Live CCTV with render-to-texture',`Point out that the monitor contains a second live scene camera, not a recorded image. Its framebuffer has color and depth attachments and is checked for completeness. The full animated thief is included in that pass but hidden from the first-person camera to avoid clipping. The monitor screen is excluded from its own render, preventing undefined read/write feedback. E switches between two camera locations. The physical screen samples linear color inside the main pipeline. The enlarged presentation view uses a separately display-converted texture, because feeding linear color directly to ImGui made it dark during development. Sources: renderer.cpp, world.cpp, surface.frag, ui.cpp and the real screenshot at 00:37.`,50);
await img(s,'cctv',410,165,812,457);
text(s,'640 × 360 FBO',58,177,320,70,34,C.gold,true);
text(s,'Color + depth\nTwo live cameras\nAnimated thief',58,292,320,142,29);
text(s,'Exclude the screen\nfrom its own pass.',58,496,320,104,26,C.muted);
//8
s=slide('Measured local performance',`Read the chart as uncapped whole-frame performance, not monitor refresh rate or isolated GPU timing. Three visible 1280 by 720 runs lasted 65 seconds with the first five discarded. The route kept CCTV, lasers, spotlights and animation active, with capture disabled. Average FPS is reciprocal mean frame time. The 1% low is reciprocal mean of the slowest one percent; values are 753.0, 470.4 and 686.3. Hardware is i5-13400F, RTX 5060 and 32 GiB. Background desktop work was possible. These local results exceed 60 FPS but cannot certify the unknown TA machine. Mention that all three CTest suites and a clean build passed. Source: evidence/benchmarks/summary.json and run-1.csv through run-3.csv.`,55);
const chart=s.charts.add('bar',{position:{left:58,top:168,width:790,height:430},categories:['Run 1','Run 2','Run 3'],series:[{name:'Average FPS',values:bench.runs.map(x=>+x.average_fps.toFixed(1)),fill:C.gold},{name:'1% low FPS',values:bench.runs.map(x=>+x.one_percent_low_fps.toFixed(1)),fill:'#769AB1'}],barOptions:{direction:'column',grouping:'clustered',gapWidth:85},hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{typeface:'Arial',fontSize:20,fill:C.ink}},xAxis:{textStyle:{typeface:'Arial',fontSize:22,fill:C.ink},line:{fill:C.line,width:1}},yAxis:{min:0,max:1500,majorUnit:500,textStyle:{typeface:'Arial',fontSize:19,fill:C.muted},majorGridlines:{fill:C.line,width:1}},dataLabels:{showValue:true,numberFormatCode:'0',position:'outEnd',textStyle:{typeface:'Arial',fontSize:20,fill:C.ink}},chartFill:C.bg,plotAreaFill:C.bg});
applyPresentationChartFont(chart,{fontFamily:'Arial'});
text(s,'1280 × 720',899,175,320,50,34,C.gold,true);text(s,'i5-13400F\nRTX 5060\n32 GiB RAM',899,264,320,144,28);
text(s,'3 × 60 s measured\n5 s warm-up\nVSync off',899,445,320,140,26,C.muted);
text(s,'TA hardware remains untested. Raw frame times are included.',58,620,1150,38,25,C.muted);
//9
s=slide('Failure, reset and safe-opening victory',`Use these actual captured frames to explain the state machine. A beam contact changes all scene illumination to red and offers retry. Retry reconstructs the initial state rather than only changing a menu label. In the successful final attempt, the player crosses the last beam while crouched, backs away using normal collision-tested movement and opens the safe within interaction range. The wheel turns, bolts retract and the door rotates around its hinge; victory follows the sequence. The demo shows this without a cut in the final attempt. These frames are evidence from the same application and rules. Sources: game.cpp, world.cpp, director.cpp, demo-gameplay-trace.csv.`,40);
await img(s,'alarm',58,180,556,313);await img(s,'victory',666,180,556,313);
text(s,'Alarm -> R -> fresh attempt',58,520,556,65,29,C.red,true);
text(s,'Wheel -> bolts -> hinged door',666,520,556,65,29,C.gold,true);
text(s,'The final low-beam passage and opening are continuous in the demo.',58,609,1164,45,25,C.muted);
//10
s=slide('Results, limits and next checks',`Conclude with concrete deliverables: the standalone game, editable Blender sources, five clips, custom shaders and runtime formats, tests, raw measurements, the report's eighteen verified references and the real-time demo. The engineering lesson is consistency between render transforms, collision, pose and color space. State limits without claiming a grade: sampled collision, LBS, one shadow map and Windows-only recording. Native human input testing, TA hardware, exact starter compatibility and oral understanding require external checks. Future technical work would be swept collision and stronger deformation if the scope expands. Next play the 3:30 captioned demo, then open the source for questions. Source: README, report and docs/defense-guide.md.`,40);
await img(s,'diagnostics',592,170,630,355);
text(s,'Complete local implementation',58,174,500,90,34,C.gold,true);
text(s,'Original assets and five clips\nThree passing test suites\n18 verified research references\n3:30 real-time demo',58,295,500,190,27);
text(s,'Next checks',58,539,500,44,29,C.ink,true);
text(s,'Human input • TA machine • live defense',58,591,1155,40,26,C.muted);
await fs.writeFile(path.join(tmp,'speaker-notes.json'),JSON.stringify(notes,null,2));
await fs.writeFile(path.join(root,'docs/presentation-notes.md'),'# Presentation notes\n\n'+notes.map(n=>`## ${n.slide}. ${n.title}\n\nTarget: ${n.seconds} seconds.\n\n${n.notes}`).join('\n\n'));
for(let i=0;i<P.slides.items.length;i++){
 const blob=await P.export({slide:P.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(tmp,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
const candidate=path.join(tmp,'candidate.pptx');await(await PresentationFile.exportPptx(P)).save(candidate);
const final=path.join(out,'Laser_Vault_Heist_Presentation.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:python,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],explicitTotalSlideCount:10,requiredNativeChartOwnerSlides:[8],materializeLiteralChartWorkbooks:true,requiredNativeTableOwnerSlides:[],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(tmp,'presentation-validation.json')});
execFileSync(process.env.SOFFICE_PATH || path.join(root,'.tools/libreoffice/program/soffice.exe'),['--headless','--convert-to','pdf','--outdir',out,final]);
console.log('Created 10 slides; speaking target',notes.reduce((a,n)=>a+n.seconds,0),'seconds');console.log(JSON.stringify(result));
