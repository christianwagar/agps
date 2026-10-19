# Contributing

Issues and pull requests are welcome.

## Setup
```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Changing the model
- To change fields, bands or defaults, edit `tools/build_config.py` and run `python tools/build_config.py && python tools/gen_methodology.py`. That regenerates the YAML, both JSON twins and METHODOLOGY.md.
- If you only edit `config/agps.v2.yaml`, run `agps convert config/agps.v2.yaml config/agps.v2.json` and copy the result to `src/agps/data/`.
- Add a test for any new band or rule. Edge values (exactly on a threshold) matter most.
- `config/agps.v1-compat.json` must keep reproducing `tests/expected_v1_scores.csv`. Don't change it in a PR unless the live model changed.

## Ground rules
- The core package stays stdlib-only. Optional extras (PyYAML, mcp) live behind extras.
- Never commit real customer data. Sample data must be fictional and marked as such.
- Keep docs plain and practical.
