# -*- coding: utf-8 -*-
"""Recalcule l'Ichimoku MTF des ACTIONS sur les bougies TradingView (daily data/ + intraday tv_intraday/).
Les fichiers crypto (ichimoku/{BTC..}) restent inchanges."""
import json, os
import ichimoku
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data"); TVI = os.path.join(BASE, "tv_intraday"); ICH = os.path.join(BASE, "ichimoku")
os.makedirs(ICH, exist_ok=True)
U = json.load(open(os.path.join(BASE, "universe_sbf120.json")))

n = 0
from collections import Counter
cnt = Counter()
for s in U["stocks"]:
    aid = s["id"]
    d = json.load(open(os.path.join(DATA, aid + ".json")))
    if "error" in d:
        continue
    si_d1 = ichimoku.compute(d["high"], d["low"], d["close"])
    si_h4 = si_h1 = None
    tip = os.path.join(TVI, aid + ".json")
    if os.path.exists(tip):
        t = json.load(open(tip))
        if t.get("h4"): si_h4 = ichimoku.compute(t["h4"]["high"], t["h4"]["low"], t["h4"]["close"])
        if t.get("h1"): si_h1 = ichimoku.compute(t["h1"]["high"], t["h1"]["low"], t["h1"]["close"])
    setup, comment = ichimoku.classify_mtf(si_d1, si_h4, si_h1)
    out = {"id": aid, "name": s["name"], "setup": setup, "comment": comment,
           "d1": si_d1, "h4": si_h4, "h1": si_h1, "notes": {"source": "TradingView"}}
    json.dump(out, open(os.path.join(ICH, aid + ".json"), "w"), ensure_ascii=False)
    cnt[setup] += 1; n += 1

print("Ichimoku TV recalcule sur %d actions" % n)
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    print("  %-30s %d" % (k, v))
