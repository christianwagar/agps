// A-GPS hosted MCP server (Cloudflare Workers, stateless Streamable HTTP at /mcp).
// Privacy: nothing is stored, nothing is logged. Accounts live only for the length of one request.
import { createMcpHandler } from "agents/mcp/server";
import { createServer, NAME } from "./server";
import { landingPage } from "./landing";

const mcp = createMcpHandler(createServer, { route: "/mcp", allowedHostnames: ["mcp.26-w.com", "localhost", "127.0.0.1"] });

export default {
  async fetch(request: Request, env: unknown, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/mcp") return mcp(request, env, ctx);
    if (url.pathname === "/" && (request.method === "GET" || request.method === "HEAD"))
      return new Response(landingPage(/^(localhost|127\.0\.0\.1)$/.test(url.hostname) ? `${url.origin}/mcp` : `https://${url.host}/mcp`), { headers: {
        "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300",
        "content-security-policy": "default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'unsafe-inline'; img-src 'self' data:; media-src 'self' blob:; connect-src 'self'",
      } });
    if (url.pathname === "/health") return Response.json({ ok: true, name: NAME });
    return new Response("Not found", { status: 404 });
  },
} satisfies ExportedHandler;
