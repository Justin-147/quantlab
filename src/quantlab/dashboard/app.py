from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

SRC_ROOT = Path(__file__).resolve().parents[2]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from quantlab.backtest.engine import run_backtest  # noqa: E402
from quantlab.config import load_backtest_settings, load_portfolios, load_strategies  # noqa: E402
from quantlab.dashboard.helpers import (  # noqa: E402
    build_input_signature,
    filter_price_data,
    limit_trades,
    result_to_frames,
    safe_metric_value,
)
from quantlab.data.loader import load_price_csv  # noqa: E402
from quantlab.models import model_to_dict  # noqa: E402


def load_dashboard_data(
    path: str | Path = "examples/sample_data/prices_sample.csv",
) -> pd.DataFrame:
    return cached_price_data(str(path))


@st.cache_data(show_spinner=False)
def cached_price_data(data_path: str) -> pd.DataFrame:
    return load_price_csv(data_path)


@st.cache_data(show_spinner=False)
def cached_backtest(
    data_path: str,
    portfolio_name: str,
    strategy_name: str,
    settings_signature: str,
) -> dict[str, Any]:
    return _run_backtest_dict(data_path, portfolio_name, strategy_name, settings_signature)


def _run_backtest_dict(
    data_path: str,
    portfolio_name: str,
    strategy_name: str,
    settings_signature: str,
) -> dict[str, Any]:
    payload = json.loads(settings_signature)
    portfolios = load_portfolios()
    strategies = load_strategies()
    settings = {
        **load_backtest_settings(),
        "benchmark_symbol": payload.get("benchmark_symbol") or "SPY",
        "execution_lag_days": int(payload["execution_lag_days"]),
    }
    price_df = cached_price_data(data_path)
    start = _parse_date(payload.get("start_date"))
    end = _parse_date(payload.get("end_date"))
    if start is not None and end is not None:
        price_df = filter_price_data(price_df, start, end)
    strategy_config = {
        **strategies[strategy_name],
        "transaction_cost_bps": float(payload["transaction_cost_bps"]),
        "slippage_bps": float(payload["slippage_bps"]),
    }
    result = run_backtest(price_df, portfolios[portfolio_name], strategy_config, settings)
    return model_to_dict(result)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return pd.Timestamp(value).date()


def main() -> None:
    st.set_page_config(page_title="QuantLab", layout="wide")
    st.title("QuantLab")

    portfolios = load_portfolios()
    strategies = load_strategies()
    settings = load_backtest_settings()
    data_path = st.sidebar.text_input("Price CSV", "examples/sample_data/prices_sample.csv")
    fast_mode = st.sidebar.checkbox("Fast mode", value=True)
    price_df = load_dashboard_data(data_path)
    min_date = pd.to_datetime(price_df["date"]).min().date()
    max_date = pd.to_datetime(price_df["date"]).max().date()

    portfolio_name = st.sidebar.selectbox("Portfolio", list(portfolios.keys()))
    strategy_name = st.sidebar.selectbox("Strategy", list(strategies.keys()))
    benchmark = st.sidebar.selectbox("Benchmark", sorted(price_df["symbol"].unique()), index=0)
    selected_range = st.sidebar.date_input("Date range", (min_date, max_date))
    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date, end_date = min_date, max_date
    execution_lag_days = st.sidebar.number_input(
        "Execution lag days",
        min_value=0,
        max_value=10,
        value=int(settings.get("execution_lag_days", 1)),
        step=1,
    )
    transaction_cost_bps = st.sidebar.slider(
        "Transaction cost bps",
        0,
        50,
        int(settings.get("default_transaction_cost_bps", 5)),
    )
    slippage_bps = st.sidebar.slider(
        "Slippage bps",
        0,
        50,
        int(settings.get("default_slippage_bps", 5)),
    )
    input_signature = build_input_signature(
        portfolio_name=portfolio_name,
        strategy_name=strategy_name,
        data_path=data_path,
        execution_lag_days=int(execution_lag_days),
        transaction_cost_bps=float(transaction_cost_bps),
        slippage_bps=float(slippage_bps),
        start_date=start_date,
        end_date=end_date,
        benchmark_symbol=benchmark,
    )

    run_clicked = st.sidebar.button("Run Backtest", type="primary")
    if run_clicked:
        with st.spinner("Running backtest..."):
            if fast_mode:
                result_dict = cached_backtest(
                    data_path,
                    portfolio_name,
                    strategy_name,
                    input_signature,
                )
            else:
                result_dict = _run_backtest_dict(
                    data_path,
                    portfolio_name,
                    strategy_name,
                    input_signature,
                )
        st.session_state["last_result"] = result_dict
        st.session_state["last_inputs"] = input_signature
        st.success("Backtest completed.")

    last_result = st.session_state.get("last_result")
    if not isinstance(last_result, dict):
        st.info("Run a backtest to view results.")
        return
    if st.session_state.get("last_inputs") != input_signature:
        st.warning("Inputs changed. Run Backtest to refresh.")

    _render_result(last_result, fast_mode)


def _render_result(result: dict[str, Any], fast_mode: bool) -> None:
    metrics = result.get("metrics", {})
    frames = result_to_frames(result)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Value", safe_metric_value({"x": result.get("final_value")}, "x"))
    col2.metric("Annualized Return", safe_metric_value(metrics, "annualized_return", percent=True))
    col3.metric("Max Drawdown", safe_metric_value(metrics, "max_drawdown", percent=True))
    col4.metric("Trades", safe_metric_value(metrics, "number_of_trades"))

    if fast_mode:
        overview_tab, equity_tab, drawdown_tab, raw_tab = st.tabs(
            ["Overview", "Equity", "Drawdown", "Raw JSON"]
        )
        _render_overview(overview_tab, frames)
        _render_equity(equity_tab, frames)
        _render_drawdown(drawdown_tab, frames)
        _render_raw_json(raw_tab, result)
        return

    (
        overview_tab,
        equity_tab,
        drawdown_tab,
        weights_tab,
        trades_tab,
        risk_tab,
        raw_tab,
    ) = st.tabs(["Overview", "Equity", "Drawdown", "Weights", "Trades", "Risk Events", "Raw JSON"])
    _render_overview(overview_tab, frames)
    _render_equity(equity_tab, frames)
    _render_drawdown(drawdown_tab, frames)
    _render_weights(weights_tab, frames)
    _render_trades(trades_tab, frames, max_rows=200)
    _render_risk_events(risk_tab, frames)
    _render_raw_json(raw_tab, result)


def _render_overview(tab: Any, frames: dict[str, pd.DataFrame]) -> None:
    with tab:
        _render_equity_chart(frames["equity"])
        _render_drawdown_chart(frames["drawdown"])
        if not frames["metrics"].empty:
            st.dataframe(frames["metrics"], width="stretch", hide_index=True)


def _render_equity(tab: Any, frames: dict[str, pd.DataFrame]) -> None:
    with tab:
        _render_equity_chart(frames["equity"])


def _render_drawdown(tab: Any, frames: dict[str, pd.DataFrame]) -> None:
    with tab:
        _render_drawdown_chart(frames["drawdown"])


def _render_weights(tab: Any, frames: dict[str, pd.DataFrame]) -> None:
    with tab:
        exposures = frames["weights"]
        weight_cols = [col for col in exposures.columns if col.startswith("weight_")]
        if exposures.empty or not weight_cols:
            st.write("No weights available.")
            return
        st.line_chart(exposures.set_index("date")[weight_cols], width="stretch")


def _render_trades(tab: Any, frames: dict[str, pd.DataFrame], max_rows: int) -> None:
    with tab:
        trades = frames["trades"]
        if trades.empty:
            st.write("No fills generated.")
            return
        visible_trades = limit_trades(trades, max_rows=max_rows)
        st.dataframe(visible_trades, width="stretch", hide_index=True)
        st.download_button(
            "Download trades CSV",
            data=trades.to_csv(index=False).encode("utf-8"),
            file_name="quantlab_trades.csv",
            mime="text/csv",
        )


def _render_risk_events(tab: Any, frames: dict[str, pd.DataFrame]) -> None:
    with tab:
        risk_events = frames["risk_events"]
        order_events = frames["order_events"]
        if risk_events.empty and order_events.empty:
            st.write("No risk or order events generated.")
            return
        if not risk_events.empty:
            st.subheader("Risk Events")
            st.dataframe(risk_events, width="stretch", hide_index=True)
        if not order_events.empty:
            st.subheader("Order Events")
            st.dataframe(order_events, width="stretch", hide_index=True)


def _render_raw_json(tab: Any, result: dict[str, Any]) -> None:
    with tab:
        payload = json.dumps(result, indent=2, sort_keys=True)
        st.download_button(
            "Download result JSON",
            data=payload.encode("utf-8"),
            file_name="quantlab_backtest_result.json",
            mime="application/json",
        )
        st.json(result)


def _render_equity_chart(equity: pd.DataFrame) -> None:
    if equity.empty:
        st.write("No equity data available.")
        return
    st.line_chart(equity.set_index("date")["total_value"], width="stretch")


def _render_drawdown_chart(drawdown: pd.DataFrame) -> None:
    if drawdown.empty:
        st.write("No drawdown data available.")
        return
    st.area_chart(drawdown.set_index("date")["drawdown"], width="stretch")


if __name__ == "__main__":
    main()
