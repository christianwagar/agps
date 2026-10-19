"""Config and CSV loading."""
from __future__ import annotations

import csv
import io as _io
import json
import os


def load_config(path_or_dict) -> dict:
    if isinstance(path_or_dict, dict):
        return path_or_dict
    path = str(path_or_dict)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml  # optional dependency: pip install agps[yaml]
        except ImportError as e:  # pragma: no cover
            raise SystemExit("Reading YAML needs PyYAML (pip install 'agps[yaml]'), or use the JSON twin.") from e
        return yaml.safe_load(text)
    return json.loads(text)


def load_mapping(spec) -> dict:
    """JSON file path, dict, or 'Header=field,Other=field2'."""
    if not spec:
        return {}
    if isinstance(spec, dict):
        return spec
    if os.path.exists(spec):
        with open(spec, encoding="utf-8") as fh:
            return {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
    return dict(p.split("=", 1) for p in spec.split(",") if "=" in p)


def read_csv(source, mapping=None):
    """source: file path or CSV text. Lines starting with '#' are skipped. Returns (columns, rows)."""
    mapping = load_mapping(mapping)
    if isinstance(source, str) and ("\n" in source or not os.path.exists(source)):
        text = source
    else:
        with open(source, newline="", encoding="utf-8-sig") as fh:
            text = fh.read()
    lines = [l for l in text.splitlines(keepends=True) if not l.startswith("#")]
    rd = csv.DictReader(lines)
    cols = [mapping.get(c, c) for c in (rd.fieldnames or [])]
    rows = [{mapping.get(k, k): (v or "").strip() for k, v in r.items() if k is not None} for r in rd]
    return cols, rows


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([r.get(c, "") for c in cols])


def to_csv_text(cols, rows) -> str:
    buf = _io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(c, "") for c in cols])
    return buf.getvalue()
