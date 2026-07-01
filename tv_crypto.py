# -*- coding: utf-8 -*-
"""Bascule la crypto sur TradingView en EUR (BTCEUR/ETHEUR/SOLEUR/HYPEEUR).
Ecrit data/{id}.json (daily EUR), tv_intraday/{id}.json (h1/h4), ichimoku/{id}.json."""
import json, os, time, datetime
import tv_client, ichimoku
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data"); TVI = os.path.join(BASE, "tv_intraday"); ICH = os.path.join(BASE, "ichimoku")
for _d in (DATA, TVI, ICH):
    os.makedirs(_d, exist_ok=True)

CRYPTO = [("BTC", "Bitcoin", "BTCEUR"), ("ETH", "Ethereum", "ETHEUR"),
          ("SOL", "Solana", "SOLEUR"), ("HYPE", "Hyperliquid", "HYPEEUR")]

for cid, name, sym in CRYPTO:
    d1 = tv_client.get_series(sym, "1D", 400)
    h4 = tv_client.get_series(sym, "240", 300)
    h1 = tv_client.get_series(sym, "60", 300)
    if not d1:
        print("MISS", cid, sym); continue
    ts, o, h, l, c, v = d1
    dates = [datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d") for t in ts]
    chg = ((c[-1] - c[-2]) / c[-2] * 100.0) if len(c) > 1 and c[-2] else None
    json.dump({"id": cid, "name": name, "sector": "Crypto", "source": "TradingView (%s)" % sym,
               "currency": "EUR", "last_date": dates[-1], "last_price": c[-1], "change_pct": chg,
               "n": len(c), "dates": dates, "open": o, "high": h, "low": l, "close": c, "volume": v},
              open(os.path.join(DATA, cid + ".json"), "w"))
    pack = lambda s: {"high": s[2], "low": s[3], "close": s[4]} if s else None
    json.dump({"id": cid, "h4": pack(h4), "h1": pack(h1)}, open(os.path.join(TVI, cid + ".json"), "w"))
    si_d1 = ichimoku.compute(h, l, c)
    si_h4 = ichimoku.compute(*[h4[i] for i in (2, 3, 4)]) if h4 else None
    si_h1 = ichimoku.compute(*[h1[i] for i in (2, 3, 4)]) if h1 else None
    setup, comment = ichimoku.classify_mtf(si_d1, si_h4, si_h1)
    json.dump({"id": cid, "name": name, "setup": setup, "comment": comment,
               "d1": si_d1, "h4": si_h4, "h1": si_h1, "notes": {"source": "TradingView"}},
              open(os.path.join(ICH, cid + ".json"), "w"), ensure_ascii=False)
    print("OK  %-5s %-8s 1D=%d 4H=%s 1H=%s last=%.2f EUR  setup=%s" % (
        cid, sym, len(c), len(h4[0]) if h4 else "-", len(h1[0]) if h1 else "-", c[-1], setup))
    time.sleep(0.3)
