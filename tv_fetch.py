# -*- coding: utf-8 -*-
"""Pull des courbes TradingView (1D/4h/1h) pour les actions SBF120.
Ecrit data/{id}.json (daily, schema commun) + tv_intraday/{id}.json (h1/h4). Crypto non concerne."""
import json, os, sys, time, datetime
import tv_client
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data"); TVI = os.path.join(BASE, "tv_intraday")
os.makedirs(TVI, exist_ok=True)
U = json.load(open(os.path.join(BASE, "universe_sbf120.json")))
STOCKS = U["stocks"]

TV_OVERRIDE = {}  # id -> symbole TV si different de EURONEXT:<mnemo>

def tvsym(s):
    return TV_OVERRIDE.get(s["id"], "EURONEXT:" + s["id"].split(".")[0])

def to_daily_json(s, ser):
    ts, o, h, l, c, v = ser
    dates = [datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d") for t in ts]
    last = c[-1]; prev = c[-2] if len(c) > 1 else None
    chg = ((last - prev) / prev * 100.0) if prev else None
    return {"id": s["id"], "name": s["name"], "sector": s.get("macsec", s.get("sector")),
            "source": "TradingView (%s)" % tvsym(s), "currency": "EUR",
            "last_date": dates[-1], "last_price": last, "change_pct": chg, "n": len(c),
            "dates": dates, "open": o, "high": h, "low": l, "close": c, "volume": v}

def run(a, b):
    log = []
    for s in STOCKS[a:b]:
        sym = tvsym(s)
        try:
            d1 = tv_client.get_series(sym, "1D", 400)
            if not d1:
                log.append("MISS %-9s %s (1D vide) -> Yahoo conserve" % (s["id"], sym)); time.sleep(0.3); continue
            json.dump(to_daily_json(s, d1), open(os.path.join(DATA, s["id"] + ".json"), "w"))
            h4 = tv_client.get_series(sym, "240", 300)
            h1 = tv_client.get_series(sym, "60", 300)
            def pack(ser):
                if not ser: return None
                return {"high": ser[2], "low": ser[3], "close": ser[4]}
            json.dump({"id": s["id"], "h4": pack(h4), "h1": pack(h1)},
                      open(os.path.join(TVI, s["id"] + ".json"), "w"))
            log.append("OK   %-9s %-16s 1D=%d 4H=%s 1H=%s last=%.2f" % (
                s["id"], sym, d1[0].__len__(), len(h4[0]) if h4 else "-", len(h1[0]) if h1 else "-", d1[4][-1]))
        except Exception as e:
            log.append("ERR  %-9s %s %s" % (s["id"], sym, str(e)[:50]))
        time.sleep(0.3)
    print("\n".join(log))

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]))
