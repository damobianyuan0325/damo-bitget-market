# damo-bitget-market

基于 Bitget 公共 API 的**行情 / 市场监控 skill**。

- Skill 名称：`damo-bitget-market`
- 功能：聚合 Bitget 上主流交易对的 24 小时行情数据，输出统一 JSON，供情报终端、早晚报、Agent 使用。
- 特点：仅使用公共接口，不需要 API Key，不读取账户、不下单，适合安全开源与复用。

---

## 功能简介

V1 版本聚焦两件事：

1. **主流交易对行情快照**（Spot + USDT 永续）
   - 使用 Bitget 公共 ticker 接口，获取：
     - `BTCUSDT`
     - `ETHUSDT`
     - `BNBUSDT`
     - `SOLUSDT`
   - 每个交易对输出两部分：
     - 现货（spot）：
       - 最新价 `last`
       - 24 小时涨跌 `change_24h`（百分比）
       - 24 小时成交额 `volume_24h`
       - 24 小时最高/最低价 `high_24h` / `low_24h`
     - USDT 永续合约（perp）：
       - 最新价 `last`
       - 24 小时涨跌 `change_24h`
       - 24 小时成交额（合约，USDT）`volume_24h`
       - 24 小时最高/最低价 `high_24h` / `low_24h`
       - 标记价 `mark_price`
       - 资金费率 `funding_rate`
       - 指数价 `index_price`

2. **统一 JSON 输出**

示例结构：

```json
{
  "generated_at": 1234567890,
  "exchange": "Bitget",
  "symbols": [
    {
      "symbol": "BTCUSDT",
      "spot": {
        "last": "67817.2",
        "change_24h": "-1.03",
        "volume_24h": "822410569.30",
        "high_24h": "68583.28",
        "low_24h": "67446.41"
      },
      "perp": {
        "last": "67810.5",
        "change_24h": "-1.01",
        "volume_24h": "4848023554.77",
        "high_24h": "68550.0",
        "low_24h": "67000.0",
        "mark_price": "67805.0",
        "funding_rate": "0.000023",
        "index_price": "67820.0"
      }
    }
  ]
}
```

后续可以扩展：

- 输出 24h 涨幅榜 / 跌幅榜 / 成交量榜等简单市场监控视图；
- 支持命令行参数查询指定交易对或 K 线数据。

---

## 安装与运行

### 1. 克隆项目

```bash
cd ~/.openclaw/workspace
# 如果还未创建目录，可直接创建
mkdir -p damo-bitget-market
cd damo-bitget-market
```

> 当前仓库已推送到 GitHub：
> https://github.com/damobianyuan0325/damo-bitget-market

将仓库克隆到你的 workspace 即可。

```bash
cd ~/.openclaw/workspace
git clone https://github.com/damobianyuan0325/damo-bitget-market.git
cd damo-bitget-market
```
### 2. 运行主脚本

```bash
python3 bitget_market.py
```

如配置正确，将在 stdout 输出一段 JSON，包含当前 Bitget 行情快照。

你可以将输出重定向至文件：

```bash
python3 bitget_market.py > bitget_market_latest.json
```

供后续脚本（如早晚报生成脚本）读取。

---

## 与 OpenClaw / 情报终端集成

在已有的 RSS + Gate 行情 + Binance 行情 + 早晚报系统中，可以这样接入：

1. 在系统 cron 中增加一步：

   ```bash
   cd ~/.openclaw/workspace/damo-bitget-market
   /usr/bin/python3 bitget_market.py > /Users/damo/.openclaw/workspace/bitget_market_latest.json
   ```

2. 在 `rss_briefing.py` 或上层简报脚本中：
   - 读取 `bitget_market_latest.json`
   - 在简报中追加一个【Bitget 行情】版块：
     - 概要描述 BTC/ETH/BNB/SOL 等主流币在 Bitget 上的表现

更多细节可以写在 `docs/setup-openclaw.md`（后续可补充）。

---

## Roadmap

- 支持更多交易对（如 ROBO、OPN 等）
- 增加 24h 涨幅榜 / 成交量榜等市场监控视图
- 支持简单 K 线查询（如 `--klines BTCUSDT --interval 1h --limit 48`）
- 输出更适合人读的 Markdown 简报格式（供直接发 Telegram / 广场）

---

## 许可证

MIT

欢迎 fork / issue / PR，一起打磨成一个通用的 Bitget 行情 skill。
