import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

(() => {
  const button = document.getElementById('mascotButton');
  if (!button || button.dataset.kix3dReady) return;
  button.dataset.kix3dReady = '1';
  const oldImage = button.querySelector('img');
  if (oldImage) { oldImage.style.opacity = '1'; oldImage.style.visibility = 'visible'; }
  let firstFrameRendered = false;
  const canvas = document.createElement('canvas');
  canvas.id = 'kixMascotCanvas';
  canvas.setAttribute('aria-label', 'روبوت KIX ثلاثي الأبعاد');
  button.appendChild(canvas);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
  camera.position.set(0, 0, 13.5);
  camera.lookAt(0, -0.15, 0);
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({canvas, alpha:true, antialias:true});
  } catch (error) {
    console.warn('KIX 3D mascot unavailable; keeping original mascot image.', error);
    canvas.remove();
    button.dataset.kix3dReady = '';
    return;
  }
  // Keep the original mascot underneath as a permanent visual fallback.
  canvas.style.position = 'absolute';
  canvas.style.inset = '0';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.zIndex = '2';
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  scene.add(new THREE.HemisphereLight(0xb9caff, 0x17040b, 2.0));
  const key = new THREE.DirectionalLight(0xffffff, 3.2); key.position.set(4,6,7); scene.add(key);
  const redLight = new THREE.PointLight(0xff1238, 24, 12); redLight.position.set(-2,1,3); scene.add(redLight);
  const goldLight = new THREE.PointLight(0xffb52e, 12, 10); goldLight.position.set(2,3,-2); scene.add(goldLight);

  const black = new THREE.MeshStandardMaterial({color:0x11131c, metalness:.78, roughness:.25});
  const dark = new THREE.MeshStandardMaterial({color:0x242633, metalness:.72, roughness:.3});
  const red = new THREE.MeshStandardMaterial({color:0xff173b, emissive:0xc90025, emissiveIntensity:2.1, metalness:.35, roughness:.22});
  const gold = new THREE.MeshStandardMaterial({color:0xffb52d, metalness:.85, roughness:.2});
  const white = new THREE.MeshStandardMaterial({color:0xe8edf9, metalness:.4, roughness:.25});
  const glow = new THREE.MeshBasicMaterial({color:0xff173b});
  const robot = new THREE.Group(); scene.add(robot);

  function mesh(parent, geo, mat, pos, scale, rot) {
    const m = new THREE.Mesh(geo,mat); m.position.set(...pos);
    if(scale) m.scale.set(...scale); if(rot) m.rotation.set(...rot);
    m.castShadow = true; m.receiveShadow = true; parent.add(m); return m;
  }
  function sphere(parent, mat, pos, scale) { return mesh(parent,new THREE.SphereGeometry(1,32,24),mat,pos,scale); }
  function cylinder(parent, mat, pos, radiusTop, radiusBottom, height, rot) {
    return mesh(parent,new THREE.CylinderGeometry(radiusTop,radiusBottom,height,24),mat,pos,[1,1,1],rot);
  }
  // torso and chest badge
  const torso = new THREE.Group(); torso.position.y=-.85; robot.add(torso);
  sphere(torso,black,[0,0,0],[.92,1.05,.55]);
  mesh(torso,new THREE.BoxGeometry(.58,.42,.08),red,[0,.12,.56],[1,1,1],[0,0,0]);
  mesh(torso,new THREE.BoxGeometry(.25,.35,.04),gold,[0,.12,.62]);
  // neck
  cylinder(robot,dark,[0,.25,0],.28,.32,.35);
  // head / helmet
  const head = new THREE.Group(); head.position.set(0,1.25,0); robot.add(head);
  sphere(head,black,[0,0,0],[1.18,1.08,.82]);
  sphere(head,dark,[0,-.03,.36],[1.08,.94,.58]);
  sphere(head,black,[0,-.05,.72],[.91,.78,.22]);
  // angular glowing eyes
  const eyeGeo = new THREE.BufferGeometry();
  eyeGeo.setAttribute('position',new THREE.Float32BufferAttribute([-.48,.12,.94,-.12,-.02,.94,-.39,-.3,.94,.48,.12,.94,.12,-.02,.94,.39,-.3,.94],3));
  eyeGeo.setIndex([0,1,2,3,4,5]); eyeGeo.computeVertexNormals();
  mesh(head,new THREE.SphereGeometry(.035,12,8),glow,[-.32,-.05,.94],[2.8,1.1,.3]);
  mesh(head,new THREE.SphereGeometry(.035,12,8),glow,[.32,-.05,.94],[2.8,1.1,.3]);
  // bright tapered eye plates
  const eyeMat = new THREE.MeshBasicMaterial({color:0xfff2f4});
  mesh(head,new THREE.ConeGeometry(.19,.42,4),eyeMat,[-.38,-.02,.96],[1,1,.18],[0,0,Math.PI/2]);
  mesh(head,new THREE.ConeGeometry(.19,.42,4),eyeMat,[.38,-.02,.96],[1,1,.18],[0,0,Math.PI/2]);
  // headphone ear cups and red rings
  for (const side of [-1,1]) {
    sphere(head,black,[side*1.05,.02,0],[.34,.62,.68]);
    sphere(head,red,[side*1.19,.02,.04],[.12,.43,.48]);
    sphere(head,dark,[side*1.27,.02,.06],[.09,.31,.34]);
  }
  // crown band and five points
  cylinder(head,gold,[0,1.0,0],.98,.98,.14);
  const crownBase = mesh(head,new THREE.TorusGeometry(.92,.075,12,64),gold,[0,1.06,0]);
  crownBase.rotation.x=Math.PI/2;
  for(let i=0;i<5;i++){
    const x=(i-2)*.39, h=[.42,.62,.78,.62,.42][i];
    mesh(head,gold,new THREE.ConeGeometry(.22,h,4),[x,1.25+h*.42,0],[1,1,1],[0,0,(i-2)*-.13]);
    sphere(head,gold,[x,1.25+h*.84,.02],[.09,.09,.09]);
    mesh(head,red,new THREE.OctahedronGeometry(.105),[x,1.38,.12],[1,1, .35]);
  }
  // Articulated arms: shoulder, elbow, wrist and fingers
  const arms=[];
  for(const side of [-1,1]){
    const shoulder=new THREE.Group(); shoulder.position.set(side*.83,-.42,0); torso.add(shoulder);
    sphere(shoulder,dark,[0,-.18,0],[.31,.32,.31]);
    cylinder(shoulder,black,[0,-.52,0],.22,.25,.62,[0,0,side*-.08]);
    sphere(shoulder,red,[0,-.5,.18],[.24,.12,.08]);
    const elbow=new THREE.Group(); elbow.position.set(0,-.83,0); shoulder.add(elbow);
    sphere(elbow,dark,[0,0,0],[.25,.25,.25]);
    cylinder(elbow,black,[0,-.32,0],.18,.21,.55);
    const wrist=new THREE.Group(); wrist.position.set(0,-.61,.02); elbow.add(wrist);
    sphere(wrist,dark,[0,0,0],[.19,.16,.19]);
    sphere(wrist,black,[0,-.19,.04],[.27,.29,.25]);
    for(let f=0;f<4;f++){
      const finger=new THREE.Group(); finger.position.set((f-1.5)*.115,-.34,.06); wrist.add(finger);
      cylinder(finger,dark,[0,-.09,0],.055,.065,.19);
      sphere(finger,dark,[0,-.18,0],[.065,.07,.065]);
    }
    const thumb=new THREE.Group(); thumb.position.set(side*.22,-.2,.08); wrist.add(thumb);
    cylinder(thumb,dark,[0,-.09,0],.065,.075,.18,[0,0,side*.55]);
    arms.push({shoulder,elbow,wrist,side});
  }
  // legs and chunky KIX sneakers
  for(const side of [-1,1]){
    const leg=new THREE.Group(); leg.position.set(side*.48,-1.65,0); robot.add(leg);
    cylinder(leg,black,[0,-.45,0],.28,.32,.82);
    sphere(leg,dark,[0,-.9,.2],[.4,.28,.62]);
    mesh(leg,new THREE.BoxGeometry(.68,.16,1.0),white,[0,-1.08,.3]);
    mesh(leg,new THREE.BoxGeometry(.52,.12,.72),black,[0,-.96,.32]);
    mesh(leg,new THREE.BoxGeometry(.22,.16,.04),red,[0,-.95,.69]);
  }
  // subtle floating platform
  const ring=mesh(robot,new THREE.TorusGeometry(1.15,.025,8,64),red,[0,-3.0,0]);
  ring.rotation.x=Math.PI/2;
  const floor=mesh(robot,new THREE.CircleGeometry(1.1,48),new THREE.MeshBasicMaterial({color:0x310713,transparent:true,opacity:.22}),[0,-3.02,0]);
  floor.rotation.x=-Math.PI/2;

  let flipStart=0;
  const greeting=document.createElement('div');
  greeting.className='kix-mascot-greeting';
  greeting.textContent='هلا بيك في KIX! 👋';
  button.appendChild(greeting);
  const flipHint=document.createElement('div');
  flipHint.className='kix-mascot-flip-hint';
  flipHint.textContent='اضغط عليّ حتى أسوي شقلبة!';
  button.appendChild(flipHint);
  button.addEventListener('click',()=>{ if(!flipStart){ flipStart=performance.now(); greeting.textContent='يلااا شقلبة! 🤸'; } });
  function resize(){
    const w=Math.max(1,button.clientWidth), h=Math.max(1,button.clientHeight);
    renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(button); resize();
  canvas.addEventListener('webglcontextlost', (event) => {
    event.preventDefault();
    if (oldImage) { oldImage.style.opacity = '1'; oldImage.style.visibility = 'visible'; }
  });
  function animate(now){
    requestAnimationFrame(animate);
    const t=now*.001;
    robot.position.y=.12+Math.sin(t*1.5)*.07;
    robot.rotation.y=Math.sin(t*.55)*.13;
    const wave=Math.sin(t*8.5);
    arms[1].shoulder.rotation.z=-2.05 + wave*.12;
    arms[1].elbow.rotation.z=-.22 + wave*.42;
    arms[1].wrist.rotation.z=wave*.32;
    arms[0].shoulder.rotation.z=.12 + Math.sin(t*1.8)*.035;
    arms[0].elbow.rotation.z=.08;
    if(flipStart){
      const p=Math.min(1,(now-flipStart)/1250);
      robot.rotation.x=p*Math.PI*2;
      robot.rotation.z=Math.sin(p*Math.PI)*.12;
      robot.position.y=.12+Math.sin(p*Math.PI)*1.1;
      if(p>=1){flipStart=0;robot.rotation.set(0,0,0);greeting.textContent='هلا بيك في KIX! 👋';}
    }
    renderer.render(scene,camera);
    if (!firstFrameRendered) {
      firstFrameRendered = true;
      if (oldImage) { oldImage.style.opacity = '0'; oldImage.style.visibility = 'hidden'; }
    }
  }
  requestAnimationFrame(animate);
})();
