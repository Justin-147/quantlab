# QuantLab：投资组合回测与纸面交易研究系统

QuantLab 是一个本地优先的投资组合研究项目，用于回测规则化资产配置策略、比较策略表现、模拟纸面账户，并分析回撤、波动率、夏普比率、换手率和资产暴露等风险指标。

本项目仅用于研究和教育。它不提供投资建议、交易建议、自动券商下单或收益保证。

## 能做什么

- 读取历史或合成日频价格 CSV。
- 使用合成投资组合配置。
- 运行买入并持有、定期再平衡、趋势过滤、回撤触发买入策略。
- 建模交易成本和滑点。
- 生成 JSON、Markdown、HTML 和图表报告。
- 在本地模拟纸面账户，不连接真实券商。
- 提供简单的 Streamlit Dashboard。
- 包含核心流程的 pytest 测试。

## 不做什么

QuantLab V1 不进行真实资金交易，不连接券商，不使用杠杆，不交易期权或保证金产品，不给出买卖推荐，也不声称历史表现能够预测未来收益。

## 快速开始

```powershell
cd D:\CodexWork\quantlab
python -m pip install -e .
python -m quantlab.main generate-sample-data
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv
```

如果不想安装包，也可以临时指定 `PYTHONPATH`：

```powershell
$env:PYTHONPATH="src"
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv
```

## 常用命令

生成样例数据：

```powershell
python -m quantlab.main generate-sample-data
```

运行单个回测：

```powershell
python -m quantlab.main backtest --portfolio growth_balanced --strategy periodic_rebalance --data examples/sample_data/prices_sample.csv
```

比较多个策略：

```powershell
python -m quantlab.main compare --portfolio growth_balanced --strategies buy_and_hold periodic_rebalance trend_filter --data examples/sample_data/prices_sample.csv
```

运行纸面账户模拟：

```powershell
python -m quantlab.main paper-run --portfolio growth_balanced --strategy trend_filter --data examples/sample_data/prices_sample.csv
```

启动 Dashboard：

```powershell
streamlit run src/quantlab/dashboard/app.py
```

## 策略

- `buy_and_hold`：按目标权重一次性买入并持有。
- `periodic_rebalance`：按月或按季度再平衡，并支持偏离阈值触发。
- `trend_filter`：使用移动平均线信号在风险开启和风险关闭权重之间切换。
- `drawdown_buy`：当参考资产达到回撤阈值时模拟追加买入。

## 风险指标

系统计算总收益、年化收益、年化波动率、夏普比率、索提诺比率、最大回撤、Calmar 比率、日胜率、最佳日、最差日、换手率、交易笔数和最终资产价值。

## 边界和免责声明

本项目仅用于研究和教育。它不是投资建议，不是交易建议，不提供买卖证券的推荐，不执行真实资金交易。历史表现不保证未来结果。
