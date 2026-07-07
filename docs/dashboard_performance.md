# Dashboard Performance

The Streamlit dashboard is optimized for local research loops:

- Price CSV loading uses `st.cache_data`.
- Fast mode caches JSON-safe backtest results.
- Cache keys include the CSV path, file size, and modified time.
- The last successful run is stored in `st.session_state`.
- Changing filters or tabs does not automatically rerun the backtest.
- Full trade logs are limited in the UI and can be downloaded as CSV.
- Raw JSON can be downloaded for inspection outside Streamlit.

The first run may load data and build the full result. Repeating the same input set should be faster because cached data and cached backtest output are reused. Editing the CSV at the same path changes its file signature, which invalidates the cached backtest result.
