// Re-render a walkthrough: npm i -D puppeteer-core, then
//   node walkthrough/rec.js anim.html          (connector version)
//   node walkthrough/rec.js anim-prompt.html   (copy-paste prompt version)
// Frames land in walkthrough/frames-<name>/; encode with ffmpeg (mp4/webm/gif, see commit notes).
const puppeteer=require("puppeteer-core");const path=require("path");
const file=process.argv[2]||"anim.html";const out=path.join(__dirname,"frames-"+file.replace(/\.html$/,""));
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME||"/usr/bin/google-chrome",args:["--no-sandbox"]});
const p=await b.newPage();await p.setViewport({width:960,height:540});
await p.goto("file://"+path.join(__dirname,file),{waitUntil:"networkidle0"});await p.evaluate(()=>document.fonts.ready);
require("fs").mkdirSync(out,{recursive:true});const fps=15,T=15;
for(let i=0;i<fps*T;i++){await p.evaluate(t=>render(t),i/fps);await p.screenshot({path:`${out}/f${String(i).padStart(4,"0")}.png`});}
await b.close();})();
