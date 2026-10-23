// A-GPS MCP server definition (tools only). Kept separate from the Worker entry so tests can load it in Node.
import { McpServer } from "@modelcontextprotocol/server";
import { z } from "zod";
import defaults from "../../../config/agps.v2.json";
import { applySettings, explainAccount, getFocusList, scoreAccounts, type Config } from "./engine";

export const NAME = "A-GPS | Account Growth Propensity Scoring";
const DEFAULTS = defaults as Config;

// Every tool is a pure calculation over the input sent with the call: no writes, no storage,
// no outbound network calls. Same input + settings -> same output.
export const TOOL_ANNOTATIONS = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false } as const;

const accountsInput = {
  accounts: z.array(z.record(z.string(), z.any())).optional()
    .describe("Your accounts, one object per account. Needs an account_name. Use the field names from get_default_settings (e.g. arr, nrr, opp_win_rate)."),
  csv: z.string().optional().describe("Or paste the accounts as CSV text instead (first row = headers)."),
  mapping: z.record(z.string(), z.string()).optional()
    .describe('Optional: rename your headers to A-GPS fields, e.g. {"Account Name": "account_name", "ARR": "arr"}.'),
  settings: z.record(z.string(), z.any()).optional()
    .describe('Optional tweaks merged over the defaults, in plain JSON. E.g. {"bucket_weights": {"gtm_propensity": 0.25, "marketing_programmatic_engagement": 0.15}} or {"options": {"renewal_direction": "runway_is_better"}} or new bands for a field under "fields".'),
  cluster_method: z.enum(["median_2x2", "quartile", "growth_arr_2x2"]).optional()
    .describe("median_2x2 (default): growth potential (score without ARR) vs spend (ARR), both split at the median; WATCH flags NRR < 90% or growth worse than 6.0. quartile: legacy four equal groups by overall score. growth_arr_2x2: legacy growth vs ARR-band quadrant."),
};

const ok = (data: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] });
const fail = (e: unknown) => ({ isError: true, content: [{ type: "text" as const, text: e instanceof Error ? e.message : String(e) }] });

export function createServer() {
  const server = new McpServer({ name: "agps", title: NAME, version: "2.0.0" }, {
    instructions: "A-GPS scores customer accounts golf-style: 1 is best, 8 is worst, lower overall is better. Accounts land on a median-split 2x2 of growth potential vs spend: P1 high growth + high spend, P2 high growth + lower spend, P3 lower growth + high spend, P4 lower on both; WATCH flags health risks. It's a framework: tune the weights and bands to your business. Nothing you send is stored.",
  });

  server.registerTool("score_accounts", {
    title: "Score my accounts",
    description: "Score your accounts with A-GPS and sort them into P1 to P4. Golf rules: lower is better. You get each account's bucket scores, a cluster summary with the play for each group, and a focus-this-week list. Send settings to tune weights or bands for your business. Nothing is stored.",
    inputSchema: z.object({ ...accountsInput, limit: z.number().int().min(1).max(1000).optional().describe("Max accounts to return (default 100).") }),
    annotations: TOOL_ANNOTATIONS,
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
    annotations: TOOL_ANNOTATIONS,
  }, async ({ account_name, settings, ...inp }) => {
    try { return ok(explainAccount(applySettings(DEFAULTS, settings), inp, account_name)); } catch (e) { return fail(e); }
  });

  server.registerTool("get_focus_list", {
    title: "Who to focus on this week",
    description: "The accounts worth your time this week: best overall score among renewals coming up inside the window. If not enough are in the window, it fills with the next renewals.",
    inputSchema: z.object({ ...accountsInput,
      count: z.number().int().min(1).max(50).optional().describe("How many accounts (default 3)."),
      window_days: z.number().int().min(0).optional().describe("Renewal window in days (default 120).") }),
    annotations: TOOL_ANNOTATIONS,
  }, async ({ count, window_days, settings, ...inp }) => {
    try { return ok(getFocusList(applySettings(DEFAULTS, settings), inp, count, window_days)); } catch (e) { return fail(e); }
  });

  server.registerTool("get_default_settings", {
    title: "Show the default settings",
    description: "The full default A-GPS model: bucket weights, every field with its bands, options and plays. Start here to see what fields to send and what you can tune.",
    inputSchema: z.object({}),
    annotations: TOOL_ANNOTATIONS,
  }, async () => ok(DEFAULTS));

  return server;
}
