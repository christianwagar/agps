// Parity: the TypeScript port must match the Python reference engine exactly.
// Fixtures come from test/make_fixtures.py (Python). Regenerate them after any engine change.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { applySettings, explainAccount, getFocusList, scoreAccounts, pyRound, parseCsv } from "../src/engine";

const ROOT = resolve(__dirname, "../../..");
const cases = JSON.parse(readFileSync(resolve(__dirname, "fixtures.json"), "utf8"));
const load = (p: string) => JSON.parse(readFileSync(resolve(ROOT, p), "utf8"));

describe.each(cases.map((c: any) => [c.name, c]))("parity: %s", (_n, c: any) => {
  const cfg = applySettings(load(c.config), c.settings);
  const csv = readFileSync(resolve(ROOT, c.csv), "utf8");
  const inp = { csv, cluster_method: c.cluster_method };
  it("score_accounts matches Python", () => expect(scoreAccounts(cfg, inp)).toEqual(c.score));
  it("explain_account matches Python for every account", () => {
    for (const [name, exp] of Object.entries(c.explain)) expect(explainAccount(cfg, inp, name)).toEqual(exp);
  });
  it("get_focus_list(5, 60) matches Python", () => expect(getFocusList(cfg, inp, 5, 60)).toEqual(c.focus_5_60));
});

describe("live-site anchors", () => {
  const cfg = load("config/agps.v1-compat.json");
  const csv = readFileSync(resolve(ROOT, "examples/demo_accounts.csv"), "utf8");
  it("legacy quartile: 40 accounts, 10 per cluster, Stripe first, focus Delta/Coca-Cola/Canva", () => {
    const r = scoreAccounts(cfg, { csv, cluster_method: "quartile" });
    expect(r.scored).toBe(40);
    expect(Object.values(r.clusters).map((x: any) => x.accounts)).toEqual([10, 10, 10, 10]);
    expect(r.accounts[0].account_name).toBe("Stripe");
    expect(r.focus_this_week.map((x) => x.account)).toEqual(["Delta", "Coca-Cola", "Canva"]);
  });
  it("default median 2x2 matches the 26-W preview: 14/6/6/14, WATCH floor, focus", () => {
    const r = scoreAccounts(cfg, { csv });
    expect(Object.values(r.clusters).map((x: any) => x.accounts)).toEqual([14, 6, 6, 14]);
    expect(r.focus_this_week.map((x) => x.account)).toEqual(["Delta", "Coca-Cola", "Canva"]);
    const t = explainAccount(cfg, { csv }, "Tesla");
    expect(t.watch).toBe(true);
    expect(t.indicator!.startsWith("Best signal: ")).toBe(true);
  });
  it("accounts given as JSON rows score the same as CSV text", () => {
    expect(scoreAccounts(cfg, { accounts: parseCsv(csv).rows })).toEqual(scoreAccounts(cfg, { csv }));
  });
  it("pyRound behaves like Python round()", () => {
    expect(pyRound(2.675, 2)).toBe(2.67); expect(pyRound(0.125, 2)).toBe(0.12); expect(pyRound(0.375, 2)).toBe(0.38);
    expect(pyRound(3.4445, 3)).toBe(3.445); expect(pyRound(-1.005, 2)).toBe(-1);
  });
});
