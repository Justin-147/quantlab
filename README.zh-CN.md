# QuantLab：投资组合回测与本地纸面模拟研究系统

[![tests](https://github.com/Justin-147/quantlab/actions/workflows/tests.yml/badge.svg)](https://github.com/Justin-147/quantlab/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**QuantLab 仅用于研究和教育。它不是投资建议、交易建议、券商接口，也不是实盘交易机器人。**

QuantLab 是一个本地优先的投资组合研究系统，用于回测规则化资产配置策略、比较策略、模拟本地纸面账户，并分析回撤、波动率、夏普比率、换手率、资产暴露、基准跟踪、VaR 和 CVaR 等指标。

## 能做什么

- 读取并校验日频价格 CSV。
- 生成可复现的合成样例数据。
- 校验资产、组合、策略和风控配置。
- 运行买入持有、定期再平衡、趋势过滤、回撤触发买入等策略。
- 支持执行延迟、交易成本和滑点假设。
- 记录成交、订单事件、风险事件、权益曲线、回撤、暴露和基准指标。
- 生成 JSON、Markdown、HTML 和图表报告。
- 运行本地纸面模拟，券商执行始终禁用。
- 提供 Streamlit Dashboard，并通过缓存和 Fast mode 加速重复运行。

## 不做什么

QuantLab 不连接券商、不提交真实订单、不使用杠杆、不交易期权或保证金、不抓取付费数据、不保存 API key、不提供买卖推荐，也不保证收益。

## 快速开始

```powershell
cd D:\CodexWork\quantlab
python -m pip install -e .[dev]
python -m quantlab.main validate
python -m quantlab.main validate-data --data examples/sample_data/prices_sample.csv
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/demo
```

## 常用命令

生成样例数据：

```powershell
python -m quantlab.main generate-sample-data
```

校验配置和数据：

```powershell
python -m quantlab.main validate
python -m quantlab.main validate-data --data examples/sample_data/prices_sample.csv
```

运行回测：

```powershell
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/backtest
```

比较策略：

```powershell
python -m quantlab.main compare --portfolio growth_balanced --strategies buy_and_hold periodic_rebalance trend_filter --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/compare
```

运行本地纸面模拟：

```powershell
python -m quantlab.main paper-run --portfolio growth_balanced --strategy trend_filter --data examples/sample_data/prices_sample.csv --as-of 2026-07-06 --output-root .tmp/paper
```

启动 Dashboard：

```powershell
streamlit run src/quantlab/dashboard/app.py
```

Dashboard 默认启用 Fast mode。首次运行会加载数据并计算结果；相同输入再次运行时会复用缓存数据和 JSON-safe 回测结果。

## 文档

- [方法论](docs/methodology.md)
- [回测假设](docs/backtest_assumptions.md)
- [输入 Schema](docs/input_schema.md)
- [安全边界](docs/safety_boundary.md)
- [Dashboard 性能](docs/dashboard_performance.md)
- [更新日志](CHANGELOG.md)
- [路线图](docs/roadmap.md)
- [GitHub About](docs/github_about.md)

## 测试和 Demo

```powershell
pytest
python scripts/run_demo.py
```

## 免责声明

本项目仅用于研究和教育。它不是投资建议，不是交易建议，不提供买卖证券的推荐，不执行真实资金交易。历史表现不保证未来结果。
