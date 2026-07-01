# -*- coding: utf-8 -*-
import json, os, io, base64, datetime, html, glob
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import analysis_data as A
import ichimoku as ICHMOD

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
W = {"tech": 50, "sent": 15, "macro": 15, "micro": 20}

tech = json.load(open(os.path.join(BASE, "scored_tech.json")))
MICRO = json.load(open(os.path.join(BASE, "micro.json"))) if os.path.exists(os.path.join(BASE, "micro.json")) else {}

# --- Contexte dynamique (sentiment/macro rafraichis par LLM, optionnel) ---
import copy as _copy
DYN = {}
_dp = os.path.join(BASE, "dynamic_context.json")
if os.path.exists(_dp):
    try:
        DYN = json.load(open(_dp))
    except Exception:
        DYN = {}
DYN_ON = bool(DYN.get("sentiment") or DYN.get("macro_today") or DYN.get("macro_sectors"))
DYN_DATE = DYN.get("generated_at", "")
MACRO_TODAY_USED = dict(A.MACRO_TODAY); MACRO_TODAY_USED.update(DYN.get("macro_today") or {})
MACRO_SECTORS_USED = _copy.deepcopy(A.MACRO_SECTORS)
for _s, _v in (DYN.get("macro_sectors") or {}).items():
    if _s in MACRO_SECTORS_USED and isinstance(_v, dict):
        if isinstance(_v.get("score"), (int, float)): MACRO_SECTORS_USED[_s]["score"] = int(_v["score"])
        if _v.get("rat"): MACRO_SECTORS_USED[_s]["rat"] = _v["rat"]
SENT_DYN = DYN.get("sentiment") or {}
uni = json.load(open(os.path.join(BASE, "universe_sbf120.json")))
NAME = {}; MACSEC = {}
for s in uni["stocks"]:
    NAME[s["id"]] = s; MACSEC[s["id"]] = s.get("macsec")
for c in uni["crypto"]:
    NAME[c["id"]] = c; MACSEC[c["id"]] = "Crypto"
CRYPTO_IDS = {c["id"] for c in uni["crypto"]}
ICH = {}
for f in glob.glob(os.path.join(BASE, "ichimoku", "*.json")):
    j = json.load(open(f)); ICH[j["id"]] = j

CHART_IDS = ["BTC","ETH","SOL","HYPE","MC.PA","RMS.PA","KER.PA","TTE.PA","AIR.PA","SAF.PA","HO.PA",
             "SAN.PA","BNP.PA","GLE.PA","STMPA.PA","SU.PA","STLAP.PA","RNO.PA"]

def grad(v):
    """0=rouge 50=ambre 100=vert -> (bg hex, text hex)."""
    if v is None:
        return ("#2a2f45", "#8b93ad")
    v = max(0, min(100, v))
    hue = v / 100.0 * 130.0
    import colorsys
    r, g, b = colorsys.hls_to_rgb(hue/360.0, 0.34, 0.62)
    return ("#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255)), "#ffffff")

def wilder(s, n):
    return s.ewm(alpha=1.0/n, adjust=False).mean()

def make_chart(aid):
    d = json.load(open(os.path.join(DATA, aid + ".json")))
    close = pd.Series([float(x) for x in d["close"]])
    dates = pd.to_datetime(d["dates"])
    mm20 = close.rolling(20).mean(); mm50 = close.rolling(50).mean(); mm200 = close.rolling(200).mean()
    mm120 = close.rolling(120).mean()
    has_ohlc = d.get("high", [None])[-1] is not None
    if has_ohlc:
        hh = pd.Series([np.nan if x is None else float(x) for x in d["high"]])
        ll = pd.Series([np.nan if x is None else float(x) for x in d["low"]])
        ich_tenkan = (hh.rolling(9).max() + ll.rolling(9).min()) / 2
        ich_kijun = (hh.rolling(26).max() + ll.rolling(26).min()) / 2
        ich_spanA = ((ich_tenkan + ich_kijun) / 2).shift(26)
        ich_spanB = ((hh.rolling(52).max() + ll.rolling(52).min()) / 2).shift(26)
    delta = close.diff(); gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
    rsi = 100 - 100/(1 + wilder(gain,14)/wilder(loss,14))
    n = min(252, len(close)); sl = slice(len(close)-n, len(close))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 4.4), height_ratios=[3,1], sharex=True)
    fig.patch.set_facecolor("#0f1320")
    for ax in (ax1, ax2):
        ax.set_facecolor("#161b2e")
        ax.tick_params(colors="#8b93ad", labelsize=8)
        for sp in ax.spines.values(): sp.set_color("#2a2f45")
        ax.grid(True, color="#222840", lw=0.5)
    ax1.plot(dates[sl], close[sl], color="#e8ebf5", lw=1.2, label="Cours")
    ax1.plot(dates[sl], mm20[sl], color="#28c2d6", lw=0.9, label="MM20")
    ax1.plot(dates[sl], mm50[sl], color="#f0a13a", lw=0.9, label="MM50")
    ax1.plot(dates[sl], mm120[sl], color="#9b8cff", lw=0.9, label="MM120")
    ax1.plot(dates[sl], mm200[sl], color="#d471d4", lw=0.9, label="MM200")
    if has_ohlc:
        x = dates[sl]; a = ich_spanA[sl]; b = ich_spanB[sl]
        ax1.fill_between(x, a, b, where=(a >= b), color="#3aa76d", alpha=0.18, linewidth=0)
        ax1.fill_between(x, a, b, where=(a < b), color="#d9534f", alpha=0.18, linewidth=0)
        ax1.plot(x, ich_kijun[sl], color="#f5d442", lw=0.8, label="Kijun")
    cur = d["currency"]
    ax1.set_title("%s  (%s)" % (d["name"], aid), color="#e8ebf5", fontsize=11, loc="left")
    ax1.legend(fontsize=8, facecolor="#161b2e", edgecolor="#2a2f45", labelcolor="#cfd4e6", ncol=6, loc="upper left")
    ax2.plot(dates[sl], rsi[sl], color="#7c5cff", lw=0.9)
    ax2.axhline(70, color="#d9534f", lw=0.5, ls="--"); ax2.axhline(30, color="#3aa76d", lw=0.5, ls="--")
    ax2.set_ylim(0, 100); ax2.set_ylabel("RSI", color="#8b93ad", fontsize=9)
    fig.tight_layout(pad=0.4)
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor()); plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

# ---- Build per-asset records ----
rows = []
unavailable = []
for aid, t in tech.items():
    if t.get("status") != "ok":
        unavailable.append((aid, t.get("name"), t.get("cause"))); continue
    macsec = MACSEC.get(aid) or A.ASSET_MACRO_SECTOR.get(aid)
    if aid in SENT_DYN and isinstance(SENT_DYN[aid], dict) and isinstance(SENT_DYN[aid].get("score"), (int, float)):
        sent = dict(SENT_DYN[aid]); sent["sourced"] = True; sent["dynamic"] = True
        sent.setdefault("points", [])
    elif aid in A.SENTIMENT:
        sent = A.SENTIMENT[aid]
    else:
        sent = {"score": A.SECTOR_SENT_DEFAULT[macsec], "sourced": False,
                "basis": "Proxy sectoriel — %s" % macsec}
    mac = MACRO_SECTORS_USED[macsec]
    ts, ss, ms = t["tech_score"], sent["score"], mac["score"]
    mrec = MICRO.get(aid, {}); mic = mrec.get("micro")
    parts = [("tech", ts, W["tech"]), ("sent", ss, W["sent"]), ("macro", ms, W["macro"])]
    if mic is not None:
        parts.append(("micro", mic, W["micro"]))
    wsum = sum(w for _, _, w in parts)
    glob = round(sum(v * w for _, v, w in parts) / wsum)
    blocks = {"Technique": ts, "Sentiment": ss, "Macro": ms}
    if mic is not None:
        blocks["Micro"] = mic
    hi = max(blocks, key=blocks.get); lo = min(blocks, key=blocks.get)
    spread = blocks[hi] - blocks[lo]
    rows.append({"id": aid, "name": t["name"], "sector": t["sector"], "macsec": macsec,
                 "price": t["last_price"], "chg": t["change_pct"], "cur": t["currency"],
                 "tech": ts, "sent": ss, "macro": ms, "micro": mic, "micro_rec": mrec, "glob": glob,
                 "trend": t["trend"], "regime": t.get("regime"), "filtered": t.get("tech_filtered", False),
                 "sourced": sent["sourced"], "sent_rec": sent, "div": spread > 30, "spread": spread,
                 "hi": hi, "lo": lo, "rsi": t["indicators"]["rsi"]})
rows.sort(key=lambda r: -r["glob"])

run_dt = datetime.datetime.now(datetime.timezone.utc)
run_str = run_dt.strftime("%Y-%m-%d %Hh%M UTC")
fname = "veille-marche_%s_%sh%s.html" % (run_dt.strftime("%Y-%m-%d"), run_dt.strftime("%H"), run_dt.strftime("%M"))
data_date = rows[0]["id"] and tech[rows[0]["id"]]["last_date"]

def esc(x): return html.escape(str(x))
def fmt_price(p, cur):
    if p is None: return "n/d"
    return ("%.2f" % p) + (" $" if cur == "USD" else " €")
def fmt_chg(c):
    if c is None: return "<span class='muted'>n/d</span>"
    cls = "up" if c >= 0 else "dn"; sign = "+" if c >= 0 else ""
    return "<span class='%s'>%s%.2f%%</span>" % (cls, sign, c)

# ---- Executive summary stats ----
ndiv = sum(1 for r in rows if r["div"])
top5 = rows[:5]; bot5 = rows[-5:]
nsourced = sum(1 for r in rows if r["sourced"])

# ===================== HTML =====================
P = []
P.append("""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Veille Marche FR — __RUN__</title>
<style>
:root{--bg:#0b0e1a;--panel:#11162a;--panel2:#161b2e;--bd:#222840;--tx:#e8ebf5;--mut:#8b93ad;--acc:#7c5cff;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.5;font-size:14px}
.wrap{max-width:1180px;margin:0 auto;padding:22px 18px 60px}
h1{font-size:23px;margin:0 0 4px} h2{font-size:18px;margin:34px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--bd)}
h3{font-size:14px;margin:18px 0 6px;color:#cfd4e6}
a{color:#8fb6ff;text-decoration:none} a:hover{text-decoration:underline}
.muted,.mut{color:var(--mut)} .up{color:#3ed598} .dn{color:#ff6b6b}
.banner{background:linear-gradient(90deg,#3a2a12,#4a2a2a);border:1px solid #6b4a2a;border-radius:8px;padding:10px 14px;font-size:13px;color:#ffd9a8;margin:14px 0}
.meta{display:flex;flex-wrap:wrap;gap:8px 22px;color:var(--mut);font-size:12.5px;margin-bottom:6px}
.meta b{color:var(--tx)}
.card{background:var(--panel);border:1px solid var(--bd);border-radius:10px;padding:14px 16px;margin:10px 0}
.kpis{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}
.kpi{background:var(--panel2);border:1px solid var(--bd);border-radius:8px;padding:8px 12px;min-width:120px}
.kpi .n{font-size:20px;font-weight:700} .kpi .l{font-size:11px;color:var(--mut)}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{padding:6px 8px;text-align:left;border-bottom:1px solid var(--bd);white-space:nowrap}
th{color:var(--mut);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.3px}
td.r,th.r{text-align:right} .sc{font-weight:700;border-radius:5px;text-align:center;padding:3px 6px;min-width:34px;display:inline-block}
.badge{font-size:10.5px;padding:2px 6px;border-radius:10px;background:#3a2030;color:#ff9db0;border:1px solid #5a2a40}
.utc{font-size:10.5px;padding:2px 7px;border-radius:5px;white-space:nowrap;display:inline-block}
.dot{font-size:10px} .src{color:#3ed598} .px{color:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.chartcard{background:var(--panel);border:1px solid var(--bd);border-radius:10px;padding:8px}
.chartcard img{width:100%;display:block;border-radius:6px;cursor:zoom-in}
#lb{position:fixed;inset:0;background:rgba(6,8,16,.94);display:none;align-items:center;justify-content:center;z-index:2000;padding:2vh}
#lb.on{display:flex}
#lb img{max-width:96vw;max-height:88vh;border-radius:8px;box-shadow:0 12px 50px #000;cursor:zoom-out}
#lb .cap{position:fixed;top:10px;left:0;right:0;text-align:center;color:#cfd4e6;font-size:13px;pointer-events:none}
#lb .x{position:fixed;top:6px;right:18px;color:#cfd4e6;font-size:26px;cursor:pointer;line-height:1}
.chmeta{display:flex;justify-content:space-between;font-size:11.5px;padding:6px 4px 2px;color:var(--mut)}
.hm{display:grid;grid-template-columns:170px repeat(5,1fr);gap:2px;font-size:11.5px}
.hm .h{color:var(--mut);font-size:10.5px;text-transform:uppercase;padding:4px}
.hm .lab{padding:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hm .c{padding:5px 2px;text-align:center;font-weight:700;border-radius:3px}
.pt{font-size:12.5px;margin:4px 0;padding-left:10px;border-left:2px solid var(--bd)}
.pt .m{color:var(--mut);font-size:11px}
.persp{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:4px 0 12px}
.persp div{background:var(--panel2);border:1px solid var(--bd);border-radius:7px;padding:8px}
.persp .t{font-size:10.5px;color:var(--acc);text-transform:uppercase;letter-spacing:.4px;margin-bottom:3px}
.small{font-size:12px;color:var(--mut)}
.tag{display:inline-block;font-size:10px;padding:1px 6px;border-radius:8px;background:#1c2238;border:1px solid var(--bd);color:#aeb6d0;margin-left:6px}
ul.src li{margin:3px 0;font-size:12.5px}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:11.5px;color:var(--mut);margin:8px 0}
.swatch{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:middle;margin-right:4px}
@media(max-width:680px){.persp{grid-template-columns:1fr}.hm{grid-template-columns:110px repeat(5,1fr)}}
</style></head><body><div class="wrap">""".replace("__RUN__", esc(run_str)))

# Header
n_crypto = sum(1 for r in rows if r["id"] in CRYPTO_IDS)
n_stocks = len(rows) - n_crypto
P.append("<h1>Veille Marché FR — Actions SBF 120 &amp; Crypto</h1>")
P.append('<div class="meta"><span>Run : <b>%s</b></span><span>Dernière donnée marché : <b>%s</b></span><span>Univers : <b>%d actifs</b> (%d valeurs SBF 120 + %d crypto)</span><span>Pondération : <b>Technique %d / Sentiment %d / Macro %d / Micro %d</b></span></div>'
         % (esc(run_str), esc(data_date), len(rows), n_stocks, n_crypto, W["tech"], W["sent"], W["macro"], W["micro"]))
P.append('<div class="banner"><b>Agrégation de signaux publics à fin d\'information. Pas un conseil d\'investissement personnalisé. Aucune garantie de performance.</b> Les scores ne sont pas des ordres : ils structurent des signaux calculés et sourcés que vous interprétez seul.</div>')

# Exec summary
strongest_div = sorted([r for r in rows if r["div"]], key=lambda r:-r["spread"])[:4]
P.append('<div class="card"><h3 style="margin-top:0">Synthèse du run</h3>')
if DYN.get("regime_summary"):
    P.append('<div class="small">Régime macro dominant : %s</div>' % esc(DYN["regime_summary"]))
else:
    P.append('<div class="small">Régime macro dominant : <b style="color:#ffd9a8">taux en hausse</b> (BCE +25 pb le 11/06, dépôt 2,25 % ; Fed maintenue mais biais haussier), <b style="color:#ffd9a8">inflation collante</b> (zone euro 3,2 %), <b style="color:#ffd9a8">choc énergétique géopolitique</b> (Moyen-Orient, Brent ~80 $). Favorise banques, énergie, défense ; pénalise immobilier, autos, utilities, crypto.</div>')
P.append('<div class="kpis">')
P.append('<div class="kpi"><div class="n">%d/%d</div><div class="l">actifs couverts (0 indisponible)</div></div>' % (len(rows), len(rows)+len(unavailable)))
P.append('<div class="kpi"><div class="n">%d</div><div class="l">flags divergence inter-blocs &gt;30 pts</div></div>' % ndiv)
P.append('<div class="kpi"><div class="n">%d</div><div class="l">sentiments sourcés individuellement</div></div>' % nsourced)
P.append('<div class="kpi"><div class="n">%s</div><div class="l">meilleur score global (%s)</div></div>' % (top5[0]["glob"], esc(top5[0]["name"])))
P.append('<div class="kpi"><div class="n">%s</div><div class="l">plus faible score global (%s)</div></div>' % (bot5[-1]["glob"], esc(bot5[-1]["name"])))
P.append('</div>')
if strongest_div:
    P.append('<div class="small" style="margin-top:6px"><b>Divergences les plus fortes (l\'information utile) :</b> ' +
             " · ".join("%s <span class='mut'>(%s %d vs %s %d)</span>" % (esc(r["name"]), r["hi"], {"Technique":r["tech"],"Sentiment":r["sent"],"Macro":r["macro"],"Micro":r["micro"]}[r["hi"]], r["lo"], {"Technique":r["tech"],"Sentiment":r["sent"],"Macro":r["macro"],"Micro":r["micro"]}[r["lo"]]) for r in strongest_div) + '</div>')
P.append('</div>')

# Summary table
P.append('<h2>Tableau de synthèse</h2>')
P.append('<div class="legend"><span><span class="swatch" style="background:%s"></span>Achat (≥66)</span><span><span class="swatch" style="background:%s"></span>Neutre (40–65)</span><span><span class="swatch" style="background:%s"></span>Vente (&lt;40)</span><span class="src">●</span> sentiment sourcé &nbsp; <span class="px">○</span> proxy sectoriel</div>' % (grad(80)[0], grad(52)[0], grad(25)[0]))
P.append('<div style="overflow-x:auto"><table><thead><tr><th>#</th><th>Actif</th><th>Secteur (macro)</th><th class="r">Prix</th><th class="r">Var.</th><th class="r">Global</th><th class="r">Tech</th><th class="r">Sent.</th><th class="r">Macro</th><th class="r">Micro</th><th>Régime</th><th>Tendance</th><th>Diverg.</th></tr></thead><tbody>')
def cell(v):
    if v is None:
        return '<span class="sc" style="background:#2a2f45;color:#8b93ad">n/d</span>'
    bg, tx = grad(v); return '<span class="sc" style="background:%s;color:%s">%d</span>' % (bg, tx, v)
def regime_chip(reg, filtered):
    if reg == "haussier": base = '<span class="utc" style="background:#1f6b46;color:#eef">MM30&gt;120</span>'
    elif reg == "baissier": base = '<span class="utc" style="background:#6b2a2a;color:#eef">MM30&lt;120</span>'
    else: base = '<span class="utc" style="background:#2a2f45;color:#8b93ad">%s</span>' % esc(reg or "n/d")
    if filtered: base += ' <span class="badge">⚑ filtré</span>'
    return base
for i, r in enumerate(rows, 1):
    dotmark = '<span class="src">●</span>' if r["sourced"] else '<span class="px">○</span>'
    divtxt = ('<span class="badge">⚠ %s/%s</span>' % (r["hi"][:4], r["lo"][:4])) if r["div"] else '<span class="mut">—</span>'
    techcell = cell(r["tech"]) + (' <span class="badge" title="signal filtré par régime MM30/MM120">⚑</span>' if r["filtered"] else '')
    P.append('<tr><td class="mut">%d</td><td><b>%s</b> %s<br><span class="mut" style="font-size:10.5px">%s</span></td><td class="mut">%s</td><td class="r">%s</td><td class="r">%s</td><td class="r">%s</td><td class="r">%s</td><td class="r">%s</td><td class="r">%s</td><td class="r">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
             % (i, esc(r["name"]), dotmark, esc(r["id"]), esc(r["macsec"]), esc(fmt_price(r["price"], r["cur"])), fmt_chg(r["chg"]),
                cell(r["glob"]), techcell, cell(r["sent"]), cell(r["macro"]), cell(r["micro"]), regime_chip(r["regime"], r["filtered"]), esc(r["trend"]), divtxt))
P.append('</tbody></table></div>')
P.append('<div class="small" style="margin-top:6px">Tri par score global décroissant. Global = <b>Tech 50 / Sentiment 15 / Macro 15 / Micro 20</b> (renormalisé si un bloc manque, ex. crypto sans Micro). Sémantique : 100 = achat max, 50 = neutre, 0 = vente max. <b>⚑ filtré</b> = signal technique amorti car contredit par le régime MM30/MM120 (achat en régime baissier, ou vente en régime haussier). <b>Micro n/d</b> = pas de fondamentaux (crypto, ou société en perte).</div>')

# Heatmap
P.append('<h2>Heatmap des scores (actifs × blocs)</h2><div class="card">')
P.append('<div class="hm"><div class="h">Actif</div><div class="h" style="text-align:center">Tech</div><div class="h" style="text-align:center">Sent.</div><div class="h" style="text-align:center">Macro</div><div class="h" style="text-align:center">Micro</div><div class="h" style="text-align:center">Global</div>')
for r in rows:
    P.append('<div class="lab">%s</div>' % esc(r["name"]))
    for v in (r["tech"], r["sent"], r["macro"], r["micro"], r["glob"]):
        if v is None:
            P.append('<div class="c" style="background:#2a2f45;color:#8b93ad">n/d</div>')
        else:
            bg, tx = grad(v); P.append('<div class="c" style="background:%s;color:%s">%d</div>' % (bg, tx, v))
P.append('</div></div>')

# Charts
P.append('<h2>Graphes par actif majeur</h2><div class="small">Cours + MM20/MM50/MM120/MM200, <b>nuage Ichimoku (Kumo) et Kijun en journalier</b>, et RSI(14). <b>Courbes TradingView</b> : actions (EURONEXT) et crypto en EUR (BTCEUR/ETHEUR/SOLEUR/HYPEEUR), toutes UT.</div><div class="grid">')
chart_map = {}
for aid in CHART_IDS:
    try:
        chart_map[aid] = make_chart(aid)
    except Exception as e:
        chart_map[aid] = None
rec_by_id = {r["id"]: r for r in rows}
for aid in CHART_IDS:
    r = rec_by_id.get(aid); b64 = chart_map.get(aid)
    if not r or not b64: continue
    bg, tx = grad(r["glob"])
    P.append('<div class="chartcard"><img src="data:image/png;base64,%s" alt="%s">' % (b64, esc(r["name"])))
    P.append('<div class="chmeta"><span>%s · RSI %.0f · %s</span><span class="sc" style="background:%s;color:%s">Global %d</span></div></div>'
             % (esc(r["trend"]), r["rsi"], esc(fmt_price(r["price"], r["cur"])), bg, tx, r["glob"]))
P.append('</div>')

# ===== Ichimoku MTF =====
SETUP_VAL = {"Achat aligné":85,"Repli haussier (guet achat)":66,"Haussier naissant":60,
             "Neutre / indécis":50,"Conflit multi-UT":None,"Baissier naissant":38,
             "Rebond baissier (guet vente)":30,"Vente alignée":15,"Données partielles":None}
def setup_cell(setup):
    v = SETUP_VAL.get(setup)
    if v is None:
        return ("#3a3f55", "#cfd4e6")
    return grad(v)
def pos_chip(ut):
    if not ut:
        return '<span class=" utc" style="background:#2a2f45;color:#8b93ad">n/d</span>'
    p = ut["pos"]; lab = {"above":"Sur nuage","inside":"Dans nuage","below":"Sous nuage"}[p]
    bg = {"above":"#1f6b46","inside":"#5a4a1e","below":"#6b2a2a"}[p]
    cr = ""
    if ut.get("cross") == "bull": cr = " ↗TK"
    elif ut.get("cross") == "bear": cr = " ↘TK"
    return '<span class="utc" style="background:%s;color:#eef">%s%s</span>' % (bg, lab, cr)

ich_rows = [r for r in rows if r["id"] in ICH]
ich_rows.sort(key=lambda r: (ICHMOD.SETUP_ORDER.get(ICH[r["id"]]["setup"], 9), -r["glob"]))
from collections import Counter as _C
setup_counts = _C(ICH[r["id"]]["setup"] for r in ich_rows)
buy_aligned = [r for r in ich_rows if ICH[r["id"]]["setup"] == "Achat aligné"]
sell_aligned = [r for r in ich_rows if ICH[r["id"]]["setup"] == "Vente aligné" or ICH[r["id"]]["setup"] == "Vente alignée"]

P.append('<h2>Timing d\'entrée — Ichimoku multi-unités de temps (1H / 4H / 1D)</h2>')
P.append('<div class="small">Couche <b>séparée du score composite</b> (qui reste un score de positionnement). Logique : <b>1D = filtre de tendance</b>, <b>4H = structure</b>, <b>1H = déclencheur</b>. Les « setups » sont des <b>configurations de signal Ichimoku, pas des ordres</b> — le bandeau non-conseil s\'applique. Ichimoku(9,26,52, décalage 26). <b>Courbes TradingView (1D/4h/1h)</b> pour actions et crypto (EUR) — HYPE désormais complet.</div>')
P.append('<div class="kpis">')
for s in ["Achat aligné","Repli haussier (guet achat)","Haussier naissant","Neutre / indécis","Conflit multi-UT","Baissier naissant","Rebond baissier (guet vente)","Vente alignée"]:
    if setup_counts.get(s):
        bg, tx = setup_cell(s)
        P.append('<div class="kpi" style="border-left:4px solid %s"><div class="n">%d</div><div class="l">%s</div></div>' % (bg, setup_counts[s], esc(s)))
P.append('</div>')
if buy_aligned:
    P.append('<div class="small" style="margin:6px 0"><b style="color:#3ed598">Achat aligné (1D+4H+1H haussiers) :</b> ' + " · ".join(esc(r["name"]) for r in buy_aligned) + '</div>')
if sell_aligned:
    P.append('<div class="small" style="margin:6px 0"><b style="color:#ff6b6b">Vente alignée (1D+4H+1H baissiers) :</b> ' + " · ".join(esc(r["name"]) for r in sell_aligned) + '</div>')
P.append('<div style="overflow-x:auto"><table><thead><tr><th>Actif</th><th>Setup MTF</th><th>1D</th><th>4H</th><th>1H</th><th class="r">Kijun 1D</th><th class="r">Nuage 1D (support–résist.)</th><th class="r">Global</th></tr></thead><tbody>')
for r in ich_rows:
    ic = ICH[r["id"]]; cur = r["cur"]
    bg, tx = setup_cell(ic["setup"])
    d1 = ic.get("d1")
    kij = ("%.2f" % d1["kijun"]) + (" $" if cur == "USD" else " €") if d1 else "n/d"
    cloud = ("%.2f–%.2f" % (d1["cloud_bot"], d1["cloud_top"])) if d1 else "n/d"
    gbg, gtx = grad(r["glob"])
    P.append('<tr><td><b>%s</b> <span class="mut" style="font-size:10px">%s</span></td>'
             '<td><span class="sc" style="background:%s;color:%s;min-width:120px">%s</span></td>'
             '<td>%s</td><td>%s</td><td>%s</td><td class="r mut">%s</td><td class="r mut">%s</td>'
             '<td class="r"><span class="sc" style="background:%s;color:%s">%d</span></td></tr>'
             % (esc(r["name"]), esc(r["id"]), bg, tx, esc(ic["setup"]),
                pos_chip(ic.get("d1")), pos_chip(ic.get("h4")), pos_chip(ic.get("h1")),
                esc(kij), esc(cloud), gbg, gtx, r["glob"]))
P.append('</tbody></table></div>')
P.append('<div class="small" style="margin-top:6px"><b>Lecture entrée (signal, non-conseil) :</b> un <b>Achat aligné</b> = les 3 UT au-dessus du nuage avec déclencheur 1H (croisement Tenkan/Kijun ↗ ou sortie de nuage). Le <b>Kijun 1D</b> et les <b>bords du nuage 1D</b> servent de niveaux de référence (support/résistance, invalidation). « Repli haussier » / « Rebond baissier » = fond directionnel mais timing 1H pas encore déclenché : zones de guet. « Conflit » = 1D et 4H opposés, pas de configuration nette.</div>')

# Sentiment
P.append('<h2>Sentiment presse &amp; consensus analystes</h2>')
P.append('<div class="small">Chaque point est sourcé (média, date, lien). Paraphrase systématique. Les actifs non listés ici reçoivent un <b>proxy sectoriel</b> (voir plus bas), explicitement non attribué à un article individuel.</div>')
for r in rows:
    s = r["sent_rec"]
    if not s["sourced"]: continue
    P.append('<div class="card"><h3 style="margin-top:0">%s <span class="tag">%s</span> <span class="tag">sentiment %d</span></h3>' % (esc(r["name"]), esc(s.get("label","")), s["score"]))
    if s.get("consensus"): P.append('<div class="small">Consensus : %s</div>' % esc(s["consensus"]))
    for pt in s.get("points", []):
        P.append('<div class="pt">%s<br><span class="m">— <a href="%s" target="_blank" rel="noopener">%s</a>, %s</span></div>'
                 % (esc(pt["t"]), esc(pt["url"]), esc(pt["media"]), esc(pt["date"])))
    P.append('</div>')
# proxy list
nproxy = sum(1 for r in rows if not r["sent_rec"]["sourced"])
P.append('<h3>Proxies sentiment sectoriels (non sourcés individuellement) — %d valeurs</h3><div class="card"><div class="small">Score affecté par secteur macro, faute de pouvoir sourcer individuellement les %d valeurs du SBF 120 en un run. Non attribué à un article. À fouiller au cas par cas pour une conviction.</div><table><thead><tr><th>Actif</th><th class="r">Sent.</th><th>Base sectorielle</th></tr></thead><tbody>' % (nproxy, len(rows)))
for r in sorted([x for x in rows if not x["sent_rec"]["sourced"]], key=lambda x:-x["sent_rec"]["score"]):
    s = r["sent_rec"]
    P.append('<tr><td>%s <span class="mut">%s</span></td><td class="r">%d</td><td class="mut">%s</td></tr>' % (esc(r["name"]), esc(r["id"]), s["score"], esc(s.get("basis",""))))
P.append('</tbody></table></div>')

# Macro
_fresh = ('<span class="tag" style="background:#12331f;border-color:#1f6b46;color:#8ef0b8">Rafraîchi par LLM le %s</span>' % esc(DYN_DATE)) if DYN_ON else '<span class="tag">Curation figée (non rafraîchie ce run)</span>'
P.append('<h2>Macro du jour %s</h2><div class="card">' % _fresh)
for k in ("bce","fed","infla","cycle","agenda"):
    if MACRO_TODAY_USED.get(k):
        P.append('<div class="pt">%s</div>' % esc(MACRO_TODAY_USED[k]))
P.append('</div>')
P.append('<h3>Score macro par secteur (appliqué par héritage sectoriel)</h3><div class="card"><table><thead><tr><th>Secteur macro</th><th class="r">Score</th><th>Logique (régime courant)</th></tr></thead><tbody>')
for sec, v in sorted(MACRO_SECTORS_USED.items(), key=lambda kv:-kv[1]["score"]):
    bg, tx = grad(v["score"])
    P.append('<tr><td><b>%s</b></td><td class="r"><span class="sc" style="background:%s;color:%s">%d</span></td><td class="mut">%s</td></tr>' % (esc(sec), bg, tx, v["score"], esc(v["rat"])))
P.append('</tbody></table></div>')

# ===== Micro / creation de valeur =====
P.append('<h2>Micro — création de valeur (ROIC vs WACC) &amp; valorisation relative (PER)</h2>')
P.append('<div class="small">Note 0–100 = 60 % <b>création de valeur</b> (spread ROIC − WACC ; pour banques/assurances : ROE − coût des FP) + 40 % <b>valorisation relative</b> (PER vs médiane du secteur macro). '
         '<b>WACC complet</b> = (E/V)·Re + (D/V)·Rd·(1−impôt), avec Re = CAPM (3 % + β·5 %), <b>Rd = taux d\'intérêt effectif réel</b> de la dette (TradingView), impôt 25 % forfaitaire, poids dette plafonné à 60 % (neutralise les bilans à banque captive type Renault/Stellantis). Banques/assurances : coût des fonds propres seul. Fondamentaux : TradingView (scanner). '
         'Crypto et sociétés en perte : <b>n/d</b>. ROIC peu pertinent pour banques/foncières (substitution/flag).</div>')
micro_rows = [r for r in rows if r["micro"] is not None]
micro_rows.sort(key=lambda r: -r["micro"])
topm = micro_rows[:6]; botm = micro_rows[-6:]
if topm:
    P.append('<div class="small" style="margin:6px 0"><b style="color:#3ed598">Créateurs de valeur (ROIC≫WACC + valorisation raisonnable) :</b> ' + " · ".join("%s (%d)" % (esc(r["name"]), r["micro"]) for r in topm) + '</div>')
    P.append('<div class="small" style="margin:6px 0"><b style="color:#ff6b6b">Destructeurs / chers vs pairs :</b> ' + " · ".join("%s (%d)" % (esc(r["name"]), r["micro"]) for r in botm) + '</div>')
P.append('<div style="overflow-x:auto"><table><thead><tr><th>Actif</th><th>Secteur</th><th class="r">Micro</th><th>Métrique</th><th class="r">ROIC/ROE</th><th class="r">WACC*</th><th class="r">Spread</th><th class="r">PER</th><th class="r">PER méd. sect.</th><th class="r">PER rel.</th></tr></thead><tbody>')
def f1(x, suf=""):
    return ("%.1f%s" % (x, suf)) if isinstance(x, (int, float)) else "n/d"
for r in micro_rows:
    m = r["micro_rec"]; bg, tx = grad(r["micro"])
    metric_val = m.get("metric")
    cav = ' <span class="badge" title="%s">!</span>' % esc(m.get("caveat")) if m.get("caveat") else ""
    betatag = ' <span class="mut" style="font-size:9px">(β déf.)</span>' if m.get("beta_default") else ""
    P.append('<tr><td><b>%s</b> <span class="mut" style="font-size:10px">%s</span>%s</td><td class="mut">%s</td>'
             '<td class="r"><span class="sc" style="background:%s;color:%s">%d</span></td>'
             '<td class="mut" style="font-size:11px">%s</td><td class="r">%s</td><td class="r mut">%s%s</td>'
             '<td class="r">%s</td><td class="r">%s</td><td class="r mut">%s</td><td class="r">%s</td></tr>'
             % (esc(r["name"]), esc(r["id"]), cav, esc(r["macsec"]), bg, tx, r["micro"],
                esc(m.get("metric_label","")), f1(metric_val, " %"), f1(m.get("wacc")," %"), betatag,
                ("+%.1f" % m["spread"]) if isinstance(m.get("spread"),(int,float)) and m["spread"]>=0 else f1(m.get("spread")),
                f1(m.get("per")), f1(m.get("sector_median_per")), f1(m.get("rel_per"))))
P.append('</tbody></table></div>')
P.append('<div class="small" style="margin-top:6px">* WACC complet = (E/V)·Re + (D/V)·Rd·(1−25 %) : Re = CAPM (3 % + β·5 %), Rd = taux d\'intérêt effectif réel de la dette (TradingView), poids dette plafonné à 60 %, WACC borné 5–13 %. Banques/assurances : coût des fonds propres. Spread &gt; 0 = rendement du capital supérieur à son coût = création de valeur (durable si récurrent). PER rel. &lt; 1 = moins cher que la médiane du secteur. Reste estimé : impôt forfaitaire 25 %, β et Rd issus de TradingView.</div>')

# Perspectives
P.append('<h2>Perspectives CT / MT / LT</h2>')
P.append('<div class="small">Court terme = lecture technique. Moyen terme = consensus analystes + dynamique de résultats. Long terme = macro sectorielle + structurel. Aucune prévision chiffrée de cours.</div>')
for label, p in A.PERSP_UNIVERS.items():
    P.append('<h3>Univers — %s</h3><div class="persp"><div><div class="t">Court terme</div>%s</div><div><div class="t">Moyen terme</div>%s</div><div><div class="t">Long terme</div>%s</div></div>' % (esc(label), esc(p["ct"]), esc(p["mt"]), esc(p["lt"])))
for aid, p in A.PERSPECTIVES.items():
    r = rec_by_id.get(aid)
    if not r: continue
    P.append('<h3>%s <span class="tag">%s</span> <span class="tag">global %d</span></h3><div class="persp"><div><div class="t">Court terme</div>%s</div><div><div class="t">Moyen terme</div>%s</div><div><div class="t">Long terme</div>%s</div></div>' % (esc(r["name"]), esc(r["id"]), r["glob"], esc(p["ct"]), esc(p["mt"]), esc(p["lt"])))

# Methodologie
P.append('<h2>Méthodologie</h2><div class="card">')
P.append('<h3 style="margin-top:0">Sémantique du score</h3><div class="small">Tout score est sur 0–100 : <b>100 = signaux d\'achat maximaux, 50 = neutre, 0 = signaux de vente maximaux</b>. Score global = (<b>50·Technique + 15·Sentiment + 15·Macro + 20·Micro</b>) / 100, renormalisé sur les blocs présents (la crypto, sans Micro, repasse en ≈ 63·Tech / 19·Sent / 19·Macro). Deux runs sur les mêmes données donnent le même score.</div>')
P.append('<h3>Règle de signal technique (déterministe, constante)</h3><div class="small">Somme de contributions signées (−100…+100) puis mappée 0–100. <b>L\'Ichimoku 1D est intégré (20 % du bloc)</b> ; les UT 4h/1h restent dans la couche timing séparée.<br>'
         '• <b>Tendance MM (±30)</b> : cours vs MM200 (±11), vs MM50 (±6), vs MM20 (±4), MM50 vs MM200 (±5), MM20 vs MM50 (±4).<br>'
         '• <b>Ichimoku 1D (±20)</b> : prix vs nuage (au-dessus +8 / dans 0 / sous −8), Tenkan vs Kijun (±4), nuage futur SpanA/B (±4), Chikou vs prix il y a 26 (±4).<br>'
         '• <b>RSI(14) (±18)</b> : ≥70 +5 · 55–70 +18 · 50–55 +9 · 45–50 −9 · 30–45 −14 · &lt;30 −7.<br>'
         '• <b>MACD(12/26/9) (±18)</b> : histogramme &gt;0 (±9) + ligne MACD &gt;0 (±9).<br>'
         '• <b>ADX(14) (±8)</b> : ≥25 ±8 · 20–25 ±4, signe selon cours vs MM50 (force × direction).<br>'
         '• <b>Bollinger %B (±6)</b> : &gt;1 +2 · 0,5–1 +6 · 0–0,5 −6 · &lt;0 −2.<br>'
         'ATR(14) et volume relatif (vs MM20) sont calculés et affichés mais hors score. Si une composante est indisponible (ex. pas d\'OHLC), elle est neutralisée et le total renormalisé sur les composantes présentes.</div>')
P.append('<h3>Filtre de régime MM30/MM120</h3><div class="small">MM30 et MM120 définissent le régime de fond : <b>haussier si MM30 &gt; MM120</b>, baissier sinon. Un signal d\'achat (technique &gt; 55) n\'est validé qu\'en régime haussier ; un signal de vente (&lt; 45) qu\'en régime baissier. Sinon le signal est <b>amorti</b> (ramené à 40 % de son écart à 50) et marqué <b>⚑ filtré</b>. Objectif : ne pas prendre un signal court terme à contre-tendance de fond.</div>')
P.append('<h3>Note Micro (création de valeur)</h3><div class="small">0–100 = 60 % spread <b>ROIC − WACC</b> (économique : gagne-t-on au-dessus du coût du capital, durablement) + 40 % <b>PER relatif</b> au secteur macro (médiane). Banques/assurances : <b>ROE − coût des FP</b> (le ROIC bancaire n\'est pas comparable). <b>WACC complet</b> = (E/V)·Re + (D/V)·Rd·(1−impôt) : Re = CAPM (rf 3 % + β·5 %), <b>Rd = taux d\'intérêt effectif réel de la dette</b> (TradingView), impôt 25 % forfaitaire, poids E/D par capitalisation vs dette totale, poids dette plafonné à 60 % (neutralise les bilans à banque captive), WACC borné 5–13 %. Banques/assurances : coût des fonds propres seul (WACC pondéré par la dette non pertinent). Fondamentaux : TradingView (scanner REST). Crypto et sociétés en perte : n/d (exclues, global renormalisé).</div>')
P.append('<h3>Sentiment</h3><div class="small">Score dérivé du sens du consensus analystes (quand disponible) et de la tonalité des analyses &lt;7 j, avec filtre « news vs bruit » (résultats, guidance, marges, M&amp;A, régulation &gt; rumeurs). Les actifs majeurs sont sourcés individuellement ; les autres reçoivent un <b>proxy sectoriel</b> explicitement signalé.</div>')
P.append('<h3>Macro</h3><div class="small">Score 0–100 par secteur selon la sensibilité documentée au régime courant (taux, inflation/énergie, géopolitique, cycle). Chaque actif hérite du score macro de son secteur.</div>')
P.append('<h3>Divergence</h3><div class="small">Un écart &gt;30 points entre le bloc le plus haut et le plus bas déclenche le flag « contradiction » (ex. Technique faible / Macro fort). La divergence est l\'information la plus utile, pas le chiffre agrégé.</div>')
P.append('<h3>Ichimoku (couche timing, séparée du score)</h3><div class="small">Ichimoku Kinko Hyo, paramètres standard : Tenkan 9, Kijun 26, Senkou B 52, décalage 26. Par UT (1D/4H/1H) : position du prix vs nuage (Kumo), relation Tenkan/Kijun + croisement récent (≤3 barres), couleur du nuage futur, Chikou. <b>Classification multi-UT déterministe</b> : 1D filtre la tendance, 4H confirme la structure, 1H déclenche. Setups : Achat/Vente aligné (3 UT cohérentes + déclencheur 1H), Repli/Rebond (fond directionnel, timing non déclenché), Conflit (1D vs 4H opposés), Naissant, Neutre. <b>Cette couche ne modifie pas le score composite</b> et reste un signal, pas un conseil. Courbes : <b>TradingView</b> (1D/4h/1h) — actions (EURONEXT) et crypto (BTCEUR/ETHEUR/SOLEUR/HYPEEUR, EUR), OHLC complet y compris HYPE.</div>')
P.append('</div>')

# Footer
P.append('<h2>Sources, limites &amp; horodatage</h2><div class="card">')
for cat, items in A.SOURCES.items():
    P.append('<h3>%s</h3><ul class="src">' % esc(cat))
    for name, url in items:
        P.append('<li><a href="%s" target="_blank" rel="noopener">%s</a></li>' % (esc(url), esc(name)))
    P.append('</ul>')
P.append('<h3>Couverture &amp; indisponibilités</h3>')
if unavailable:
    P.append('<div class="small">Actifs indisponibles : ' + " · ".join("%s (%s)" % (esc(a), esc(c)) for a,n,c in unavailable) + '</div>')
else:
    P.append('<div class="small">Couverture : <b>%d/%d actifs</b> (%d valeurs SBF 120 + %d crypto), tous avec prix réel + indicateurs calculés + score décomposé. Aucun actif indisponible sur ce run.</div>' % (len(rows), len(rows), n_stocks, n_crypto))
P.append('<h3>Limites connues (à vérifier)</h3><div class="small">'
         '• <b>Univers SBF 120</b> : %d/120 valeurs résolues. Membership A→O vérifiée sur source live datée (EasyBourse, 27/06/2026) ; tail P→Z complété par connaissance puis <b>chaque ticker validé par le pull Yahoo</b> (aucun prix fabriqué). Il peut manquer ~%d valeurs récemment entrées et 1–2 rotations du tail — à recouper sur la liste officielle Euronext.<br>'
         '• <b>Sentiment</b> : %d valeurs sourcées individuellement ; les %d autres en proxy sectoriel explicite (non attribué à un article).<br>'
         '• <b>Courbes actions = TradingView</b> (websocket, données différées, token non authentifié) : endpoint non officiel, soumis aux CGU TradingView (usage perso, pas de rediffusion), peut changer/casser sans préavis. Non temps réel.<br>'
         '• <b>Crypto</b> : TradingView en EUR (BTCEUR/ETHEUR/SOLEUR/HYPEEUR), OHLC complet sur les 3 UT, y compris HYPE (historique court ~167 j en journalier).<br>'
         '• <b>Macro &amp; agenda</b> : vérifie chaque chiffre/échéance récent sur la source primaire avant d\'agir.</div>'
         % (n_stocks, max(0, 120 - n_stocks), nsourced, len(rows) - nsourced))
P.append('<div class="small" style="margin-top:10px">Généré le <b>%s</b> · Veille Marché FR (agrégateur de signaux, non-conseil).</div>' % esc(run_str))
P.append('</div>')

P.append('</div>')
P.append('<div id="lb"><span class="x">&#10005;</span><div class="cap"></div><img alt=""></div>')
P.append('<script>(function(){var lb=document.getElementById("lb"),im=lb.querySelector("img"),cap=lb.querySelector(".cap");document.querySelectorAll(".chartcard img").forEach(function(g){g.addEventListener("click",function(){im.src=g.src;cap.textContent=g.alt||"";lb.classList.add("on");});});function c(){lb.classList.remove("on");im.removeAttribute("src");}lb.addEventListener("click",function(){c();});document.addEventListener("keydown",function(e){if(e.key==="Escape")c();});})();</script>')
P.append('</body></html>')

out_path = os.path.join(BASE, fname)
open(out_path, "w", encoding="utf-8").write("".join(P))
size_kb = os.path.getsize(out_path) / 1024
print("Dashboard ecrit:", fname, "(%.0f KB)" % size_kb)
print("Couverts: %d | Indisponibles: %d | Divergences: %d | Sourced sentiment: %d" % (len(rows), len(unavailable), ndiv, nsourced))
# Save a machine-readable snapshot too
json.dump({"run": run_str, "data_date": data_date, "rows": rows, "unavailable": unavailable}, open(os.path.join(BASE, "run_snapshot.json"), "w"), indent=1, default=str)
print("Top5:", [(r["name"], r["glob"]) for r in rows[:5]])
print("Bot5:", [(r["name"], r["glob"]) for r in rows[-5:]])
