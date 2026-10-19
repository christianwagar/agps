// Re-render the walkthrough: npm i -D puppeteer-core, then node walkthrough/rec.js (uses Chrome), then ffmpeg (see README).
const puppeteer=require("puppeteer-core");
(async()=>{const b=await puppeteer.launch({executablePath:"/usr/bin/google-chrome",args:["--no-sandbox"]});
const p=await b.newPage();await p.setViewport({width:960,height:540});
await p.goto("file://"+__dirname+"/anim.html",{waitUntil:"networkidle0"});await p.evaluate(()=>document.fonts.ready);
require("fs").mkdirSync(__dirname+"/frames",{recursive:true});const fps=15,T=15;
for(let i=0;i<fps*T;i++){await p.evaluate(t=>render(t),i/fps);await p.screenshot({path:__dirname+`/frames/f${String(i).padStart(4,"0")}.png`});}
await b.close();})();
