#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal Bitget market intel snapshot.

V1: fetch 24h ticker for a few core symbols using Bitget public REST API.

Usage:
    python3 bitget_market.py

Outputs JSON to stdout, e.g.:
{
  "generated_at": 1772903371,
  "exchange": "Bitget",
  "spot": [
    {"symbol": "BTCUSDT", ...},
    {"symbol": "ETHUSDT", ...}
  ]
}
"""

import json
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "https://api.bitget.com"  # Bitget public API base

# 默认监控的交易对，可按需扩展
SPOT_SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
]


def fetch_24h_ticker(symbol: str) -> dict:
    """Fetch 24h ticker for a symbol from Bitget public API.

    Bitget v2 spot ticker endpoint 返回全部现货 ticker：
    GET /api/v2/spot/market/tickers

    这里先一次性拉全量，然后在本地按 symbol 过滤，避免单个 symbol
    URL 404 之类的问题。
    """
    url = f"{BASE_URL}/api/v2/spot/market/tickers"

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
        payload = json.loads(data)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore") if e.fp else ""
        err = f"HTTP {e.code}: {detail}"
        print(f"[ERR] Failed to fetch tickers for {symbol}: {err}", file=sys.stderr)
        return {"symbol": symbol, "error": err}
    except Exception as e:  # noqa: BLE001
        err = str(e)
        print(f"[ERR] Failed to fetch tickers for {symbol}: {err}", file=sys.stderr)
        return {"symbol": symbol, "error": err}

    if payload.get("code") != "00000":
        msg = payload.get("msg")
        print(
            f"[ERR] Bitget API error for {symbol}: code={payload.get('code')} msg={msg}",
            file=sys.stderr,
        )
        return {"symbol": symbol, "error": f"api_error:{payload.get('code')}"}

    data_list = payload.get("data") or []
    # Bitget v2 tickers 中字段含义：
    # {
    #   "symbol":"BTCUSDT",
    #   "lastPr":"67817.2",
    #   "high24h":"68583.28",
    #   "low24h":"67446.41",
    #   "quoteVolume":"822410569.30",
    #   "change24h":"-1.03",
    #   ...
    # }
    row = None
    for d in data_list:
        if d.get("symbol") == symbol:
            row = d
            break

    if row is None:
        return {"symbol": symbol, "error": "symbol_not_found"}

    return {
        "symbol": row.get("symbol", symbol),
        "last": row.get("lastPr"),
        "change_24h": row.get("change24h"),
        "volume_24h": row.get("quoteVolume"),
        "high_24h": row.get("high24h"),
        "low_24h": row.get("low24h"),
    }

    if payload is None:
        print(f"[ERR] Failed to fetch {symbol}: {last_error}", file=sys.stderr)
        return {"symbol": symbol, "error": last_error or "request_failed"}

    # Bitget v2 ticker 返回结构大致为：
    # {
    #   "code":"00000",
    #   "msg":"success",
    #   "requestTime": 1700000000000,
    #   "data":[{
    #       "symbol":"BTCUSDT_SPBL",
    #       "close":"67817.2",
    #       "high24h":"68583.28",
    #       "low24h":"67446.41",
    #       "quoteVol24h":"822410569.30",
    #       "change24h":"-1.03",
    #       ...
    #   }]
    # }
    if payload.get("code") != "00000":
        msg = payload.get("msg")
        print(
            f"[ERR] Bitget API error for {symbol}: code={payload.get('code')} msg={msg}",
            file=sys.stderr,
        )
        return {"symbol": symbol, "error": f"api_error:{payload.get('code')}"}

    data_list = payload.get("data") or []
    if not data_list:
        return {"symbol": symbol, "error": "no_data"}

    d = data_list[0]

    return {
        "symbol": d.get("symbol", symbol),
        "last": d.get("close"),
        "change_24h": d.get("change24h"),
        "volume_24h": d.get("quoteVol24h"),
        "high_24h": d.get("high24h"),
        "low_24h": d.get("low24h"),
    }


def main() -> None:
    spot = []
    for sym in SPOT_SYMBOLS:
        spot.append(fetch_24h_ticker(sym))

    result = {
        "generated_at": int(time.time()),
        "exchange": "Bitget",
        "spot": spot,
    }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
