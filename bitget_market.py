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


def fetch_spot_tickers() -> dict:
    """Fetch all spot tickers once, return dict[symbol] -> row.

    Bitget v2 spot ticker endpoint:
        GET /api/v2/spot/market/tickers
    """
    url = f"{BASE_URL}/api/v2/spot/market/tickers"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    payload = json.loads(data)
    if payload.get("code") != "00000":
        raise RuntimeError(f"spot api_error:{payload.get('code')} {payload.get('msg')}")
    result = {}
    for d in payload.get("data") or []:
        sym = d.get("symbol")
        if sym:
            result[sym] = d
    return result


def fetch_perp_tickers() -> dict:
    """Fetch USDT-margined futures tickers once, return dict[symbol] -> row.

    Bitget v2 mix ticker endpoint:
        GET /api/v2/mix/market/tickers?productType=USDT-FUTURES
    """
    url = f"{BASE_URL}/api/v2/mix/market/tickers?productType=USDT-FUTURES"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    payload = json.loads(data)
    if payload.get("code") != "00000":
        raise RuntimeError(f"perp api_error:{payload.get('code')} {payload.get('msg')}")
    result = {}
    for d in payload.get("data") or []:
        sym = d.get("symbol")
        if sym:
            result[sym] = d
    return result

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
    # 拉一次现货 & 永续 tickers
    spot_all = fetch_spot_tickers()
    perp_all = fetch_perp_tickers()

    symbols = []
    for sym in SPOT_SYMBOLS:
        spot_row = spot_all.get(sym)
        perp_row = perp_all.get(sym)

        spot = None
        if spot_row:
            spot = {
                "last": spot_row.get("lastPr"),
                "change_24h": spot_row.get("change24h"),
                "volume_24h": spot_row.get("quoteVolume"),
                "high_24h": spot_row.get("high24h"),
                "low_24h": spot_row.get("low24h"),
            }

        perp = None
        if perp_row:
            perp = {
                "last": perp_row.get("lastPr"),
                "change_24h": perp_row.get("change24h"),
                "volume_24h": perp_row.get("usdtVolume"),
                "high_24h": perp_row.get("high24h"),
                "low_24h": perp_row.get("low24h"),
                "mark_price": perp_row.get("markPrice"),
                "funding_rate": perp_row.get("fundingRate"),
                "index_price": perp_row.get("indexPrice"),
            }

        symbols.append({
            "symbol": sym,
            "spot": spot or {"error": "no_spot_data"},
            "perp": perp or {"error": "no_perp_data"},
        })

    result = {
        "generated_at": int(time.time()),
        "exchange": "Bitget",
        "symbols": symbols,
    }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
