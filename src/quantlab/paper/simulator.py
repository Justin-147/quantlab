from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from quantlab.models import PaperAccountState, PortfolioConfig, model_to_dict


PAPER_DIR = Path("data/paper_accounts")


def initialize_paper_account(portfolio_config: PortfolioConfig) -> PaperAccountState:
    return PaperAccountState(
        account_id=f"paper_{portfolio_config.name}_{uuid4().hex[:8]}",
        date=datetime.now(),
        cash=float(portfolio_config.initial_cash),
        positions={},
        risk_status="ok",
        notes=["Local paper simulation only. No broker connection exists."],
    )


def run_paper_day(account_state: PaperAccountState, date, prices, strategy=None) -> PaperAccountState:
    account_state.date = date if isinstance(date, datetime) else datetime.fromisoformat(str(date))
    total_positions = sum(
        position.quantity * float(prices.get(symbol, 0.0))
        for symbol, position in account_state.positions.items()
    )
    account_state.equity_history.append(
        {
            "date": account_state.date.strftime("%Y-%m-%d"),
            "cash": account_state.cash,
            "market_value": total_positions,
            "total_value": account_state.cash + total_positions,
        }
    )
    account_state.notes.append("Paper day processed locally; no real orders were submitted.")
    return account_state


def save_paper_account(account_state: PaperAccountState, path: str | Path | None = None) -> Path:
    output = Path(path) if path else PAPER_DIR / f"{account_state.account_id}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(model_to_dict(account_state), indent=2), encoding="utf-8")
    return output


def load_paper_account(account_id: str, path: str | Path | None = None) -> PaperAccountState:
    input_path = Path(path) if path else PAPER_DIR / f"{account_id}.json"
    data = json.loads(input_path.read_text(encoding="utf-8"))
    return PaperAccountState(**data)
