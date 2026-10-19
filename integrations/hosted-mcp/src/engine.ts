// A-GPS scoring engine: a line-by-line TypeScript port of src/agps/engine.py + api.py.
// Golf-style: every field gets a band score 1 (best) .. 8 (worst); lower overall = higher priority.
// Pure functions. No storage, no logging, no network.
export type Row = Record<string, any>;
export type Config = Record<string, any>;
export const NA = "n/a";

const DEFAULT_OPTIONS: Record<string, any> = {
  not_applicable: "exclude", empty_bucket: "renormalize", use_field_weights: false,
  size_normalization: false, min_closed_opps: 3, min_survey_responses: 3,
  renewal_direction: "sooner_is_better", arr_scoring: "absolute", segment_field: null, stale_rag_penalty: false,
};
const NA_TOKENS = new Set(["n/a", "na", "not applicable", "not_applicable"]);
const OPS: Record<string, (a: number, b: number) => boolean> = {
  eq: (a, b) => a === b, ne: (a, b) => a !== b, lt: (a, b) => a < b,
  lte: (a, b) => a <= b, gt: (a, b) => a > b, gte: (a, b) => a >= b,
};
const PLAY_LABELS = ["P1", "P2", "P3", "P4"];

/** Python round(x, n): correctly rounded on the exact binary value, ties to even. */
export function pyRound(x: number, n: number): number {
  if (!isFinite(x)) return x;
  const neg = x < 0;
  const s = Math.abs(x).toFixed(100); // exact decimal expansion of the double
  const [ip, fp] = s.split(".");
  const keep = fp.slice(0, n), rest = fp.slice(n);
  let digits = ip + keep;
  const first = rest[0], tail = rest.slice(1);
  let up = first > "5" || (first === "5" && /[1-9]/.test(tail));
  if (first === "5" && !/[1-9]/.test(tail)) up = (Number(digits[digits.length - 1]) % 2) === 1;
  let big = BigInt(digits) + (up ? 1n : 0n);
  const v = Number(big) / 10 ** n;
  return neg ? -v : v;
}

// Python float() on the cleaned string.
const FLOAT_RE = /^[+-]?((\d(_?\d)*)(\.(\d(_?\d)*)?)?|\.\d(_?\d)*)([eE][+-]?\d(_?\d)*)?$/;
export function num(v: any): number | null {
  if (v === null || v === undefined) return null;
  if (typeof v === "boolean") return v ? 1 : 0;
  if (typeof v === "number") return v;
  const s = pyStr(v).trim().replace(/,/g, "").replace(/\$/g, "").replace(/%/g, "");
  if (s === "") return null;
  const l = s.toLowerCase().replace(/^[+-]/, "");
  if (l === "inf" || l === "infinity") return s.startsWith("-") ? -Infinity : Infinity;
  if (l === "nan") return NaN;
  if (!FLOAT_RE.test(s)) return null;
  return parseFloat(s.replace(/_/g, ""));
}
function pyStr(v: any): string {
  if (typeof v === "boolean") return v ? "True" : "False";
  return String(v);
}
const blank = (v: any) => v === null || v === undefined || pyStr(v).trim() === "";
const cond = (row: Row, c: any) => { const v = num(row[c.field]); return v !== null && OPS[c.op ?? "eq"](v, c.value); };

export function options(cfg: Config) {
  const out = { ...DEFAULT_OPTIONS };
  for (const [k, v] of Object.entries(cfg.options ?? {}))
    out[k] = v && typeof v === "object" && !Array.isArray(v) && "value" in (v as any) ? (v as any).value : v;
  return out;
}

export function bandScore(bands: any[], val: number, missing: number) {
  for (const b of bands) {
    const lo = b.min, hx = b.max_exclusive, hi = b.max;
    if (lo !== undefined && lo !== null && val < lo) continue;
    if (hx !== undefined && hx !== null && val >= hx) continue;
    if (hi !== undefined && hi !== null && val > hi) continue;
    return b.score;
  }
  return missing;
}

function modify(cfg: Config, opts: any, spec: any, row: Row, score: number) {
  const st = spec.stale;
  if (st && opts[st.option]) {
    const age = num(row[st.field]);
    if (age !== null && age > st.after_days) score = Math.min(cfg.scale.missing_score, score + (st.add ?? 1));
  }
  return score;
}

export function fieldScore(cfg: Config, opts: any, name: string, spec: any, row: Row): number | string {
  const missing = cfg.scale.missing_score;
  const naResult = opts.not_applicable === "exclude" ? NA : missing;
  const raw = row[name];
  for (const c of spec.na_if ?? []) if (cond(row, c)) return naResult;
  const mc = spec.min_count;
  if (mc && !blank(row[mc.field])) {
    const n = num(row[mc.field]);
    if (n !== null && n < opts[mc.option]) return naResult;
  }
  for (const o of spec.overrides ?? []) if (cond(row, o)) return o.score;
  if (blank(raw)) return spec.missing === "na" ? naResult : missing;
  const s = pyStr(raw).trim().toLowerCase();
  if (NA_TOKENS.has(s) && spec.type !== "ordinal") return naResult;
  const t = spec.type ?? "number";
  let val: number | null | undefined;
  if (t === "ordinal" && "levels" in spec) {
    const lv: Record<string, any> = {};
    for (const [k, v] of Object.entries(spec.levels)) lv[k.toLowerCase()] = v;
    if (!(s in lv)) return missing;
    return lv[s] === "na" ? naResult : modify(cfg, opts, spec, row, lv[s]);
  }
  if (t === "ordinal") {
    const m: Record<string, any> = {};
    for (const [k, v] of Object.entries(spec.ordinal_map)) m[k.toLowerCase()] = v;
    val = s in m ? m[s] : null;
  } else if (t === "boolean") {
    const bv = cfg.boolean_values ?? { true: ["true", "t", "yes", "y", "1"], false: ["false", "f", "no", "n", "0"] };
    val = bv.true.includes(s) ? 1 : bv.false.includes(s) ? 0 : null;
  } else {
    val = num(raw);
    const pct = spec.transform?.percent_of;
    if (pct) { const base = num(row[pct]) || 0; val = base > 0 ? (100 * (val || 0)) / base : null; }
  }
  if (val === null || val === undefined) return missing;
  let bands = spec.bands;
  if ("band_sets" in spec) {
    bands = spec.band_sets[opts[spec.band_option]];
    if (!bands) throw new Error(`setting '${spec.band_option}' must be one of: ${Object.keys(spec.band_sets).join(", ")}`);
  }
  const norm = spec.normalize;
  if (norm && opts.size_normalization) {
    const base = num(row[norm.divide_by]);
    if (!base) return missing;
    val = (val / base) * (norm.multiply ?? 1); bands = norm.bands;
  }
  return modify(cfg, opts, spec, row, bandScore(bands, val, missing));
}

function percentileScores(rows: Row[], field: string, seg: string | null) {
  const groups = new Map<any, Row[]>();
  for (const r of rows) if (num(r[field]) !== null) {
    const k = seg ? r[seg] : null;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k)!.push(r);
  }
  const out = new Map<Row, number>();
  for (const g0 of groups.values()) {
    const g = [...g0].sort((a, b) => -num(a[field])! - -num(b[field])!);
    g.forEach((r, i) => out.set(r, Math.min(8, 1 + Math.floor((8 * i) / g.length))));
  }
  return out;
}

function wavg(pairs: [number, number][]) {
  let tw = 0, s = 0;
  for (const [, w] of pairs) tw += w;
  for (const [v, w] of pairs) s += v * w;
  return tw ? s / tw : null;
}
// Python's sum() adds left to right from 0, same as above.

function cmpTuple(a: any[], b: any[]) {
  for (let i = 0; i < a.length; i++) {
    if (a[i] < b[i]) return -1;
    if (a[i] > b[i]) return 1;
  }
  return 0;
}

export function scoreRows(cfg: Config, rows: Row[], method?: string | null) {
  const opts = options(cfg);
  const W: Record<string, number> = cfg.bucket_weights;
  const missing = cfg.scale.missing_score;
  const rd = cfg.rounding ?? { bucket_scores: 2, overall_score: 3 };
  const v1 = !("options" in cfg);
  const pct: Record<string, Map<Row, number>> = {};
  for (const [f, spec] of Object.entries<any>(cfg.fields)) {
    const po = spec.percentile_option;
    if (po && opts[po] === "percentile") pct[f] = percentileScores(rows, f, opts.segment_field);
  }
  rows.forEach((r, i) => {
    r._i = i;
    const fs: Record<string, any> = {};
    for (const [f, spec] of Object.entries<any>(cfg.fields))
      fs[f] = f in pct ? (pct[f].get(r) ?? missing) : fieldScore(cfg, opts, f, spec, r);
    r._fields = fs;
    const b: Record<string, number | null> = {}, bx: Record<string, number | null> = {};
    const w = (spec: any) => (v1 || opts.use_field_weights ? (spec.weight ?? 1) : 1);
    for (const bk of Object.keys(W)) {
      const ents = Object.entries<any>(cfg.fields).filter(([f, s]) => s.bucket === bk && fs[f] !== NA);
      const pairs = ents.map(([f, s]) => [fs[f], w(s)] as [number, number]);
      const ex = ents.filter(([f]) => f !== "arr").map(([f, s]) => [fs[f], w(s)] as [number, number]);
      b[bk] = wavg(pairs);
      if (b[bk] === null && opts.empty_bucket === "score_missing") b[bk] = missing;
      bx[bk] = ex.length ? wavg(ex) : b[bk];
    }
    r._buckets = b;
    for (const bk of Object.keys(W)) r[`${bk}_score`] = b[bk] === null ? "" : pyRound(b[bk]!, rd.bucket_scores);
    const live = Object.entries(W).filter(([k]) => b[k] !== null).map(([k, wt]) => [b[k]!, wt] as [number, number]);
    r._overall = live.length ? wavg(live) : missing;
    const gx = Object.keys(W).filter((k) => bx[k] !== null).map((k) => [bx[k]!, W[k]] as [number, number]);
    r._growth_ex_arr = gx.length ? wavg(gx) : missing;
    r.overall_score = pyRound(r._overall, rd.overall_score);
  });
  assignClusters(cfg, rows, method);
  return rows;
}

function median(xs: number[]) {
  const s = [...xs].sort((a, b) => a - b), n = s.length;
  if (!n) throw new Error("no accounts to score");
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2;
}

export function assignClusters(cfg: Config, rows: Row[], method?: string | null) {
  const cl = cfg.cluster;
  method = method || cl.method;
  if (method === "quartile") {
    const labels = cl.quartile?.labels ?? PLAY_LABELS;
    const ranked = [...rows].sort((a, b) => cmpTuple([a._overall, -(num(a.arr) || 0), a._i], [b._overall, -(num(b.arr) || 0), b._i]));
    const size = Math.floor(ranked.length / 4), rem = ranked.length % 4;
    let i = 0;
    for (let q = 0; q < 4; q++) for (let k = 0; k < size + (q < rem ? 1 : 0); k++) ranked[i++].cluster = labels[q];
  } else if (method === "growth_arr_2x2") {
    const c = cl.growth_arr_2x2;
    const med = median(rows.map((r) => r._growth_ex_arr));
    for (const r of rows) {
      const g = r._growth_ex_arr <= med;
      const fa = r._fields.arr;
      const a = fa !== undefined && fa !== null && fa !== NA && fa <= c.arr_high_max_band;
      r.cluster = g ? (a ? "P1" : "P2") : (a ? "P3" : "P4");
    }
  } else throw new Error(`unknown cluster method '${method}'`);
}

export const renewalDays = (cfg: Config, r: Row) => num(r[cfg.focus?.renewal_field ?? "days_to_next_renewal"]);

export function focusList(cfg: Config, rows: Row[], count?: number | null, windowDays?: number | null) {
  const f = cfg.focus ?? {};
  const n = count || f.count || 3;
  const win = windowDays ?? f.window_days ?? 120;
  const ren = (r: Row) => renewalDays(cfg, r);
  const key = (r: Row) => [r.overall_score, ren(r), pyStr(r.account_name ?? "")];
  const inw = rows.filter((r) => ren(r) !== null && ren(r)! <= win).sort((a, b) => cmpTuple(key(a), key(b)));
  if (inw.length >= n) return inw.slice(0, n);
  const later = rows.filter((r) => ren(r) !== null && ren(r)! > win).sort((a, b) => cmpTuple([ren(a), ...key(a)], [ren(b), ...key(b)]));
  return [...inw, ...later].slice(0, n);
}

export function explain(cfg: Config, r: Row) {
  const W: Record<string, number> = cfg.bucket_weights;
  const live = Object.keys(W).filter((k) => r._buckets[k] !== null);
  const ranked = [...live].sort((a, b) => cmpTuple([r._buckets[a], -W[a]], [r._buckets[b], -W[b]]));
  const scored = Object.entries<any>(r._fields).filter(([, v]) => v !== NA);
  const bs: Record<string, number | null> = {};
  for (const k of Object.keys(W)) bs[k] = r._buckets[k] === null ? null : pyRound(r._buckets[k], 2);
  return {
    account: r.account_name ?? null, cluster: r.cluster, overall_score: r.overall_score, bucket_scores: bs,
    strongest_bucket: ranked[0] ?? null, weakest_bucket: ranked.length ? ranked[ranked.length - 1] : null,
    best_fields: [...scored].sort((a, b) => a[1] - b[1]).slice(0, 3).map(([field, score]) => ({ field, score })),
    weakest_fields: [...scored].sort((a, b) => b[1] - a[1]).slice(0, 3).map(([field, score]) => ({ field, score })),
    not_applicable: Object.entries<any>(r._fields).filter(([, v]) => v === NA).map(([k]) => k),
    play: cfg.plays?.[r.cluster] ?? null,
    note: "Generated from the scores; not an AI judgement.",
  };
}

// ---------- api.py ----------
export function parseCsv(text: string): { cols: string[]; rows: Row[] } {
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1);
  const lines = text.split(/(?<=\n)/).filter((l) => !l.startsWith("#")).join("");
  const recs: string[][] = []; let rec: string[] = [], fld = "", q = false, i = 0, any = false;
  while (i < lines.length) {
    const ch = lines[i];
    if (q) {
      if (ch === '"') { if (lines[i + 1] === '"') { fld += '"'; i++; } else q = false; }
      else fld += ch;
    } else if (ch === '"') { q = true; any = true; }
    else if (ch === ",") { rec.push(fld); fld = ""; any = true; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && lines[i + 1] === "\n") i++;
      if (any || fld !== "" || rec.length) { rec.push(fld); recs.push(rec); }
      rec = []; fld = ""; any = false;
    } else { fld += ch; any = true; }
    i++;
  }
  if (any || fld !== "" || rec.length) { rec.push(fld); recs.push(rec); }
  const cols = recs.shift() ?? [];
  const rows = recs.map((r) => { const o: Row = {}; cols.forEach((c, j) => (o[c] = (r[j] ?? "").trim())); return o; });
  return { cols, rows };
}

export interface Input { accounts?: Row[]; csv?: string; mapping?: Record<string, string>; cluster_method?: string | null }

function prep(cfg: Config, inp: Input) {
  let cols: string[], rows: Row[];
  const m = inp.mapping ?? {};
  if (inp.accounts) {
    rows = inp.accounts.map((r) => { const o: Row = {}; for (const [k, v] of Object.entries(r)) o[m[k] ?? k] = v; return o; });
    cols = rows.length ? Object.keys(rows[0]) : [];
  } else if (inp.csv) {
    const p = parseCsv(inp.csv);
    cols = p.cols.map((c) => m[c] ?? c);
    rows = p.rows.map((r) => { const o: Row = {}; for (const [k, v] of Object.entries(r)) o[m[k] ?? k] = v; return o; });
  } else throw new Error("Send your accounts as `accounts` (a list of rows) or `csv` (CSV text).");
  if (!rows.length) throw new Error("No accounts found. Send at least one row.");
  if (!cols.includes("account_name")) throw new Error("missing required column(s) ['account_name']; map your headers with mapping");
  scoreRows(cfg, rows, inp.cluster_method);
  return { cols, rows };
}

const outCols = (cfg: Config) => [...Object.keys(cfg.bucket_weights).map((b) => `${b}_score`), "overall_score", "cluster"];
function pub(cfg: Config, r: Row, cols?: string[]) {
  const keep = [...new Set([...(cols ?? ["account_name", "arr"]), ...outCols(cfg)])];
  const o: Row = {};
  for (const k of keep) if (!k.startsWith("_")) o[k] = r[k] ?? null;
  return o;
}
const focusItem = (cfg: Config, r: Row) => ({
  account: r.account_name ?? null, cluster: r.cluster, overall_score: r.overall_score,
  days_to_renewal: renewalDays(cfg, r), arr: num(r.arr),
});

export function scoreAccounts(cfg: Config, inp: Input & { include_inputs?: boolean }) {
  const { cols, rows } = prep(cfg, inp);
  const ranked = [...rows].sort((a, b) => cmpTuple([a._overall, a._i], [b._overall, b._i]));
  const clusters: Row = {};
  for (const k of PLAY_LABELS) {
    const g = ranked.filter((r) => r.cluster === k);
    clusters[k] = { accounts: g.length, total_arr: g.reduce((s, r) => s + (num(r.arr) || 0), 0),
      top: g.slice(0, 3).map((r) => r.account_name ?? null), play: cfg.plays?.[k] ?? null };
  }
  return {
    config: cfg.name ?? null, scored: rows.length,
    missing_fields: Object.keys(cfg.fields).filter((f) => !cols.includes(f)),
    clusters, focus_this_week: focusList(cfg, rows).map((r) => focusItem(cfg, r)),
    accounts: ranked.map((r) => pub(cfg, r, inp.include_inputs ? cols : undefined)),
  };
}

export function explainAccount(cfg: Config, inp: Input, name: string) {
  const { rows } = prep(cfg, inp);
  const r = rows.find((x) => pyStr(x.account_name ?? "").toLowerCase() === name.toLowerCase());
  if (!r) throw new Error(`account '${name}' not found`);
  return explain(cfg, r);
}

export function getFocusList(cfg: Config, inp: Input, count?: number | null, windowDays?: number | null) {
  const { rows } = prep(cfg, inp);
  return focusList(cfg, rows, count, windowDays).map((r) => focusItem(cfg, r));
}

/** Deep-merge plain-JSON setting overrides onto a config (objects merge, everything else replaces). */
export function applySettings(base: Config, over?: Record<string, any> | null): Config {
  const cfg = structuredClone(base);
  if (!over) return cfg;
  const merge = (t: any, s: any) => {
    for (const [k, v] of Object.entries(s)) {
      if (v && typeof v === "object" && !Array.isArray(v) && t[k] && typeof t[k] === "object" && !Array.isArray(t[k])) merge(t[k], v);
      else t[k] = v;
    }
  };
  merge(cfg, over);
  const w = cfg.bucket_weights;
  for (const k of Object.keys(w)) if (typeof w[k] !== "number" || w[k] < 0) throw new Error(`bucket weight '${k}' must be a number >= 0`);
  return cfg;
}
