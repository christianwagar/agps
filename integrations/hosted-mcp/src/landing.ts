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
h1{font-size:clamp(3rem,9vw,6.5rem)}h2{font-size:clamp(1.75rem,4vw,2.5rem)}
.sub{font-family:var(--d);font-weight:600;letter-spacing:.2em;text-transform:uppercase;font-size:1.1rem;margin:-.5rem 0 1rem}
.intro{color:var(--muted);max-width:56ch}section{padding:4rem 0;border-top:1px solid var(--border)}
.cta,button{font-family:var(--d);font-weight:600;letter-spacing:.14em;text-transform:uppercase;margin-right:1.5rem;font-size:1rem}
.cta:before,button:before{content:"[ "}.cta:after,button:after{content:" ]"}
.url{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;background:var(--bg-soft);border:1px solid var(--border);padding:1.25rem 1.5rem;margin:1.5rem 0}
.url code{font-size:1.05rem;word-break:break-all;flex:1}
button{background:none;border:0;padding:0;cursor:pointer;color:var(--text)}button:hover{opacity:.55}
.g{display:grid;gap:2rem;grid-template-columns:repeat(3,1fr)}@media(max-width:800px){.g{grid-template-columns:1fr}}
.card{border-top:1px solid #000;padding-top:1rem}.card p{color:var(--muted);margin:.5rem 0 0}
.n{font-family:var(--d);font-weight:700;font-size:2.5rem;line-height:1}
.chips{display:flex;gap:.5rem;margin:1.5rem 0}.chips span{font-family:var(--d);font-weight:700;letter-spacing:.1em;width:3rem;height:3rem;display:grid;place-items:center}
ul{color:var(--muted);padding-left:1.1rem}
footer{padding:2rem 0;border-top:1px solid var(--border);color:var(--muted);font-size:.85rem}
</style></head><body><div class="c">
<header><a href="https://26-w.com">26-W / Notes</a><span>Christian Wagar</span></header>
<section style="border:0"><span class="label">MCP server · free · no sign-up</span><h1>A-GPS</h1>
<p class="sub">Account Growth Propensity Scoring</p>
<p class="intro">Score your book of customer accounts right inside your AI. Golf rules: lower is better. Every account lands in P1 to P4 with the why and a focus-this-week list.</p>
<div class="chips"><span style="background:#000;color:#fff">P1</span><span style="background:#444;color:#fff">P2</span><span style="background:#999;color:#fff">P3</span><span style="border:1px solid #000">P4</span></div>
<span class="label">Add this one URL</span>
<div class="url"><code id="u">${u}</code><button id="b" type="button">Copy</button></div>
</section>
<section><span class="label">Three steps</span><h2>Two minutes, no code</h2><div class="g">
<div class="card"><div class="n">1</div><span class="label">Copy the URL</span><p>Hit [ COPY ] above.</p></div>
<div class="card"><div class="n">2</div><span class="label">Add it to your AI</span><p><b>Claude:</b> Settings → Connectors → Add custom connector.<br><b>ChatGPT:</b> Settings → Connectors (developer mode) → Create.<br><b>Cursor:</b> Settings → MCP → Add server.</p></div>
<div class="card"><div class="n">3</div><span class="label">Ask it</span><p>Attach your account spreadsheet and say "Score these with A-GPS and tell me who to focus on this week."</p></div>
</div></section>
<section><span class="label">Read this first</span><h2>A framework, not a formula</h2>
<p class="intro">The weights and bands were tuned for one book of business. Yours is different. Just tell your AI in plain English, like "use 25% GTM and 15% marketing" or "ARR band 1 is $200K+", and it passes the tweak along.</p>
<ul><li>Nothing you send is stored or logged. Each request is scored and forgotten.</li><li>No account or sign-up needed.</li></ul>
<a class="cta" href="https://26-w.com/notes/account-growth-propensity/">Read the writeup</a><a class="cta" href="https://github.com/christianwagar/agps">View on GitHub</a></section>
<footer>Built by <a href="https://26-w.com">Christian Wagar · 26-W</a> · MIT License · Sample data is fictional.</footer>
</div><script>
document.getElementById("b").onclick=function(){var b=this;navigator.clipboard.writeText(document.getElementById("u").textContent).then(function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy"},1600)})};
</script></body></html>`;
}
