# -*- coding: utf-8 -*-
"""Pull fondamentaux TradingView (scanner REST) en un POST pour tout le SBF120.
ROIC, ROE, PER, beta, secteur. Ecrit fundamentals.json {id: {...}}."""
import json, os, urllib.request
BASE = os.path.dirname(os.path.abspath(__file__))
U = json.load(open(os.path.join(BASE, "universe_sbf120.json")))

# mnemo -> id (EURONEXT:<mnemo> = id sans suffixe)
mnemo2id = {s["id"].split(".")[0]: s["id"] for s in U["stocks"]}
tickers = ["EURONEXT:" + m for m in mnemo2id]
cols = ["return_on_invested_capital", "return_on_equity", "price_earnings_ttm",
        "beta_1_year", "sector", "debt_to_equity", "operating_margin",
        "market_cap_basic", "total_debt", "effective_interest_rate_on_debt_fy"]
body = {"symbols": {"tickers": tickers}, "columns": cols}
req = urllib.request.Request("https://scanner.tradingview.com/global/scan",
                             data=json.dumps(body).encode(),
                             headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"})
d = json.loads(urllib.request.urlopen(req, timeout=25).read())
out = {}
for row in d["data"]:
    sym = row["s"]; mnemo = sym.split(":")[1]
    aid = mnemo2id.get(mnemo)
    if not aid:
        continue
    v = dict(zip(cols, row["d"]))
    out[aid] = {"roic": v["return_on_invested_capital"], "roe": v["return_on_equity"],
                "per": v["price_earnings_ttm"], "beta": v["beta_1_year"],
                "tv_sector": v["sector"], "debt_to_equity": v["debt_to_equity"],
                "op_margin": v["operating_margin"], "mcap": v["market_cap_basic"],
                "total_debt": v["total_debt"], "cost_of_debt": v["effective_interest_rate_on_debt_fy"]}
json.dump(out, open(os.path.join(BASE, "fundamentals.json"), "w"), ensure_ascii=False, indent=0)
have_roic = sum(1 for x in out.values() if isinstance(x["roic"], (int, float)))
have_per = sum(1 for x in out.values() if isinstance(x["per"], (int, float)))
have_beta = sum(1 for x in out.values() if isinstance(x["beta"], (int, float)))
print("Fondamentaux recus: %d/%d titres | ROIC=%d PER=%d beta=%d" % (len(out), len(tickers), have_roic, have_per, have_beta))
miss = [a for a in mnemo2id.values() if a not in out]
if miss: print("Sans fondamentaux:", miss)
