# Veille Marché FR — SBF 120 + Crypto

Agrégateur de signaux publics (NON un conseil d'investissement) : technique TradingView + Ichimoku MTF
+ filtre de régime MM30/MM120 + sentiment/macro (curation) + micro (ROIC vs WACC, PER relatif).
Produit un dashboard HTML autoportant `veille-marche_AAAA-MM-JJ_HHhMM.html`.

## Lancer un run
```
pip install -r requirements.txt --break-system-packages
python3 tv_fetch.py 0 20 && python3 tv_fetch.py 20 40 && python3 tv_fetch.py 40 60 \
 && python3 tv_fetch.py 60 80 && python3 tv_fetch.py 80 100 && python3 tv_fetch.py 100 113
python3 tv_crypto.py
python3 tv_fundamentals.py
python3 compute_micro.py
python3 indicators.py
python3 tv_ichimoku.py
python3 build_dashboard.py
```
Le dashboard est écrit dans le dossier courant.

## Pondération du score global
Technique 50 / Sentiment 15 / Macro 15 / Micro 20 (renormalisé si un bloc manque, ex. crypto).

## Données
- Courbes : TradingView (websocket, actions EURONEXT:* et crypto *EUR), différées, endpoint non officiel.
- Fondamentaux : TradingView scanner (ROIC, ROE, PER, beta, dette, coût de la dette).
- Sentiment & macro : curation manuelle dans `analysis_data.py` (à rafraîchir périodiquement).
