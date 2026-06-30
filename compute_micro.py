# -*- coding: utf-8 -*-
"""Note Micro (creation de valeur) : ROIC vs WACC (ROE vs cout des FP pour banques) + PER relatif au secteur.
WACC proxy = CAPM cout des fonds propres = rf + beta*ERP (rf 3%, ERP 5%, borne 6-13%). Flagge."""
import json, os, statistics
BASE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(BASE, "fundamentals.json")))
U = json.load(open(os.path.join(BASE, "universe_sbf120.json")))
MACSEC = {s["id"]: s.get("macsec") for s in U["stocks"]}
RF, ERP, TAX = 3.0, 5.0, 0.25  # taux sans risque, prime de risque actions, taux d'impot forfaitaire
WD_CAP = 0.60                  # plafond du poids de la dette (neutralise les bilans a banque captive)
BANKS = {"Banques & Assurance"}

def num(x):
    return x if isinstance(x, (int, float)) else None

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

# mediane PER par macsec (PER>0)
per_by_sec = {}
for aid, f in F.items():
    per = num(f.get("per")); sec = MACSEC.get(aid)
    if per and per > 0:
        per_by_sec.setdefault(sec, []).append(per)
sec_median_per = {s: statistics.median(v) for s, v in per_by_sec.items() if len(v) >= 2}

micro = {}
for aid, f in F.items():
    sec = MACSEC.get(aid)
    beta = num(f.get("beta")); beta_def = beta is None
    if beta is None: beta = 1.0
    Re = RF + beta * ERP  # cout des fonds propres (CAPM)
    is_bank = sec in BANKS
    mcap = num(f.get("mcap")); debt = num(f.get("total_debt")); rd = num(f.get("cost_of_debt"))
    wd = None; rd_use = None
    if is_bank:
        wacc = clamp(Re, 6.0, 14.0); wacc_method = "Coût des FP (banque/assurance)"
    elif mcap and debt and debt > 0 and mcap > 0:
        wd = min(debt / (debt + mcap), WD_CAP)
        rd_use = rd if (rd is not None and 0.3 <= rd <= 12) else (RF + 1.5)
        wacc = clamp((1 - wd) * Re + wd * rd_use * (1 - TAX), 5.0, 13.0)
        wacc_method = "WACC (capitaux propres + dette)"
    else:
        wacc = clamp(Re, 5.0, 13.0); wacc_method = "Coût des FP (dette n/d)"
    roic = num(f.get("roic")); roe = num(f.get("roe")); per = num(f.get("per"))
    metric = roe if is_bank else roic
    metric_label = "ROE vs coût des FP" if is_bank else "ROIC vs WACC"
    caveat = ""
    if is_bank: caveat = "Modèle bancaire/assurance : ROE substitué au ROIC."
    elif sec == "Immobilier": caveat = "Foncière : ROIC indicatif, peu comparable."
    spread = (metric - wacc) if metric is not None else None
    value_score = clamp(50 + spread * 5, 5, 95) if spread is not None else None
    # PER relatif secteur
    med = sec_median_per.get(sec); rel = None; val_score = None
    if per and per > 0 and med:
        rel = per / med
        val_score = clamp(50 + (1 - rel) * 60, 5, 95)
    # blend
    if value_score is not None and val_score is not None:
        note = round(0.6 * value_score + 0.4 * val_score)
    elif value_score is not None:
        note = round(value_score)
    elif val_score is not None:
        note = round(val_score)
    else:
        note = None
    micro[aid] = {"micro": note, "roic": roic, "roe": roe, "per": per, "beta": round(beta, 2),
                  "beta_default": beta_def, "wacc": round(wacc, 1), "wacc_method": wacc_method,
                  "re": round(Re, 1), "rd": round(rd_use, 1) if rd_use is not None else None,
                  "wd": round(wd, 2) if wd is not None else None, "metric": metric,
                  "metric_label": metric_label, "spread": round(spread, 1) if spread is not None else None,
                  "value_score": round(value_score) if value_score is not None else None,
                  "sector": sec, "sector_median_per": round(med, 1) if med else None,
                  "rel_per": round(rel, 2) if rel else None,
                  "val_score": round(val_score) if val_score is not None else None, "caveat": caveat}

json.dump(micro, open(os.path.join(BASE, "micro.json"), "w"), ensure_ascii=False, indent=0)
ok = [m for m in micro.values() if m["micro"] is not None]
print("Note micro calculee: %d titres (sur %d)" % (len(ok), len(micro)))
print("Medianes PER par secteur:", {k: round(v, 1) for k, v in sec_median_per.items()})
sm = sorted([(a, m["micro"], m["spread"], m["rel_per"]) for a, m in micro.items() if m["micro"] is not None], key=lambda x: -x[1])
print("Top micro:", [(a, n) for a, n, s, r in sm[:6]])
print("Bottom micro:", [(a, n) for a, n, s, r in sm[-6:]])
nd = [a for a, m in micro.items() if m["micro"] is None]
if nd: print("Micro n/d:", nd)
