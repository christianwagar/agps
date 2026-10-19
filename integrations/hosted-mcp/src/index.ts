// A-GPS hosted MCP server (Cloudflare Workers, stateless Streamable HTTP at /mcp).
// Privacy: nothing is stored, nothing is logged. Accounts live only for the length of one request.
import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";
import defaults from "../../../config/agps.v2.json";
import { applySettings, explainAccount, getFocusList, scoreAccounts, type Config } from "./engine";
import { landingPage } from "./landing";

const NAME = "A-GPS | Account Growth Propensity Scoring";
const DEFAULTS = defaults as Config;

const accountsInput = {
  accounts: z.array(z.record(z.string(), z.any())).optional()
    .describe("Your accounts, one object per account. Needs an account_name. Use the field names from get_default_settings (e.g. arr, nrr, opp_win_rate)."),
  csv: z.string().optional().describe("Or paste the accounts as CSV text instead (first row = headers)."),
  mapping: z.record(z.string(), z.string()).optional()
    .describe('Optional: rename your headers to A-GPS fields, e.g. {"Account Name": "account_name", "ARR": "arr"}.'),
  settings: z.record(z.string(), z.any()).optional()
    .describe('Optional tweaks merged over the defaults, in plain JSON. E.g. {"bucket_weights": {"gtm_propensity": 0.25, "marketing_programmatic_engagement": 0.15}} or {"options": {"renewal_direction": "runway_is_better"}} or new bands for a field under "fields".'),
  cluster_method: z.enum(["quartile", "growth_arr_2x2"]).optional()
    .describe("quartile (default): rank and split into four equal groups. growth_arr_2x2: growth vs ARR quadrant."),
};

const ok = (data: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] });
const fail = (e: unknown) => ({ isError: true, content: [{ type: "text" as const, text: e instanceof Error ? e.message : String(e) }] });

function createServer() {
  const server = new McpServer({ name: "agps", title: NAME, version: "2.0.0" }, {
    instructions: "A-GPS scores customer accounts golf-style: 1 is best, 8 is worst, lower overall is better. Accounts land in P1 (expand now) to P4 (protect / low touch). It's a framework: tune the weights and bands to your business. Nothing you send is stored.",
  });

  server.registerTool("score_accounts", {
    title: "Score my accounts",
    description: "Score your accounts with A-GPS and sort them into P1 to P4. Golf rules: lower is better. You get each account's bucket scores, a cluster summary with the play for each group, and a focus-this-week list. Send settings to tune weights or bands for your business. Nothing is stored.",
    inputSchema: z.object({ ...accountsInput, limit: z.number().int().min(1).max(1000).optional().describe("Max accounts to return (default 100).") }),
  }, async ({ limit, settings, ...inp }) => {
    try {
      const r = scoreAccounts(applySettings(DEFAULTS, settings), inp);
      return ok({ ...r, accounts: r.accounts.slice(0, limit ?? 100) });
    } catch (e) { return fail(e); }
  });

  server.registerTool("explain_account", {
    title: "Explain one account",
    description: "Tell me why an account landed where it did: its bucket scores, strongest and weakest bucket, best and worst fields, and the play for its cluster. Built from the scores, not a guess.",
    inputSchema: z.object({ account_name: z.string().describe("The account to explain."), ...accountsInput }),
  }, async ({ account_name, settings, ...inp }) => {
    try { return ok(explainAccount(applySettings(DEFAULTS, settings), inp, account_name)); } catch (e) { return fail(e); }
  });

  server.registerTool("get_focus_list", {
    title: "Who to focus on this week",
    description: "The accounts worth your time this week: best overall score among renewals coming up inside the window. If not enough are in the window, it fills with the next renewals.",
    inputSchema: z.object({ ...accountsInput,
      count: z.number().int().min(1).max(50).optional().describe("How many accounts (default 3)."),
      window_days: z.number().int().min(0).optional().describe("Renewal window in days (default 120).") }),
  }, async ({ count, window_days, settings, ...inp }) => {
    try { return ok(getFocusList(applySettings(DEFAULTS, settings), inp, count, window_days)); } catch (e) { return fail(e); }
  });

  server.registerTool("get_default_settings", {
    title: "Show the default settings",
    description: "The full default A-GPS model: bucket weights, every field with its bands, options and plays. Start here to see what fields to send and what you can tune.",
    inputSchema: z.object({}),
  }, async () => ok(DEFAULTS));

  return server;
}

const mcp = createMcpHandler(createServer, { route: "/mcp", allowedHostnames: ["mcp.26-w.com", "localhost", "127.0.0.1"] });

export default {
  async fetch(request: Request, env: unknown, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/mcp") return mcp(request, env, ctx);
    if (url.pathname === "/" && (request.method === "GET" || request.method === "HEAD"))
      return new Response(landingPage(/^(localhost|127\.0\.0\.1)$/.test(url.hostname) ? `${url.origin}/mcp` : `https://${url.host}/mcp`), { headers: {
        "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300",
        "content-security-policy": "default-src 'none'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; script-src 'unsafe-inline'; img-src 'self' data:; media-src 'self'",
      } });
    if (url.pathname === "/health") return Response.json({ ok: true, name: NAME });
    return new Response("Not found", { status: 404 });
  },
} satisfies ExportedHandler;
