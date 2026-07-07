from __future__ import annotations

from quantlab.data.loader import get_price_matrix, load_price_csv
from quantlab.data.sample_data import SYMBOLS, generate_sample_prices


def test_sample_data_loads(tmp_path):
    csv_path = tmp_path / "prices_sample.csv"
    generate_sample_prices(csv_path)
    df = load_price_csv(csv_path)
    assert not df.empty
    assert set(SYMBOLS).issubset(set(df["symbol"]))


def test_price_matrix_has_expected_symbols(tmp_path):
    csv_path = tmp_path / "prices_sample.csv"
    generate_sample_prices(csv_path)
    matrix = get_price_matrix(load_price_csv(csv_path))
    assert set(SYMBOLS).issubset(set(matrix.columns))
