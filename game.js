(() => {
  "use strict";
  const canvas = document.getElementById("game");
  const ctx = canvas.getContext("2d", { alpha: false });
  const W = canvas.width, H = canvas.height, TILE = 16, LEVEL_W = 1900;
  const $ = (id) => document.getElementById(id);
  const keys = new Set();
  let state = "menu", camera = 0, last = 0, time = 0, shake = 0;
  let player, platforms, enemies, gems, shots, particles, score, levelSeed = 11;
  const C = { sky:"#10152e", deep:"#171e40", blue:"#324c87", cyan:"#72f6ff", white:"#f2f7ff", gold:"#ffe27a", red:"#ff647d", violet:"#a77aff", green:"#75f4b4" };
  const clamp = (v,a,b) => Math.max(a,Math.min(b,v));
  const rect = (x,y,w,h,c) => { ctx.fillStyle=c; ctx.fillRect(Math.round(x),Math.round(y),Math.round(w),Math.round(h)); };
  const pixel = (x,y,c,s=1) => rect(x,y,s,s,c);
  function label(text,x,y,size=8,color=C.white,align="left") {
    ctx.save(); ctx.font = size+"px monospace"; ctx.textAlign=align; ctx.textBaseline="top";
    ctx.fillStyle="#080c1d"; ctx.fillText(text,x+1,y+2); ctx.fillStyle=color; ctx.fillText(text,x,y); ctx.restore();
  }
  function panel(x,y,w,h) { rect(x,y,w,h,"#080d20"); rect(x+1,y+1,w-2,h-2,"#18213f"); rect(x+2,y+2,w-4,1,"#536b9e"); }
  function reset() {
    player={x:36,y:180,w:12,h:20,vx:0,vy:0,face:1,hp:5,inv:0,cool:0,onGround:false};
    platforms=[
      [0,226,320,44],[354,211,150,59],[540,190,160,80],[736,218,174,52],[946,194,155,76],[1138,218,150,52],[1320,185,170,85],[1528,211,160,59],[1712,222,188,48],
      [150,174,64,8],[393,153,58,8],[575,136,56,8],[777,163,56,8],[982,143,60,8],[1170,161,56,8],[1370,132,58,8],[1570,164,56,8]
    ];
    enemies=[
      enemy(210,210,120,300),enemy(386,195,365,470),enemy(579,174,550,675),
      enemy(788,202,750,880),enemy(984,178,960,1070),enemy(1180,202,1150,1260),
      enemy(1385,169,1340,1470),enemy(1570,195,1540,1660),enemy(1745,206,1730,1850)
    ];
    gems=[[180,151],[420,130],[600,113],[802,140],[1010,120],[1198,138],[1400,109],[1598,141],[1765,180]];
    shots=[]; particles=[]; score=0; camera=0; shake=0; state="playing";
  }
  function enemy(x,y,left,right){return {x,y,left,right,v:Math.random()>.5?.45:-.45,hp:2,alive:true,flash:0};}
  function burst(x,y,color,n=8) {
    for(let i=0;i<n;i++){const a=Math.random()*Math.PI*2,s=.3+Math.random()*1.5;particles.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s-.4,life:16+Math.random()*16,max:32,color,size:Math.random()>.5?2:1});}
  }
  function shoot() {
    if(player.cool>0 || state!=="playing") return;
    shots.push({x:player.x+(player.face>0?player.w:0),y:player.y+10,vx:player.face*3.3,life:65});
    player.cool=15; burst(player.x+(player.face>0?player.w:0),player.y+10,C.cyan,4);
  }
  function overlap(a,b){return a.x < b.x+b.w && a.x+a.w>b.x && a.y<b.y+b.h && a.y+a.h>b.y;}
  function update(dt) {
    const step=Math.min(dt/16.667,2); time+=dt;
    if(state!=="playing") { updateParticles(step); return; }
    const left=keys.has("ArrowLeft")||keys.has("a")||keys.has("A");
    const right=keys.has("ArrowRight")||keys.has("d")||keys.has("D");
    player.vx=(right?1:0)-(left?1:0); player.vx*=1.8*step;
    if(player.vx)player.face=Math.sign(player.vx);
    if((keys.has(" ")||keys.has("ArrowUp")||keys.has("w")||keys.has("W"))&&player.onGround){player.vy=-6.1;player.onGround=false;burst(player.x+6,player.y+20,"#7f9bd8",5);}
    player.x=clamp(player.x+player.vx,0,LEVEL_W-player.w);
    player.x=Math.round(player.x);
    player.y+=player.vy*step; player.vy=Math.min(7,player.vy+.29*step); player.onGround=false;
    for(const p of platforms){const r={x:p[0],y:p[1],w:p[2],h:p[3]};if(overlap(player,r)&&player.vy>=0&&player.y+player.h-player.vy*step<=r.y+5){player.y=r.y-player.h;player.vy=0;player.onGround=true;}}
    if(player.y>H+30){player.hp=0;}
    player.cool=Math.max(0,player.cool-step);player.inv=Math.max(0,player.inv-step);
    for(const e of enemies){if(!e.alive)continue;e.x+=e.v*step;if(e.x<e.left||e.x>e.right)e.v*=-1;e.flash=Math.max(0,e.flash-step);
      if(overlap(player,{x:e.x,y:e.y,w:13,h:12})&&player.inv<=0){player.hp--;player.inv=70;player.vy=-3.6;player.vx=player.x<e.x?-2:2;shake=5;burst(player.x+6,player.y+10,C.red,9);}}
    for(const s of shots){s.x+=s.vx*step;s.life-=step;for(const e of enemies){if(e.alive&&overlap({x:s.x-3,y:s.y-3,w:6,h:6},{x:e.x,y:e.y,w:13,h:12})){e.hp--;e.flash=7;s.life=0;burst(s.x,s.y,C.cyan,7);if(e.hp<=0){e.alive=false;burst(e.x+6,e.y+6,C.violet,12);}break;}}}
    shots=shots.filter(s=>s.life>0&&s.x>0&&s.x<LEVEL_W);
    for(const g of gems.slice()){const r={x:g[0]-5,y:g[1]-6,w:10,h:12};if(overlap(player,r)){gems.splice(gems.indexOf(g),1);score++;burst(g[0],g[1],C.gold,12);}}
    updateParticles(step);
    camera=clamp(player.x-W*.38,0,LEVEL_W-W);
    if(player.hp<=0)state="gameover";
    if(player.x>LEVEL_W-58&&score>=5)state="victory";
    if(shake>0)shake=Math.max(0,shake-step);
  }
  function updateParticles(step){for(const p of particles){p.x+=p.vx*step;p.y+=p.vy*step;p.vy+=.035*step;p.life-=step;}particles=particles.filter(p=>p.life>0);}
  function background() {
    rect(0,0,W,H,"#10152e");
    // Stars, fixed to the sky for a parallax feel
    for(let i=0;i<64;i++){const x=((i*83-camera*.13)%W+W)%W,y=(i*47+13)%145;pixel(x,y,i%5===0?"#b9c9ff":"#657bb5",i%7===0?2:1);}
    // Moon
    rect(365,28,30,30,"#293c72");rect(370,23,24,34,"#718dc8");rect(373,26,20,27,"#c1d9ff");rect(378,27,4,3,"#edf5ff");
    // Distant blocky mountains
    for(let i=0;i<9;i++){let x=((i*76-camera*.2)%560+560)%560-40;const y=178+(i%3)*13;rect(x,y-44,18,44,"#202d5b");rect(x+7,y-58,18,58,"#202d5b");rect(x+18,y-35,18,35,"#202d5b");rect(x+7,y-58,6,6,"#35487c");}
    // Foreground haze
    rect(0,204,W,66,"#141d3b");
    for(let i=0;i<12;i++){const x=((i*59-camera*.35)%600+600)%600-50;rect(x,195+(i%4)*7,32,3,"#202c51");}
  }
  function drawPlatform(p){
    const x=Math.round(p[0]-camera),y=p[1],w=p[2],h=p[3];if(x+w<0||x>W)return;
    rect(x,y+3,w,h,"#080d1c");rect(x,y,w,h,"#303e6a");rect(x+1,y+5,w-2,Math.max(0,h-6),"#202d51");
    rect(x,y,w,3,"#69dbe8");rect(x+2,y+3,w-4,1,"#a4ffff");
    for(let k=x+7;k<x+w-4;k+=16){rect(k,y+10,2,Math.max(2,h-15),"#29385f");rect(k+3,y+12,2,Math.max(2,h-17),"#182440");}
    for(let k=x+8;k<x+w-4;k+=42){rect(k,y+5,3,1,"#a5ffff");}
  }
  function drawHero() {
    const x=Math.round(player.x-camera),y=Math.round(player.y);
    if(player.inv>0&&Math.floor(time/75)%2===0)return;
    // shadow
    rect(x-2,y+19,16,3,"#090d20");
    // boots
    rect(x+2,y+17,4,3,"#26314f");rect(x+8,y+17,4,3,"#26314f");rect(x+2,y+19,4,1,"#79dff0");
    // cloak and armor
    rect(x+2,y+8,9,9,"#315db1");rect(x+1,y+10,11,5,"#427be1");rect(x+3,y+8,7,2,"#79aaff");
    rect(x+4,y+10,5,4,"#1b3975");rect(x+5,y+10,3,3,C.cyan);pixel(x+6,y+11,"#ffffff");
    // head and hair
    rect(x+3,y+2,7,6,"#e9b58c");rect(x+2,y+1,9,3,"#dceaff");rect(x+3,y,6,2,"#f7fbff");rect(x+2,y+3,2,3,"#9dbcf3");
    pixel(x+(player.face>0?8:4),y+4,"#17203b");
    // arms
    rect(x,y+9,3,5,"#e9b58c");rect(x+10,y+9,3,5,"#e9b58c");rect(x+(player.face>0?11:0),y+9,2,3,C.cyan);
  }
  function drawEnemy(e){
    if(!e.alive)return;const x=Math.round(e.x-camera),y=Math.round(e.y);if(x<-20||x>W+20)return;
    const c=e.flash>0?"#e7ffff":"#8e65d7";
    rect(x+2,y+9,9,3,"#0a0e23");rect(x,y+5,3,5,c);rect(x+2,y+2,8,9,c);rect(x+4,y,5,3,"#bd8cff");rect(x+3,y+7,2,2,"#ff668f");rect(x+8,y+7,2,2,"#ff668f");rect(x+2,y+10,2,3,"#6343a3");rect(x+9,y+10,2,3,"#6343a3");
    rect(x+1,y+13,3,1,"#cfb6ff");rect(x+8,y+13,3,1,"#cfb6ff");
  }
  function drawGem(g){
    const bob=Math.round(Math.sin(time/180+g[0]) * 2),x=Math.round(g[0]-camera),y=g[1]+bob;
    rect(x-1,y-7,3,2,"#fff1ac");rect(x-4,y-5,8,3,"#f7b946");rect(x-5,y-2,10,4,C.gold);rect(x-3,y+2,6,3,"#f7b946");rect(x-1,y+5,3,2,"#bd7d35");rect(x-2,y-4,2,4,"#fffbd2");
    pixel(x-7,y,"#8d713f");pixel(x+6,y-2,"#fff1ac");
  }
  function drawPortal(){
    const x=Math.round(LEVEL_W-49-camera),y=177,phase=Math.floor(time/140)%2;
    rect(x-7,y-4,24,51,"#182d61");rect(x-4,y-2,18,47,"#3c5eae");rect(x-2,y,14,43,phase?"#83f7ff":"#4dd7ff");rect(x+1,y+3,8,37,"#243a83");
    rect(x+2,y+5,2,7,"#c7ffff");rect(x+7,y+23,2,10,"#8cfcff");
    for(let i=0;i<5;i++){const sx=x+Math.round(Math.sin(time/170+i*2)*10);const sy=y+20+Math.round(Math.cos(time/190+i)*20);pixel(sx,sy,C.cyan,2);}
    rect(x-5,y-7,2,3,C.violet);rect(x+13,y+41,2,3,C.violet);
  }
  function drawShot(s){const x=Math.round(s.x-camera),y=Math.round(s.y);rect(x-5,y-2,10,5,"#386aff");rect(x-3,y-1,6,3,C.cyan);pixel(x-1,y-1,"#fff");pixel(x-7,y,"#9cefff");}
  function drawParticles(){for(const p of particles){rect(p.x-camera,p.y,p.size,p.size,p.color);}}
  function drawHud(){
    panel(8,8,140,31);label("HP",15,14,7,"#a9bce8");
    for(let i=0;i<5;i++){const x=35+i*19;rect(x+2,16,3,2,i<player.hp?C.red:"#3b4565");rect(x,18,7,4,i<player.hp?"#ff718b":"#3b4565");rect(x+2,22,3,2,i<player.hp?"#ff718b":"#3b4565");}
    panel(342,8,130,31);label("CRYSTALS",350,13,7,"#a9bce8");label(String(score).padStart(2,"0")+" / 05",405,23,10,C.gold);
    rect(8,44,464,2,"#2b3a64");rect(8,44,Math.min(464,(player.x/LEVEL_W)*464),2,C.cyan);
  }
  function overlay(title,subtitle,action,color=C.cyan){
    rect(0,0,W,H,"#080c20");rect(22,22,W-44,H-44,"#121b37");rect(24,24,W-48,H-48,"#10172f");
    rect(48,54,W-96,2,"#354978");rect(48,214,W-96,2,"#354978");
    label("✦  ENVEL / RIFT PROTOCOL  ✦",W/2,38,7,"#839bd1","center");
    label(title,W/2,88,18,color,"center");label(subtitle,W/2,124,8,C.white,"center");
    label(action,W/2,176,8,C.green,"center");label("A/D OR ARROWS  ·  SPACE JUMP  ·  J MAGIC",W/2,230,6,"#8395c4","center");
    for(let i=0;i<7;i++){pixel(57+i*55,201+(i%2)*3,i%2?C.violet:C.cyan,2);}
  }
  function render(){
    background();
    for(const p of platforms)drawPlatform(p);
    drawPortal();for(const g of gems)drawGem(g);for(const e of enemies)drawEnemy(e);for(const s of shots)drawShot(s);
    drawHero();drawParticles();
    if(state==="playing"||state==="pause"||state==="victory"||state==="gameover")drawHud();
    if(state==="menu")overlay("ГЕРОИ ЭНВЕЛЛА","РАЗЛОМ МЕЖДУ МИРАМИ","[ ENTER ]  НАЧАТЬ ПРИКЛЮЧЕНИЕ",C.cyan);
    if(state==="pause")overlay("ПАУЗА","Мир замер. Магия ждёт.","[ ENTER ]  ПРОДОЛЖИТЬ",C.gold);
    if(state==="gameover")overlay("ТЫ ПОТЕРЯЛ СИЛЫ","Тени оказались сильнее на этот раз.","[ ENTER ]  ПОПРОБОВАТЬ СНОВА",C.red);
    if(state==="victory")overlay("ПОРТАЛ ОТКРЫТ!","Кристаллов собрано: "+score+" / 9","[ ENTER ]  ИГРАТЬ ЕЩЁ",C.gold);
    $("top-status").textContent=state==="playing"?"СИГНАЛ ПОРТАЛА: АКТИВЕН":state==="victory"?"МИССИЯ ВЫПОЛНЕНА":state==="gameover"?"СВЯЗЬ ПОТЕРЯНА":"ОЖИДАНИЕ КОМАНДЫ";
    $("hint").textContent=state==="playing"?"Кристаллы: "+score+" · Портал ждёт в конце уровня":"ENTER — начать · ESC — пауза";
  }
  function frame(now){const dt=Math.min(40,now-(last||now));last=now;update(dt);render();requestAnimationFrame(frame);}
  window.addEventListener("keydown",e=>{
    if(["ArrowLeft","ArrowRight","ArrowUp"," ","Escape"].includes(e.key))e.preventDefault();
    keys.add(e.key);
    if(e.repeat)return;
    if(e.key==="j"||e.key==="J")shoot();
    if(e.key==="Escape"){if(state==="playing")state="pause";else if(state==="pause")state="playing";else if(state==="menu")return;}
    if(e.key==="Enter"||e.key===" "){
      if(state==="menu"||state==="gameover"||state==="victory")reset();
      else if(state==="pause")state="playing";
    }
  });
  window.addEventListener("keyup",e=>keys.delete(e.key));
  window.addEventListener("blur",()=>keys.clear());
  // Small touch controls make the canvas playable on phones and tablets.
  let touchButtons=[];
  function addTouchControls(){
    if(document.querySelector(".touch-controls"))return;
    const wrap=document.createElement("div");wrap.className="touch-controls";
    [["◀","left"],["▶","right"],["▲","jump"],["✦","magic"]].forEach(([txt,act])=>{
      const b=document.createElement("button");b.type="button";b.textContent=txt;b.setAttribute("aria-label",act);
      b.addEventListener("pointerdown",e=>{e.preventDefault();b.setPointerCapture(e.pointerId);if(act==="magic")shoot();else if(act==="jump"){keys.add(" ");setTimeout(()=>keys.delete(" "),180);}else keys.add(act==="left"?"ArrowLeft":"ArrowRight");});
      const release=()=>{keys.delete("ArrowLeft");keys.delete("ArrowRight");b.classList.remove("pressed");};
      b.addEventListener("pointerup",release);b.addEventListener("pointercancel",release);b.addEventListener("pointerleave",release);
      wrap.appendChild(b);touchButtons.push(b);
    });
    document.querySelector(".game-shell").appendChild(wrap);
  }
  addTouchControls();requestAnimationFrame(frame);
})();