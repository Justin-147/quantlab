from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

SRC_ROOT = Path(__file__).resolve().parents[2]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from quantlab.backtest.engine import run_backtest
from quantlab.config import load_backtest_settings, load_portfolios, load_strategies
from quantlab.data.loader import load_price_csv


st.set_page_config(page_title="QuantLab", layout="wide")
st.title("QuantLab")

portfolios = load_portfolios()
strategies = load_strategies()
portfolio_name = st.sidebar.selectbox("Portfolio", list(portfolios.keys()))
strategy_name = st.sidebar.selectbox("Strategy", list(strategies.keys()))
data_path = st.sidebar.text_input("Price CSV", "examples/sample_data/prices_sample.csv")

if st.sidebar.button("Run Backtest", type="primary"):
    price_df = load_price_csv(data_path)
    result = run_backtest(
        price_df,
        portfolios[portfolio_name],
        strategies[strategy_name],
        load_backtest_settings(),
    )
    metrics = pd.DataFrame([result.metrics]).T.rename(columns={0: "value"})
    equity = pd.DataFrame(result.equity_curve)
    equity["date"] = pd.to_datetime(equity["date"])
    drawdown = pd.DataFrame(result.drawdown_curve)
    drawdown["date"] = pd.to_datetime(drawdown["date"])
    exposures = pd.DataFrame(result.exposures)
    exposures["date"] = pd.to_datetime(exposures["date"])
    fills = pd.DataFrame([fill.model_dump() if hasattr(fill, "model_dump") else fill.dict() for fill in result.fills])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Value", f"{result.final_value:,.0f}")
    col2.metric("Annualized Return", f"{result.metrics['annualized_return']:.2%}")
    col3.metric("Max Drawdown", f"{result.metrics['max_drawdown']:.2%}")
    col4.metric("Trades", f"{result.metrics['number_of_trades']:.0f}")

    st.subheader("Equity Curve")
    st.line_chart(equity.set_index("date")["total_value"])

    st.subheader("Drawdown")
    st.area_chart(drawdown.set_index("date")["drawdown"])

    st.subheader("Performance Metrics")
    st.dataframe(metrics, use_container_width=True)

    st.subheader("Asset Weights")
    weight_cols = [col for col in exposures.columns if col.startswith("weight_")]
    if weight_cols:
        st.line_chart(exposures.set_index("date")[weight_cols])

    st.subheader("Trade Log")
    st.dataframe(fills, use_container_width=True)

    st.subheader("Paper Account Status")
    paper_files = sorted(Path("data/paper_accounts").glob("*.json"))
    if paper_files:
        st.write(f"Latest paper account: {paper_files[-1]}")
    else:
        st.write("No local paper account state found.")
else:
    st.info("Choose a portfolio and strategy, then run a backtest.")
