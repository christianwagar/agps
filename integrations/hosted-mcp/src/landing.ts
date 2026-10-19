// Landing page at GET / — styled to match 26-w.com (and docs/index.html in the repo).
const esc = (s: string) => s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));

export function landingPage(mcpUrl: string): string {
  const u = esc(mcpUrl);
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>A-GPS | Account Growth Propensity Scoring · MCP</title>
<meta name="description" content="Add one URL to Claude, ChatGPT or Cursor and score your customer accounts with A-GPS.">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--bg:#fff;--bg-soft:#f7f7f7;--text:#000;--muted:#666;--border:#e5e5e5;--d:"Barlow Condensed","Arial Narrow",sans-serif;--b:"IBM Plex Sans",system-ui,sans-serif}
body{margin:0;font-family:var(--b);color:var(--text);background:var(--bg);line-height:1.65;-webkit-font-smoothing:antialiased}
.c{width:min(100% - 2.5rem,1100px);margin-inline:auto}a{color:var(--text);text-decoration:none}a:hover{opacity:.55}
header{display:flex;justify-content:space-between;padding:1.5rem 0;border-bottom:1px solid #000;font-family:var(--d);font-weight:600;letter-spacing:.16em;text-transform:uppercase;font-size:.85rem}
.label{font-family:var(--d);font-weight:600;letter-spacing:.16em;text-transform:uppercase;font-size:.8125rem}
h1,h2{font-family:var(--d);font-weight:700;text-transform:uppercase;letter-spacing:.04em;line-height:1.05;margin:0 0 1rem}
h1{font-size:clamp(3rem,9vw,6.5rem)}@media(max-width:600px){section{padding:2.5rem 0}.cta{display:inline-block;margin-bottom:.5rem}}h2{font-size:clamp(1.75rem,4vw,2.5rem)}
.sub{font-family:var(--d);font-weight:600;letter-spacing:.2em;text-transform:uppercase;font-size:1.1rem;margin:-.5rem 0 1rem}
.intro{color:var(--muted);max-width:56ch}section{padding:3.5rem 0;border-top:1px solid var(--border)}
.cta,button{font-family:var(--d);font-weight:600;letter-spacing:.14em;text-transform:uppercase;margin-right:1.5rem;font-size:1rem}
.cta:before,button:before{content:"[ "}.cta:after,button:after{content:" ]"}
.url{display:flex;flex-wrap:wrap;gap:.75rem 1rem;align-items:center;justify-content:space-between;background:var(--bg-soft);border:1px solid var(--border);padding:1rem 1.1rem;margin:.75rem 0 0}
.url code{font-size:1rem;word-break:break-all}.url button{margin:0}
button{background:none;border:0;padding:0;cursor:pointer;color:var(--text)}button:hover{opacity:.55}
.g{display:grid;gap:2rem;grid-template-columns:repeat(3,1fr)}@media(max-width:800px){.g{grid-template-columns:1fr}}
.card{border-top:1px solid #000;padding-top:1rem}.card p{color:var(--muted);margin:.5rem 0 0}
.n{font-family:var(--d);font-weight:700;font-size:2.5rem;line-height:1}
.hero{border:0;padding-bottom:2rem}.lead{font-size:1.25rem;max-width:48ch;margin:.75rem 0 0}
.pg{display:grid;gap:1.5rem 2rem;grid-template-columns:repeat(2,1fr)}@media(max-width:700px){.pg{grid-template-columns:1fr}}
.p{display:flex;gap:1rem;align-items:flex-start;border-top:1px solid var(--border);padding-top:1rem}.p p{color:var(--muted);margin:.25rem 0 0}
.chip{flex:none;font-family:var(--d);font-weight:700;letter-spacing:.1em;width:3rem;height:3rem;display:grid;place-items:center;box-sizing:border-box}
.links{margin-top:2rem}
ul{color:var(--muted);padding-left:1.1rem}
.two{color:var(--muted);max-width:70ch;margin-top:2.5rem}.two b{color:var(--text)}.demo{width:100%;max-width:960px;display:block;border:1px solid var(--border);margin:0 0 2.5rem}
.card .label{position:relative;display:inline-block;padding-bottom:.3rem}
.card .label{padding-bottom:.55rem}
.ink{position:absolute;left:-2%;bottom:-.1rem;width:104%;height:.6rem;overflow:visible;fill:#1a1a1a;filter:url(#rough);clip-path:inset(0 100% 0 0);transition:clip-path .5s cubic-bezier(.6,.05,.3,1),opacity .5s ease;opacity:.0}
.card.on .ink{clip-path:inset(0 0 0 0);opacity:.92;transition:clip-path .5s cubic-bezier(.6,.05,.3,1),opacity .15s ease}
.card[data-step="2"] .ink{transform:rotate(-.6deg)}.card[data-step="3"] .ink{transform:rotate(.5deg);width:112%}
.sync .card p{color:#999;transition:color .4s ease}.sync .card.on p{color:#000}
.demo{margin-bottom:.75rem!important}.prog{display:flex;gap:.6rem;align-items:center;margin:0 0 2rem;color:var(--muted)}
.prog button{margin:0;color:var(--muted);font-size:.95rem;transition:color .3s ease}.prog button:before,.prog button:after{content:""}
.prog button.on{color:var(--text);text-decoration:underline;text-underline-offset:.3em}

@media(prefers-reduced-motion:reduce){.card *,.ink,.prog button{transition:none!important}}
footer{padding:2rem 0;border-top:1px solid var(--border);color:var(--muted);font-size:.85rem}
</style></head><body><svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="rough" x="-5%" y="-50%" width="110%" height="200%"><feTurbulence type="fractalNoise" baseFrequency="0.6 0.25" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="1.1"/></filter></svg><div class="c">
<header><a href="https://26-w.com">26-W / Notes</a><span>Christian Wagar</span></header>
<section class="hero"><span class="label">MCP server · free · no sign-up</span><h1>A-GPS</h1>
<p class="sub">Account Growth Propensity Scoring</p>
<p class="intro">Score your book of customer accounts right inside your AI. Golf rules: lower is better. Every account lands in P1 to P4 with the why and a focus-this-week list.</p></section>
<section><span class="label">Read this first</span><h2>A framework, not a formula</h2>
<p class="intro">The weights and bands were tuned for one book of business. Yours is different. Just tell your AI in plain English, like "use 25% GTM and 15% marketing" or "ARR band 1 is $200K+", and it passes the tweak along.</p>
<ul><li>Nothing you send is stored or logged. Each request is scored and forgotten.</li><li>No account or sign-up needed.</li></ul><p class="links"><a class="cta" href="https://26-w.com/notes/account-growth-propensity/">Read the writeup</a><a class="cta" href="https://github.com/christianwagar/agps">View on GitHub</a></p></section>
<section><span class="label">Three steps</span><h2>Two minutes, no code</h2>
<video id="v" class="demo" autoplay muted loop playsinline preload="auto" poster="/agps-walkthrough-poster.png" aria-label="Walkthrough: copy the link, add it to your AI app, ask it to score your accounts, get P1 to P4 and a focus-this-week list">
<source src="/agps-walkthrough.webm" type="video/webm"><source src="/agps-walkthrough.mp4" type="video/mp4">
<img src="/agps-walkthrough.gif" alt="A-GPS walkthrough" style="width:100%"></video>
<nav class="prog" id="prog" aria-label="Jump to a step in the video" hidden><button type="button" data-s="1">1 Copy</button><span>·</span><button type="button" data-s="2">2 Add</button><span>·</span><button type="button" data-s="3">3 Ask</button></nav>
<div class="g">
<div class="card" data-step="1"><div class="n">1</div><span class="label">Copy the URL<svg class="ink" viewBox="0 0 200 10" preserveAspectRatio="none" aria-hidden="true"><path d="M1 6.2 C 20 4.9, 45 5.6, 70 4.6 S 120 4.1, 150 4.9 S 185 5.3, 199 3.9 L 198.6 4.6 C 182 6.4, 150 7.3, 118 7.1 S 60 7.9, 34 7.6 S 9 7.2, 1 6.6 Z"/></svg></span><p>Add this one URL:</p>
<div class="url"><code id="u">${u}</code><button id="b" type="button">Copy</button></div></div>
<div class="card" data-step="2"><div class="n">2</div><span class="label">Add it to your AI<svg class="ink" viewBox="0 0 200 10" preserveAspectRatio="none" aria-hidden="true"><path d="M0.8 5.4 C 25 4.2, 52 5.1, 84 4.3 S 140 3.6, 168 4.6 S 192 4.4, 199.2 5.3 L 198.4 5.8 C 176 7.0, 146 6.6, 112 7.4 S 58 7.0, 30 7.5 S 8 6.4, 0.8 5.9 Z"/></svg></span><p><b>Claude:</b> Settings → Connectors → Add custom connector.<br><b>ChatGPT:</b> Settings → Connectors (developer mode) → Create.<br><b>Cursor:</b> Settings → MCP → Add server.</p></div>
<div class="card" data-step="3"><div class="n">3</div><span class="label">Ask it<svg class="ink" viewBox="0 0 200 10" preserveAspectRatio="none" aria-hidden="true"><path d="M1.2 4.8 C 30 5.6, 58 4.2, 92 4.9 S 146 5.4, 174 4.2 S 194 4.9, 199 4.4 L 198.8 5.1 C 180 7.6, 152 6.9, 120 7.6 S 66 7.1, 36 7.8 S 10 6.0, 1.2 5.3 Z"/></svg></span><p>Attach your account spreadsheet and say "Score these with A-GPS and tell me who to focus on this week."</p></div>
</div>
<p class="two"><b>Two ways in.</b> No setup? Use the <a class="cta" style="margin:0" href="https://github.com/christianwagar/agps/blob/main/integrations/any-llm/PROMPT.md">Copy-paste prompt</a> in any AI chat. Want the exact calculator inside your AI app? Add this link.</p></section>
<section><span class="label">The clusters</span><h2>P1 to P4</h2><div class="pg">
<div class="p"><span class="chip" style="background:#000;color:#fff">P1</span><div><span class="label">Expand now</span><p>Exec-aligned expansion, multi-thread, bring in AE + SE.</p></div></div>
<div class="p"><span class="chip" style="background:#444;color:#fff">P2</span><div><span class="label">Grow into it</span><p>Land-and-expand, programs, close the weakest bucket first.</p></div></div>
<div class="p"><span class="chip" style="background:#999;color:#fff">P3</span><div><span class="label">Protect and re-ignite</span><p>Retention first, fix health, find the next use case.</p></div></div>
<div class="p"><span class="chip" style="border:1px solid #000">P4</span><div><span class="label">Scale and monitor</span><p>Digital or pooled CS, watch for signals.</p></div></div>
</div>
<p class="links"><a class="cta" href="https://26-w.com/notes/account-growth-propensity/">Read the writeup</a><a class="cta" href="https://github.com/christianwagar/agps">View on GitHub</a></p></section>
<footer>Built by <a href="https://26-w.com">Christian Wagar · 26-W</a> · MIT License · Sample data is fictional.</footer>
</div><script>
document.getElementById("b").onclick=function(){var b=this;navigator.clipboard.writeText(document.getElementById("u").textContent).then(function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy"},1600)})};

(function(){var v=document.getElementById("v");if(!v||!v.canPlayType)return;
var ok=v.canPlayType("video/webm")||v.canPlayType("video/mp4");if(!ok)return; // GIF fallback: no sync
var cards=[].slice.call(document.querySelectorAll(".card[data-step]")),prog=document.getElementById("prog"),btns=[].slice.call(prog.querySelectorAll("button"));
var START={1:0,2:4.5,3:9};
if(window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches){v.removeAttribute("autoplay");v.pause();v.controls=true;return;}
prog.hidden=false;document.querySelector(".g").classList.add("sync");var cur=0;
function stepAt(t){return t<4.5?1:t<9?2:3}
function set(n){if(n===cur)return;cur=n;cards.forEach(function(c){c.classList.toggle("on",+c.dataset.step===n)});btns.forEach(function(b){b.classList.toggle("on",+b.dataset.s===n);b.setAttribute("aria-current",+b.dataset.s===n?"step":"false")})}
function tick(){if(!v.paused&&v.readyState>1)set(stepAt(v.currentTime));requestAnimationFrame(tick)}
v.addEventListener("timeupdate",function(){set(stepAt(v.currentTime))});
btns.forEach(function(b){b.onclick=function(){var n=+b.dataset.s;v.currentTime=START[n]+0.01;set(n);var p=v.play();if(p&&p.catch)p.catch(function(){})}});
requestAnimationFrame(tick);
// Static assets aren't served with byte ranges, so load the clip into memory once to make seeking reliable.
v.addEventListener("loadeddata",function once(){v.removeEventListener("loadeddata",once);var src=v.currentSrc;if(!src||!window.fetch||!window.URL)return;
fetch(src).then(function(r){return r.ok?r.blob():null}).then(function(bl){if(!bl)return;var t=v.currentTime;v.src=URL.createObjectURL(bl);v.addEventListener("loadedmetadata",function(){v.currentTime=t;var p=v.play();if(p&&p.catch)p.catch(function(){})},{once:true})}).catch(function(){})});
if(v.readyState>=2)v.dispatchEvent(new Event("loadeddata"))})();
</script></body></html>`;
}
