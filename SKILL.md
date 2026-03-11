---
name: damo-bitget-market
description: |
  使用 Bitget 公共 API 获取 BTCUSDT / ETHUSDT / BNBUSDT / SOLUSDT 等主流交易对的
  24 小时行情。仅使用公共接口，不需要 API Key，不读取账户、不下单。
metadata:
  author: damobianyuan0325
  version: "0.1.0"
license: MIT
---

# damo-bitget-market Skill

## 概览

`damo-bitget-market` 是一个只读行情 skill，用于从 Bitget 公共接口获取主流交易对
的 24 小时行情快照。

- 仅调用公共 REST API，不需要任何账户信息或 API Key。
- 不读取资产、不修改订单，适合作为安全的市场数据源。

---

## 输出字段

主脚本 `bitget_market.py` 执行时，将输出类似结构的 JSON：

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

字段说明：

- `generated_at`：Unix 时间戳（秒），表示数据生成时间。
- `exchange`：固定为 `Bitget`。
- `symbols`：数组，每个元素对应一个交易对：
  - `symbol`：交易对名称（如 `BTCUSDT`）。
  - `spot`：现货行情对象：
    - `last`：最新成交价。
    - `change_24h`：24 小时涨跌幅（百分比字符串，如 `-1.03`）。
    - `volume_24h`：24 小时成交额（以报价币计价）。
    - `high_24h`：24 小时最高价。
    - `low_24h`：24 小时最低价。
  - `perp`：USDT 永续合约行情对象：
    - `last`：最新成交价。
    - `change_24h`：24 小时涨跌幅。
    - `volume_24h`：24 小时成交额（USDT 计）。
    - `high_24h`：24 小时最高价。
    - `low_24h`：24 小时最低价。
    - `mark_price`：永续标记价。
    - `funding_rate`：当前/上一周期资金费率。
    - `index_price`：指数价，用作合理价格参考。

---

## 使用方式

在 OpenClaw 环境中：

1. 切换到 skill 目录：

   ```bash
   cd ~/.openclaw/workspace/damo-bitget-market
   ```

2. 运行脚本：

   ```bash
   python3 bitget_market.py
   ```

3. 由 Agent 解析 JSON 输出，并生成自然语言回答。例如：

> Bitget 现货行情：  
> - BTCUSDT：现价 67,817.2，24h -1.03%，成交额约 8.22 亿 USDT，高/低：68,583.28 / 67,446.41  
> - ETHUSDT：现价 1,979.31，24h +0.35%，成交额约 4.15 亿 USDT，高/低：1,996.04 / 1,955.95

可以在对话中约定口令，例如：

- “虾叔，看下 Bitget 上 BTC 和 ETH 的价格。”
- “虾叔，给我一个 Bitget 四大主流币的快照。”

---

## 安全说明

- 不需要提供 API Key 或账户信息。
- 不会执行下单、撤单、转账等任何账户相关操作。
- 仅访问 Bitget 公共行情接口，作为信息参考使用。
