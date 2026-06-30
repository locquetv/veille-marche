# -*- coding: utf-8 -*-
"""Ichimoku Kinko Hyo (9,26,52, decalage 26) + classification multi-UT.
Couche timing SEPAREE : ne modifie pas le score composite 40/30/30."""
import numpy as np, pandas as pd

T, K, B, SHIFT = 9, 26, 52, 26

def compute(high, low, close):
    """high/low/close: listes chronologiques. Retourne l'etat Ichimoku au dernier point, ou None si donnees insuffisantes."""
    h = pd.Series([np.nan if x is None else float(x) for x in high], dtype="float64")
    l = pd.Series([np.nan if x is None else float(x) for x in low], dtype="float64")
    c = pd.Series([np.nan if x is None else float(x) for x in close], dtype="float64")
    n = len(c)
    if n < B + SHIFT + 2 or h.isna().all() or l.isna().all():
        return None
    tenkan = (h.rolling(T).max() + l.rolling(T).min()) / 2
    kijun = (h.rolling(K).max() + l.rolling(K).min()) / 2
    spanA = (tenkan + kijun) / 2            # plotted +SHIFT ahead
    spanB = (h.rolling(B).max() + l.rolling(B).min()) / 2  # plotted +SHIFT ahead
    i = n - 1
    px = float(c.iloc[i])
    tk = float(tenkan.iloc[i]); kj = float(kijun.iloc[i])
    # nuage AU point courant = spanA/B calcules SHIFT barres plus tot
    sa_now = float(spanA.iloc[i - SHIFT]); sb_now = float(spanB.iloc[i - SHIFT])
    cloud_top = max(sa_now, sb_now); cloud_bot = min(sa_now, sb_now)
    # nuage FUTUR (front, i+SHIFT) = spanA/B au point courant
    sa_fut = float(spanA.iloc[i]); sb_fut = float(spanB.iloc[i])
    # position prix vs nuage
    if px > cloud_top: pos = "above"
    elif px < cloud_bot: pos = "below"
    else: pos = "inside"
    # croisement Tenkan/Kijun : recence (<=3 barres)
    diff = (tenkan - kijun)
    tk_state = "bull" if tk > kj else ("bear" if tk < kj else "flat")
    cross = None
    for back in range(1, 4):
        if i - back >= 0 and not np.isnan(diff.iloc[i]) and not np.isnan(diff.iloc[i - back]):
            if diff.iloc[i] > 0 and diff.iloc[i - back] <= 0:
                cross = "bull"; break
            if diff.iloc[i] < 0 and diff.iloc[i - back] >= 0:
                cross = "bear"; break
    future = "bull" if sa_fut > sb_fut else ("bear" if sa_fut < sb_fut else "flat")
    # Chikou (close courant vs prix il y a SHIFT)
    chikou = "bull" if px > float(c.iloc[i - SHIFT]) else "bear"
    # label synthetique de l'UT
    if pos == "above" and tk_state == "bull" and future == "bull":
        label = "Haussier"
    elif pos == "below" and tk_state == "bear" and future == "bear":
        label = "Baissier"
    elif pos == "above":
        label = "Haussier faible"
    elif pos == "below":
        label = "Baissier faible"
    else:
        label = "Dans le nuage"
    return {"px": round(px, 4), "tenkan": round(tk, 4), "kijun": round(kj, 4),
            "cloud_top": round(cloud_top, 4), "cloud_bot": round(cloud_bot, 4),
            "pos": pos, "tk": tk_state, "cross": cross, "future": future,
            "chikou": chikou, "label": label, "n": n}

# Priorite de tri des setups (du plus 'achat' au plus 'vente')
SETUP_ORDER = {"Achat aligné": 0, "Repli haussier (guet achat)": 1, "Haussier naissant": 2,
               "Neutre / indécis": 3, "Conflit multi-UT": 4, "Baissier naissant": 5,
               "Rebond baissier (guet vente)": 6, "Vente alignée": 7, "Données partielles": 8}

def classify_mtf(d1, h4, h1):
    """1D = filtre tendance, 4H = structure, 1H = declencheur. Retourne (setup, commentaire)."""
    if d1 is None:
        return "Données partielles", "1D Ichimoku indisponible (pas d'OHLC) — timing non calculable."
    dp = d1["pos"]
    h4p = h4["pos"] if h4 else None
    h1p = h1["pos"] if h1 else None
    h1cross = h1["cross"] if h1 else None
    # tendances de fond
    up = dp == "above"; down = dp == "below"
    h4up = h4p == "above"; h4down = h4p == "below"
    if up and h4up and (h1cross == "bull" or (h1p == "above" and h1 and h1["tk"] == "bull")):
        return "Achat aligné", "1D et 4H au-dessus du nuage, déclencheur 1H haussier (croisement TK / sortie de nuage)."
    if down and h4down and (h1cross == "bear" or (h1p == "below" and h1 and h1["tk"] == "bear")):
        return "Vente alignée", "1D et 4H sous le nuage, déclencheur 1H baissier."
    if up and h4up and (h1p in ("inside", "below")):
        return "Repli haussier (guet achat)", "Fond haussier (1D+4H), repli 1H dans/sous le nuage : guetter un retour au-dessus du Tenkan/nuage 1H."
    if down and h4down and (h1p in ("inside", "above")):
        return "Rebond baissier (guet vente)", "Fond baissier (1D+4H), rebond 1H : guetter un rejet sous le Tenkan/nuage 1H."
    if up and not h4down:
        return "Haussier naissant", "1D au-dessus du nuage ; 4H/1H pas encore pleinement alignés."
    if down and not h4up:
        return "Baissier naissant", "1D sous le nuage ; 4H/1H pas encore pleinement alignés."
    if (up and h4down) or (down and h4up):
        return "Conflit multi-UT", "1D et 4H en contradiction : pas de configuration d'entrée nette."
    return "Neutre / indécis", "Prix dans le nuage sur l'UT de fond : tendance indécise."
