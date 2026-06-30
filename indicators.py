import json, os, glob
import numpy as np, pandas as pd
import ichimoku as ICH

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

def wilder_rma(s, n):
    return s.ewm(alpha=1.0 / n, adjust=False).mean()

def compute(d):
    close = pd.Series([x for x in d["close"]], dtype="float64")
    vol = pd.Series([(np.nan if x is None else x) for x in d["volume"]], dtype="float64")
    has_ohlc = d.get("ohlc_available", True) and d["high"][-1] is not None
    out = {}
    # Moving averages
    mm20 = close.rolling(20).mean(); mm50 = close.rolling(50).mean(); mm200 = close.rolling(200).mean()
    mm30 = close.rolling(30).mean(); mm120 = close.rolling(120).mean()
    c = float(close.iloc[-1])
    out["mm20"] = float(mm20.iloc[-1]); out["mm50"] = float(mm50.iloc[-1]); out["mm200"] = float(mm200.iloc[-1])
    out["mm30"] = float(mm30.iloc[-1]) if not np.isnan(mm30.iloc[-1]) else None
    out["mm120"] = float(mm120.iloc[-1]) if not np.isnan(mm120.iloc[-1]) else None
    # RSI(14) Wilder
    delta = close.diff()
    gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
    rs = wilder_rma(gain, 14) / wilder_rma(loss, 14)
    rsi = 100 - 100 / (1 + rs)
    out["rsi"] = float(rsi.iloc[-1])
    # MACD 12/26/9
    ema12 = close.ewm(span=12, adjust=False).mean(); ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26; signal = macd.ewm(span=9, adjust=False).mean(); hist = macd - signal
    out["macd"] = float(macd.iloc[-1]); out["macd_signal"] = float(signal.iloc[-1]); out["macd_hist"] = float(hist.iloc[-1])
    # Bollinger 20,2
    std20 = close.rolling(20).std(ddof=0)
    upper = mm20 + 2 * std20; lower = mm20 - 2 * std20
    out["boll_up"] = float(upper.iloc[-1]); out["boll_low"] = float(lower.iloc[-1])
    rng = float(upper.iloc[-1] - lower.iloc[-1])
    out["boll_pctb"] = float((c - lower.iloc[-1]) / rng) if rng else None
    out["boll_bw"] = float(rng / mm20.iloc[-1] * 100) if mm20.iloc[-1] else None
    # Volume relative
    vsma20 = vol.rolling(20).mean()
    out["vol_rel"] = float(vol.iloc[-1] / vsma20.iloc[-1]) if (vsma20.iloc[-1] and not np.isnan(vsma20.iloc[-1])) else None
    # ATR + ADX (need OHLC)
    if has_ohlc:
        high = pd.Series([x for x in d["high"]], dtype="float64")
        low = pd.Series([x for x in d["low"]], dtype="float64")
        prev_close = close.shift(1)
        tr = pd.concat([(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
        atr = wilder_rma(tr, 14)
        out["atr"] = float(atr.iloc[-1]); out["atr_pct"] = float(atr.iloc[-1] / c * 100)
        up_move = high.diff(); down_move = -low.diff()
        plus_dm = ((up_move > down_move) & (up_move > 0)) * up_move
        minus_dm = ((down_move > up_move) & (down_move > 0)) * down_move
        atrw = wilder_rma(tr, 14)
        plus_di = 100 * wilder_rma(plus_dm, 14) / atrw
        minus_di = 100 * wilder_rma(minus_dm, 14) / atrw
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = wilder_rma(dx, 14)
        out["adx"] = float(adx.iloc[-1]); out["plus_di"] = float(plus_di.iloc[-1]); out["minus_di"] = float(minus_di.iloc[-1])
    else:
        out["atr"] = None; out["atr_pct"] = None; out["adx"] = None; out["plus_di"] = None; out["minus_di"] = None
    out["close"] = c
    try:
        out["ich"] = ICH.compute(d["high"], d["low"], d["close"]) if has_ohlc else None
    except Exception:
        out["ich"] = None
    return out

def tech_score(o):
    """Regle deterministe. Score signe s in [-100,+100] -> 0..100. Ichimoku 1D inclus (option 1).
    Grille (somme +-100): Tendance MM 30 | Ichimoku 1D 20 | RSI 18 | MACD 18 | ADX 8 | Bollinger 6."""
    c = o["close"]; trace = []
    s = 0.0
    # A. Tendance MM (+-30)
    a = 0
    a += 11 if c > o["mm200"] else -11
    a += 6 if c > o["mm50"] else -6
    a += 4 if c > o["mm20"] else -4
    a += 5 if o["mm50"] > o["mm200"] else -5
    a += 4 if o["mm20"] > o["mm50"] else -4
    s += a; trace.append(("Tendance (MM)", a, 30))
    # B. RSI (+-18)
    r = o["rsi"]
    if r >= 70: b = 5
    elif r >= 55: b = 18
    elif r >= 50: b = 9
    elif r >= 45: b = -9
    elif r >= 30: b = -14
    else: b = -7
    s += b; trace.append(("Momentum RSI", b, 18))
    # C. MACD (+-18)
    cc = (9 if o["macd_hist"] > 0 else -9) + (9 if o["macd"] > 0 else -9)
    s += cc; trace.append(("MACD", cc, 18))
    # F. Ichimoku 1D (+-20) : prix/nuage 8, Tenkan/Kijun 4, nuage futur 4, Chikou 4
    ich = o.get("ich"); ich_av = ich is not None
    if ich_av:
        ff = 0
        ff += 8 if ich["pos"] == "above" else (-8 if ich["pos"] == "below" else 0)
        ff += 4 if ich["tk"] == "bull" else (-4 if ich["tk"] == "bear" else 0)
        ff += 4 if ich["future"] == "bull" else (-4 if ich["future"] == "bear" else 0)
        ff += 4 if ich["chikou"] == "bull" else -4
        s += ff; trace.append(("Ichimoku 1D", ff, 20))
    else:
        trace.append(("Ichimoku 1D", 0, 20, "indisponible"))
    # D. Force tendance ADX (+-8)
    if o["adx"] is None:
        adx_av = False; trace.append(("ADX (force)", 0, 8, "indisponible"))
    else:
        adx_av = True; direction = 1 if c > o["mm50"] else -1
        if o["adx"] >= 25: dd = 8 * direction
        elif o["adx"] >= 20: dd = 4 * direction
        else: dd = 0
        s += dd; trace.append(("ADX (force)", dd, 8))
    # E. Bollinger %B (+-6)
    pb = o["boll_pctb"]
    if pb is None: ee = 0
    elif pb > 1: ee = 2
    elif pb >= 0.5: ee = 6
    elif pb >= 0: ee = -6
    else: ee = -2
    s += ee; trace.append(("Bollinger %B", ee, 6))
    # Normalisation dynamique selon composantes disponibles
    max_abs = 100 - (0 if adx_av else 8) - (0 if ich_av else 20)
    s_norm = max(-100, min(100, s / max_abs * 100))
    score = round((s_norm + 100) / 2)
    # Filtre de regime MM30/MM120 : achat valide seulement si MM30>MM120 ; vente si MM30<MM120
    mm30 = o.get("mm30"); mm120 = o.get("mm120")
    if mm30 is None or mm120 is None:
        regime = "n/d"
    elif mm30 > mm120:
        regime = "haussier"
    elif mm30 < mm120:
        regime = "baissier"
    else:
        regime = "neutre"
    filtered = False
    if regime in ("haussier", "baissier", "neutre"):
        if score > 55 and regime != "haussier":
            filtered = True; score = round(50 + (score - 50) * 0.4)
        elif score < 45 and regime != "baissier":
            filtered = True; score = round(50 + (score - 50) * 0.4)
    return score, trace, regime, filtered

def trend_label(o):
    c = o["close"]
    above = sum([c > o["mm20"], c > o["mm50"], c > o["mm200"]])
    aligned_up = o["mm20"] > o["mm50"] > o["mm200"]
    aligned_dn = o["mm20"] < o["mm50"] < o["mm200"]
    if above == 3 and aligned_up: return "Haussier fort"
    if above >= 2: return "Haussier"
    if above == 0 and aligned_dn: return "Baissier fort"
    if above <= 1: return "Baissier"
    return "Neutre"

results = {}
for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
    d = json.load(open(f))
    aid = d["id"]
    if "error" in d:
        results[aid] = {"id": aid, "name": d.get("name"), "sector": d.get("sector"), "status": "indisponible", "cause": d["error"]}
        continue
    try:
        ind = compute(d)
        sc, trace, regime, filtered = tech_score(ind)
        results[aid] = {"id": aid, "name": d["name"], "sector": d["sector"], "source": d["source"],
                        "currency": d["currency"], "status": "ok", "last_date": d["last_date"],
                        "last_price": d["last_price"], "change_pct": d["change_pct"],
                        "indicators": ind, "tech_score": sc, "tech_trace": trace, "trend": trend_label(ind),
                        "regime": regime, "tech_filtered": filtered, "cg_change_24h": d.get("cg_change_24h")}
    except Exception as e:
        results[aid] = {"id": aid, "name": d.get("name"), "sector": d.get("sector"), "status": "indisponible", "cause": "calc: " + str(e)[:100]}

json.dump(results, open(os.path.join(BASE, "scored_tech.json"), "w"), indent=1)
ok = [r for r in results.values() if r["status"] == "ok"]
print("Calcul OK: %d/%d actifs" % (len(ok), len(results)))
print("%-26s %-22s %6s %5s  %s" % ("Actif", "Secteur", "Tech", "RSI", "Tendance"))
for r in sorted(ok, key=lambda x: -x["tech_score"]):
    print("%-26s %-22s %6d %5.0f  %s" % (r["name"][:26], r["sector"][:22], r["tech_score"], r["indicators"]["rsi"], r["trend"]))
bad = [r for r in results.values() if r["status"] != "ok"]
if bad: print("Indisponibles:", [(r["id"], r.get("cause")) for r in bad])
