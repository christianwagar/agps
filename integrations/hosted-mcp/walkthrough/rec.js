// Re-render: npm i -D puppeteer-core; node walkthrough/rec.js anim.html | anim-prompt.html, then ffmpeg (15fps; gif at 10fps/720px/32 colors).
// Slowed render: scenes 1-4 at 1/1.5 speed (4.5s each), last scene 4.5s + 2s hold, then fade. Total 24.5s.
const puppeteer=require("puppeteer-core");const path=require("path");
const file=process.argv[2]||"anim.html",out=path.join(__dirname,"frames-"+file.replace(/\.html$/,""));
const S=1.5,T=24.5;
function map(tau){ if(tau<18) return tau/S; if(tau<24.2) return 12+Math.min((tau-18)/S,2.6); return 12+2.7+(tau-24.2); }
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||"/usr/bin/google-chrome",args:["--no-sandbox"]});
const p=await b.newPage();await p.setViewport({width:960,height:540});
await p.goto("file://"+path.join(__dirname,file),{waitUntil:"networkidle0"});await p.evaluate(()=>document.fonts.ready);
require("fs").mkdirSync(out,{recursive:true});const fps=15;
for(let i=0;i<Math.round(fps*T);i++){await p.evaluate(t=>render(t),Math.min(map(i/fps),14.999));await p.screenshot({path:`${out}/f${String(i).padStart(4,"0")}.png`});}
await b.close();})();
