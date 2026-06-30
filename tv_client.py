# -*- coding: utf-8 -*-
"""Client minimal du websocket TradingView (donnees differees, token 'unauthorized_user_token').
Recupere des series de bougies OHLCV pour un symbole et une resolution. Non officiel (ToS TV)."""
import websocket, json, re, random, string, time

def _gen(prefix):
    return prefix + "".join(random.choice(string.ascii_lowercase) for _ in range(12))

def _msg(m, p):
    j = json.dumps({"m": m, "p": p}); return "~m~%d~m~%s" % (len(j), j)

def get_series(symbol, resolution="1D", bars=400, timeout=22):
    """Retourne (dates_ts, open, high, low, close, volume) ou None. resolution: '60','240','1D','1W'..."""
    cs = _gen("cs_")
    ws = websocket.create_connection("wss://data.tradingview.com/socket.io/websocket",
                                     header=["Origin: https://www.tradingview.com"], timeout=15)
    try:
        ws.send(_msg("set_auth_token", ["unauthorized_user_token"]))
        ws.send(_msg("chart_create_session", [cs, ""]))
        sym = '={"symbol":"%s","adjustment":"splits"}' % symbol
        ws.send(_msg("resolve_symbol", [cs, "sym1", sym]))
        ws.send(_msg("create_series", [cs, "s1", "s1", "sym1", resolution, bars, ""]))
        bars_map = {}; done = False; err = None; t0 = time.time()
        while time.time() - t0 < timeout and not done:
            data = ws.recv()
            for part in re.split(r"~m~\d+~m~", data):
                if not part:
                    continue
                if part.startswith("~h~"):
                    ws.send("~m~%d~m~%s" % (len(part), part)); continue
                try:
                    o = json.loads(part)
                except Exception:
                    continue
                m = o.get("m")
                if m == "timescale_update":
                    pdata = o["p"][1]
                    for k, v in pdata.items():
                        if isinstance(v, dict) and "s" in v:
                            for b in v["s"]:
                                vv = b["v"]; bars_map[vv[0]] = vv
                elif m == "series_completed":
                    done = True
                elif m in ("symbol_error", "series_error", "critical_error", "protocol_error"):
                    err = str(o.get("p")); done = True
        if err or not bars_map:
            return None
        rows = [bars_map[k] for k in sorted(bars_map)]
        ts = [int(r[0]) for r in rows]
        op = [r[1] for r in rows]; hi = [r[2] for r in rows]; lo = [r[3] for r in rows]
        cl = [r[4] for r in rows]; vo = [r[5] if len(r) > 5 else None for r in rows]
        return ts, op, hi, lo, cl, vo
    finally:
        try: ws.close()
        except Exception: pass

if __name__ == "__main__":
    import sys, datetime
    sym = sys.argv[1] if len(sys.argv) > 1 else "EURONEXT:BNP"
    for res in ("1D", "240", "60"):
        r = get_series(sym, res, 300)
        if r:
            ts = r[0]; f = lambda t: datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d %H:%M")
            print("%-16s %-4s bars=%d  [%s -> %s]  last close=%.2f" % (sym, res, len(ts), f(ts[0]), f(ts[-1]), r[4][-1]))
        else:
            print("%-16s %-4s -> AUCUNE SERIE" % (sym, res))
        time.sleep(0.4)
