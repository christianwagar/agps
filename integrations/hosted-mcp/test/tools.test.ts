// Every MCP tool, called by name through a real MCP client (in memory), plus its annotations.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { Client, InMemoryTransport } from "@modelcontextprotocol/client";
import { createServer } from "../src/server";

const csv = readFileSync(resolve(__dirname, "../../../examples/v2_small_accounts.csv"), "utf8");
const TOOLS = ["explain_account", "get_default_settings", "get_focus_list", "score_accounts"];

async function connect() {
  const [a, b] = InMemoryTransport.createLinkedPair();
  await createServer().connect(b);
  const client = new Client({ name: "agps-test", version: "1.0.0" });
  await client.connect(a);
  return client;
}
const call = async (c: Client, name: string, args: Record<string, unknown>) => {
  const r: any = await c.callTool({ name, arguments: args });
  expect(r.isError).toBeFalsy();
  return JSON.parse(r.content[0].text);
};

describe("MCP tools", () => {
  it("lists all tools with explicit read-only annotations", async () => {
    const c = await connect();
    const tools = (await c.listTools()).tools;
    expect(tools.map((t) => t.name).sort()).toEqual(TOOLS);
    for (const t of tools) expect(t.annotations).toMatchObject({ readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false });
  });
  it("score_accounts scores every account", async () => {
    const s = await call(await connect(), "score_accounts", { csv });
    expect(s.scored).toBeGreaterThan(0);
    expect(s.accounts[0].account_name).toBeTruthy();
  });
  it("explain_account explains a named account", async () => {
    const c = await connect();
    const top = (await call(c, "score_accounts", { csv })).accounts[0].account_name;
    expect((await call(c, "explain_account", { csv, account_name: top })).account).toBe(top);
  });
  it("get_focus_list returns the requested count", async () => {
    expect(await call(await connect(), "get_focus_list", { csv, count: 2 })).toHaveLength(2);
  });
  it("get_default_settings returns the default model", async () => {
    const d = await call(await connect(), "get_default_settings", {});
    expect(d.bucket_weights).toBeTruthy();
    expect(d.fields).toBeTruthy();
  });
});
