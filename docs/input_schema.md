# Input Schema

## Price CSV

Required columns:

```text
date,symbol,open,high,low,close,adjusted_close,volume,currency
```

Rules:

- `date` must parse as a date and cannot be empty.
- `symbol` cannot be empty and must exist in `config/assets.yaml`.
- `open`, `high`, `low`, `close`, and `adjusted_close` must be positive.
- `high` must be at least the maximum of open, low, and close.
- `low` must be at most the minimum of open, high, and close.
- `volume`, when present, must be non-negative.
- `currency` cannot be empty.

## Config Files

Config files live under `config/` and are validated with:

```powershell
python -m quantlab.main validate
```
