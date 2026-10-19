"""A-GPS: Account Growth Propensity Scoring (golf-style, 1 = best, 8 = worst)."""
from .api import explain_account, get_focus_list, score_accounts
from .io import load_config, read_csv

__all__ = ["score_accounts", "explain_account", "get_focus_list", "load_config", "read_csv"]
__version__ = "0.2.0"
