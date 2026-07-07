from __future__ import annotations

from quantlab.config import load_portfolio_config
from quantlab.paper.simulator import (
    initialize_paper_account,
    load_paper_account,
    save_paper_account,
)


def test_paper_account_state_saves_and_loads(tmp_path):
    account = initialize_paper_account(load_portfolio_config("growth_balanced"))
    path = save_paper_account(account, tmp_path / "paper.json")
    loaded = load_paper_account(account.account_id, path)
    assert loaded.account_id == account.account_id
