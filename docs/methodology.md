# Methodology

QuantLab is a local-first research prototype for evaluating rule-based portfolio allocation ideas with synthetic or user-provided historical daily price data.

Backtests use a daily loop:

1. Read prices available for the current trading date.
2. Execute orders due on that date.
3. Value the portfolio.
4. Generate strategy orders using data available through the current date.
5. Schedule orders according to the configured execution lag.
6. Record equity, drawdown, exposure, fills, risk events, and order events.

The default execution lag is one trading day to reduce lookahead risk. A zero-day lag is supported for controlled same-day simulation and should be interpreted as a modeling assumption, not live execution.

All outputs are for research and education only.
