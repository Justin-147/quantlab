from __future__ import annotations

from quantlab.models import Fill, PaperAccountState


def record_fill(account: PaperAccountState, fill: Fill) -> PaperAccountState:
    account.fills.append(fill)
    return account


def record_note(account: PaperAccountState, note: str) -> PaperAccountState:
    account.notes.append(note)
    return account
