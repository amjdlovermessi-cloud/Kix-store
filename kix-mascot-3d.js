import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

(() => {
  const button = document.getElementById('mascotButton');
  if (!button || button.dataset.kix3dReady) return;
  button.dataset.kix3dReady = '1';
  const oldImage = button.querySelector('img');
  if (oldImage) oldImage.remove();
  const canvas = document.createElement('canvas');
  canvas.id = 'kixMascotCanvas';
  canvas.setAttribute('aria-label', 'روبوت KIX ثلاثي الأبعاد');
  button.appendChild(canvas);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
  camera.position.set(0, 1.05, 10.2);
  const renderer = new THREE.WebGLRenderer({canvas, alpha:true, antialias:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
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
  // arms, pivot at shoulders, right arm waves
  const arms=[];
  for(const side of [-1,1]){
    const arm=new THREE.Group(); arm.position.set(side*.83,-.42,0); torso.add(arm); arms.push(arm);
    sphere(arm,dark,[0,-.28,0],[.29,.38,.3]);
    cylinder(arm,black,[0,-.66,0],.22,.25,.62,[0,0,side*-.12]);
    sphere(arm,red,[0,-.48,.18],[.24,.12,.08]);
    sphere(arm,black,[0,-1.02,.04],[.29,.3,.28]);
    for(let f=0;f<4;f++) sphere(arm,dark,[(f-1.5)*.12,-1.2,.12],[.09,.18,.1]);
    sphere(arm,dark,[0,-1.02,.29],[.1,.2,.09]);
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

  let flipStart=0, waving=true, last=0;
  button.addEventListener('click',()=>{ if(!flipStart) flipStart=performance.now(); });
  function resize(){
    const w=Math.max(1,button.clientWidth), h=Math.max(1,button.clientHeight);
    renderer.setSize(w,h,false); camera.aspect=w/h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(button); resize();
  function animate(now){
    requestAnimationFrame(animate);
    const t=now*.001;
    robot.position.y=.12+Math.sin(t*1.5)*.07;
    robot.rotation.y=Math.sin(t*.55)*.13;
    arms[1].rotation.z=-.15+Math.sin(t*5.2)*.24;
    arms[0].rotation.z=-.2 + Math.sin(t*5.5)*.55;
    if(flipStart){
      const p=Math.min(1,(now-flipStart)/1250);
      robot.rotation.x=p*Math.PI*2;
      robot.rotation.z=Math.sin(p*Math.PI)*.12;
      robot.position.y=.12+Math.sin(p*Math.PI)*1.1;
      if(p>=1){flipStart=0;robot.rotation.set(0,0,0);}
    }
    renderer.render(scene,camera);
  }
  requestAnimationFrame(animate);
})();
