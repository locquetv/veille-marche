# -*- coding: utf-8 -*-
# Donnees d'analyse resolues par recherche web le 2026-06-29. Chaque fait sentiment/macro est source.

# ---- MACRO : score 0-100 par secteur macro + justification (regime courant) ----
MACRO_SECTORS = {
 "Energie":           {"score": 72, "rat": "Brent ~80 $ (19/06), choc d'offre Moyen-Orient, resultats petroliers dopes. Biais MT prudent (AIE : surproduction record ~4 Mb/j en 2026)."},
 "Defense & Aero":    {"score": 75, "rat": "Rearmement europeen + budgets OTAN + conflit Moyen-Orient ; carnets de commandes record. Risque : valorisations tendues, debat exclusion CAC 40 ESG."},
 "Banques & Assurance":{"score": 68, "rat": "Hausse BCE (+25 pb le 11/06, depot 2,25 %) elargit les marges nettes d'interet ; ROE > 10 %. Risque : instabilite politique francaise."},
 "Electrification & Industrie":{"score": 60, "rat": "Capex electrification / datacenters structurel, mais sensibilite aux taux longs en regime de remontee."},
 "Construction & Infra":{"score": 42, "rat": "Remontee des taux directeurs penalise les valeurs a fort levier et le BTP ; demande de credit atone."},
 "Luxe":              {"score": 47, "rat": "Demande chinoise atone, craintes de guerre commerciale ; sous-performance ~20 % sur 2 ans. Franchises premium intactes."},
 "Automobile":        {"score": 33, "rat": "Tarifs douaniers US (Stellantis : 1,6 Md€ de couts 2026), demande faible, cycle defavorable."},
 "Sante":             {"score": 60, "rat": "Profil defensif recherche en regime d'incertitude ; faible sensibilite aux taux ; decotes de valorisation."},
 "Conso de base":     {"score": 52, "rat": "Defensif, mais inflation des intrants (energie +10,9 %) ; exposition Chine pour les spiritueux."},
 "Conso discretionnaire & Services":{"score": 48, "rat": "Voyage / hotellerie resilients (Accor) ; cycle publicitaire incertain (Publicis)."},
 "Utilities":         {"score": 43, "rat": "Sensibilite negative aux taux (proxy obligataire, dette elevee) ; effet prix de l'energie mitige."},
 "Materiaux":         {"score": 50, "rat": "Gaz industriels defensifs (Air Liquide) vs siderurgie cyclique exposee aux couts energie (ArcelorMittal)."},
 "Technologie":       {"score": 46, "rat": "Hausse des taux pese sur les multiples ; semis cycliques mais tires par l'IA / datacenters."},
 "Telecoms":          {"score": 50, "rat": "Defensif, cash-flows stables, mais dette sensible aux taux."},
 "Immobilier":        {"score": 32, "rat": "Remontee des taux = vent de face direct sur les foncieres (cout de la dette, valorisation d'actifs)."},
 "Crypto":            {"score": 38, "rat": "Regime taux eleves + Fed au biais haussier = risk-off ; sorties ETF massives en juin 2026 (~4,3 Md$)."},
}

ASSET_MACRO_SECTOR = {
 "TTE.PA":"Energie",
 "AIR.PA":"Defense & Aero","SAF.PA":"Defense & Aero","HO.PA":"Defense & Aero",
 "BNP.PA":"Banques & Assurance","GLE.PA":"Banques & Assurance","ACA.PA":"Banques & Assurance","CS.PA":"Banques & Assurance","ENX.PA":"Banques & Assurance",
 "SU.PA":"Electrification & Industrie","LR.PA":"Electrification & Industrie",
 "DG.PA":"Construction & Infra","FGR.PA":"Construction & Infra","EN.PA":"Construction & Infra","SGO.PA":"Construction & Infra","BVI.PA":"Construction & Infra",
 "MC.PA":"Luxe","OR.PA":"Luxe","RMS.PA":"Luxe","KER.PA":"Luxe",
 "ML.PA":"Automobile","STLAP.PA":"Automobile","RNO.PA":"Automobile",
 "SAN.PA":"Sante","EL.PA":"Sante","ERF.PA":"Sante",
 "BN.PA":"Conso de base","RI.PA":"Conso de base","CA.PA":"Conso de base",
 "PUB.PA":"Conso discretionnaire & Services","AC.PA":"Conso discretionnaire & Services",
 "ENGI.PA":"Utilities","VIE.PA":"Utilities",
 "AI.PA":"Materiaux","MT.PA":"Materiaux",
 "STMPA.PA":"Technologie","CAP.PA":"Technologie","DSY.PA":"Technologie",
 "ORA.PA":"Telecoms",
 "URW.PA":"Immobilier",
 "BTC":"Crypto","ETH":"Crypto","SOL":"Crypto","HYPE":"Crypto",
}

# ---- SENTIMENT : score 0-100. sourced=True -> points sources individuels. sinon proxy sectoriel flagge. ----
SENTIMENT = {
 # --- Crypto (sources) ---
 "BTC": {"score":28,"sourced":True,"label":"Negatif","consensus":"Test du support 60 000 $",
   "points":[{"t":"Pire mois observe : ~4,33 Md$ de sorties globales sur ETF crypto ; le BTC a efface toute la hausse de 2025, retour sur niveaux de 2024.","media":"ActuCrypto","date":"juin 2026","url":"https://actucrypto.info/etf/etf-crypto-sorties-bitcoin-ethereum-solana-hype/"},
            {"t":"BTC ~60 029 $ (-0,75 % sur 24 h), 444,5 M$ de retraits nets sur les produits BTC.","media":"ActuCrypto","date":"juin 2026","url":"https://actucrypto.info/bitcoin/bitcoin-bitcoinperpetuel-prix-btcusdt-60029-usd-btc-aujourdhui/"}]},
 "ETH": {"score":27,"sourced":True,"label":"Negatif","consensus":"Ne capte pas la rotation",
   "points":[{"t":"Sorties sur ETF ETH ; incapacite a capter la rotation des capitaux, l'ETH reste a la traine.","media":"ActuCrypto","date":"juin 2026","url":"https://actucrypto.info/etf/etf-crypto-sorties-bitcoin-ethereum-solana-hype/"}]},
 "SOL": {"score":45,"sourced":True,"label":"Mitige / force relative","consensus":"Test du support 68 $",
   "points":[{"t":"A contre-courant : entrees sur ETF SOL, forte activite on-chain (DeFi, RWA) ; mais test du support critique 68 $ dans un marche en correction.","media":"ActuCrypto","date":"juin 2026","url":"https://actucrypto.info/solana/solana-solanaperpetuel-prix-solusdt-69-63-usd-sol-cours/"}]},
 "HYPE":{"score":48,"sourced":True,"label":"Mitige / rotation favorable","consensus":"Vehicule favorise dans la rotation",
   "points":[{"t":"Les institutionnels alimentent discretement les vehicules lies a Solana, XRP et Hyperliquid pendant qu'ils retirent du BTC/ETH.","media":"ActuCrypto / Crypto-insiders","date":"juin 2026","url":"https://actucrypto.info/etf/etf-crypto-sorties-bitcoin-ethereum-solana-hype/"}]},
 # --- Luxe ---
 "MC.PA":{"score":52,"sourced":True,"label":"Mitige (decote vs consensus)","consensus":"58 % a l'Achat/Surperf., OC moyen ~646,7 €",
   "points":[{"t":"Consensus majoritairement acheteur (OC moyen 12 m ~646,7 €), mais Berenberg a nettement abaisse ses objectifs sur LVMH et Hermes ; marche chinois atone.","media":"MSN Finance / EasyBourse","date":"mai-juin 2026","url":"https://www.easybourse.com/action-consensus/lvmh/FR0000121014-25"}]},
 "RMS.PA":{"score":42,"sourced":True,"label":"Negatif court terme","consensus":"Objectifs abaisses (Berenberg)",
   "points":[{"t":"Hermes parmi les valeurs ayant le plus pese sur le CAC le 22/06 ; objectifs de cours luxe abaisses ; sous-performance sectorielle ~20 % sur 2 ans.","media":"MoneyVox / MSN Finance","date":"22/06/2026","url":"https://www.moneyvox.fr/bourse/actualites/109381/prudence-pour-le-cac-40-chute-de-hermes-le-journal-de-la-bourse-du-22-juin-2026"}]},
 "KER.PA":{"score":44,"sourced":True,"label":"Mitige (redressement incertain)","consensus":"Decote vs juste prix estime",
   "points":[{"t":"Analystes jugent les justes prix de LVMH/Hermes/Kering superieurs aux cours, mais redressement de Kering (Gucci) incertain dans un luxe sous pression.","media":"MSN Finance","date":"mai-juin 2026","url":"https://www.msn.com/fr-fr/finance/autres/lvmh-herm%C3%A8s-et-kering-accumulent-un-net-retard-en-bourse-du-potentiel-sur-les-actions-du-luxe-du-cac-40/ar-AA22WcTb"}]},
 # --- Energie ---
 "TTE.PA":{"score":63,"sourced":True,"label":"Positif (avec reserve MT)","consensus":"Jefferies Achat, OC releve a 93 € (vs 78 €)",
   "points":[{"t":"Resultat net T1 2026 a 5,93 Md$ (vs 3,92 Md$ un an avant), dope par la hausse du petrole ; OC analystes 78-93 €.","media":"EasyBourse / Investing.fr","date":"juin 2026","url":"https://fr.investing.com/news/stock-market-news/totalenergies-seffondre-avec-le-petrole--le-pire-estil-a-venir--3397985"},
            {"t":"Reserve MT : l'AIE anticipe une surproduction record (~4 Mb/j) en 2026, scenarios Brent moyen 60-75 $.","media":"Investing.fr","date":"juin 2026","url":"https://fr.investing.com/news/stock-market-news/totalenergies-seffondre-avec-le-petrole--le-pire-estil-a-venir--3397985"}]},
 # --- Defense / Aero ---
 "AIR.PA":{"score":60,"sourced":True,"label":"Positif (valorisation tendue)","consensus":"Secteur porteur, points d'entree exigeants",
   "points":[{"t":"Aero civile + defense porteuses (rearmement, OTAN) ; debat sur la surevaluation des leaders Airbus/Thales/Safran.","media":"Le Journal de la Finance","date":"2026","url":"https://www.lejournaldelafinance.com/airbus-thales-safran-defense/"}]},
 "SAF.PA":{"score":60,"sourced":True,"label":"Positif (valorisation tendue)","consensus":"Secteur porteur",
   "points":[{"t":"Moteurs / defense : visibilite exceptionnelle a LT (budgets OTAN), mais valorisations deja riches.","media":"Le Journal de la Finance / Meilleurtaux","date":"2026","url":"https://placement.meilleurtaux.com/bourse/actualites/2026-janvier/defense-aeronautique-deviennent-nouveaux-secteurs-prometteurs-investir.html"}]},
 "HO.PA":{"score":62,"sourced":True,"label":"Positif (valorisation tendue)","consensus":"Carnet >3 ans de visibilite",
   "points":[{"t":"Prises de commandes Defense +75 % en organique au T1 2026 (SAMP/T NG Danemark, contrat Qatar) ; carnet 53,3 Md$ fin 2025.","media":"Cafe de la Bourse","date":"T1 2026","url":"https://www.cafedelabourse.com/bourse/action-thales-faut-il-investir"},
            {"t":"Risque : debat sur une exclusion du CAC 40 ESG et valorisation deja tendue.","media":"Cafe de la Bourse","date":"2026","url":"https://www.cafedelabourse.com/bourse/action-thales-faut-il-investir"}]},
 # --- Sante ---
 "SAN.PA":{"score":70,"sourced":True,"label":"Positif (value + croissance)","consensus":"12/22 positifs, 0 negatif, OC median 97 € (+26 %)",
   "points":[{"t":"Consensus haussier (OC median 97 €, +26 %) ; Dupixent >30 % de croissance (>4 Md€/trim.) ; nouveaux medicaments +49,6 % au T1.","media":"Zonebourse / EasyBourse","date":"juin 2026","url":"https://www.zonebourse.com/cours/action/SANOFI-4698/consensus/"},
            {"t":"Decote marquee : PER ~8,75 et rendement du dividende >5 %.","media":"MoneyRadar","date":"juin 2026","url":"https://moneyradar.org/bourse/acheter-des-actions/action-sanofi/"}]},
 # --- Banques ---
 "BNP.PA":{"score":72,"sourced":True,"label":"Positif","consensus":"Beneficiaire direct de la hausse BCE",
   "points":[{"t":"+5 % en seance apres la hausse BCE (depot 2,25 %) : un depot plus eleve dope la marge nette d'interet de la banque de detail ; +10,89 % YTD 2026.","media":"XTB / BFM Bourse","date":"12/06/2026","url":"https://www.xtb.com/fr/analyses-marches/bourse-bnp-paribas-et-societe-generale-bondissent-de-5"}]},
 "GLE.PA":{"score":68,"sourced":True,"label":"Positif","consensus":"Forte revalorisation sur 1 an",
   "points":[{"t":"+85,56 % sur 1 an (leger repli ~ -2 % YTD 2026) ; beneficiaire de la hausse des taux, ROE >10 %, attrait dividende.","media":"XTB / BFM Bourse","date":"juin 2026","url":"https://www.xtb.com/fr/analyses-marches/bourse-bnp-paribas-et-societe-generale-bondissent-de-5"}]},
 # --- Tech ---
 "STMPA.PA":{"score":75,"sourced":True,"label":"Positif","consensus":"1re hausse du CAC 40 en 2026 (+79 %)",
   "points":[{"t":"+79 % en 2026, 1re place du CAC 40 ; objectif datacenters double a 1 Md$ ; mega-contrat AWS estime ~5 Md$.","media":"BFM Bourse / Usine Nouvelle","date":"juin 2026","url":"https://www.usinenouvelle.com/electronique-informatique/semi-conducteurs-porte-par-le-developpement-de-lia-stmicro-double-son-objectif-de-chiffre-daffaires-pour-2026-dans-les-datacenters.UOP3E6LCCZH77BS5MHMS2IPAUE.html"}]},
 "SU.PA":{"score":52,"sourced":True,"label":"Neutre court terme","consensus":"Structurellement solide",
   "points":[{"t":"-4,2 % en seance (degagements) malgre l'exposition datacenters ; socle structurel d'electrification intact.","media":"BFM Bourse","date":"juin 2026","url":"https://www.tradingsat.com/stmicroelectronics-NL0000226223/actualites/stmicroelectronics-les-resultats-explosifs-de-l-americain-micron-165-a-wall-street-relancent-les-groupes-de-semi-conducteurs-en-bourse-stmicro-prend-4-et-soitec-9-1165649.html"}]},
 # --- Autos ---
 "STLAP.PA":{"score":40,"sourced":True,"label":"Negatif structurel / pari redressement","consensus":"75 % Achat, OC moyen 28 € (pari redressement)",
   "points":[{"t":"Tarifs US : 1,6 Md€ de couts nets 2026, marge op. projetee 1-3 % ; dividende suspendu (0 € vs 1,55 €) apres perte nette 22,3 Md€ en 2025.","media":"BFM Bourse","date":"30/04/2026","url":"https://www.tradingsat.com/stellantis-NL00150001Q9/actualites/stellantis-les-droits-de-douane-americains-plombent-l-automobile-en-bourse-1131959.html"},
            {"t":"Lueur T1 2026 : ventes +5 % en Europe, +4 % aux US ; consensus 75 % Achat, OC moyen 28 €.","media":"France-Epargne","date":"T1 2026","url":"https://www.france-epargne.fr/news/stellantis-redressement-t1-2026-ventes-hausse-europe-etats-unis"}]},
 "RNO.PA":{"score":45,"sourced":True,"label":"Mitige (moins expose tarifs)","consensus":"Limite la casse vs Stellantis",
   "points":[{"t":"Absent du marche US, Renault ne perd que ~0,8 % lors des chocs tarifaires, mais reste un 'petit groupe' (CA ~3x inferieur a Stellantis).","media":"Finance Heros / BFM","date":"juin 2026","url":"https://finance-heros.fr/action-renault-avis-analyse/"}]},
 # --- Proxies sectoriels (NON sources individuellement) ---
 "OR.PA":{"score":50,"sourced":False,"basis":"Luxe (cosmetique, plus defensive que le luxe dur)"},
 "CS.PA":{"score":66,"sourced":False,"basis":"Finance/assurance, beneficiaire hausse des taux"},
 "ACA.PA":{"score":66,"sourced":False,"basis":"Banque, beneficiaire hausse des taux"},
 "ENX.PA":{"score":66,"sourced":False,"basis":"Bourse (Euronext), profite des volumes et de la volatilite"},
 "EL.PA":{"score":56,"sourced":False,"basis":"Sante/optique, profil defensif"},
 "ERF.PA":{"score":56,"sourced":False,"basis":"Sante/diagnostics, defensif"},
 "CAP.PA":{"score":48,"sourced":False,"basis":"Services IT, pression sur les multiples (taux) vs tailwind IA"},
 "DSY.PA":{"score":50,"sourced":False,"basis":"Logiciel, sensible aux taux longs"},
 "ML.PA":{"score":44,"sourced":False,"basis":"Pneus, un cran au-dessus des constructeurs mais cycle auto faible"},
 "DG.PA":{"score":50,"sourced":False,"basis":"Concessions resilientes vs sensibilite taux du BTP"},
 "FGR.PA":{"score":48,"sourced":False,"basis":"BTP/concessions, sensible aux taux"},
 "EN.PA":{"score":48,"sourced":False,"basis":"BTP/medias, sensible aux taux"},
 "SGO.PA":{"score":46,"sourced":False,"basis":"Materiaux de construction, sensible au cycle/taux"},
 "LR.PA":{"score":54,"sourced":False,"basis":"Infrastructures electriques, demande structurelle"},
 "AI.PA":{"score":56,"sourced":False,"basis":"Gaz industriels, profil defensif"},
 "MT.PA":{"score":44,"sourced":False,"basis":"Siderurgie cyclique, exposee couts energie"},
 "BN.PA":{"score":54,"sourced":False,"basis":"Agroalimentaire defensif"},
 "RI.PA":{"score":46,"sourced":False,"basis":"Spiritueux, exposition Chine, conso premium molle"},
 "CA.PA":{"score":52,"sourced":False,"basis":"Distribution, defensive"},
 "AC.PA":{"score":56,"sourced":False,"basis":"Hotellerie, voyage resilient"},
 "PUB.PA":{"score":50,"sourced":False,"basis":"Communication, cycle publicitaire incertain"},
 "ENGI.PA":{"score":46,"sourced":False,"basis":"Utility, sensible aux taux"},
 "VIE.PA":{"score":46,"sourced":False,"basis":"Utility (eau/dechets), sensible aux taux"},
 "ORA.PA":{"score":50,"sourced":False,"basis":"Telecom defensif, dette sensible aux taux"},
 "BVI.PA":{"score":48,"sourced":False,"basis":"Certification, industriel sensible au cycle"},
 "URW.PA":{"score":36,"sourced":False,"basis":"Fonciere, vent de face direct de la remontee des taux"},
}

# ---- PERSPECTIVES CT / MT / LT (actifs majeurs + univers) ----
PERSP_UNIVERS = {
 "Actions CAC 40": {
   "ct":"Indice volatil autour de 8 000-8 400 pts, dicte par la geopolitique (Iran, petrole) ; rotation defense/banques/energie en tete, luxe et autos a la traine.",
   "mt":"Saison de resultats sous le signe de la hausse BCE : banques favorisees, marges sous pression d'energie ailleurs ; dispersion sectorielle elevee.",
   "lt":"Profil structurel luxe + industrie/defense ; tech sous-representee. Sensibilite aux taux longs et a la stabilite politique francaise."},
 "Crypto": {
   "ct":"Marche en correction (pire mois, ~4,3 Md$ de sorties ETF) ; BTC teste 60 000 $, SOL teste 68 $.",
   "mt":"Rotation des capitaux institutionnels BTC/ETH -> SOL/XRP/HYPE ; sensibilite forte au regime de taux et au risk-off.",
   "lt":"Theme structurel (DeFi, RWA, ETF) intact, mais classe d'actifs a beta eleve, penalisee par un cout du capital plus eleve."},
}

PERSPECTIVES = {
 "BTC":{"ct":"Tendance baissiere, momentum faible (RSI ~33) ; 60 000 $ = support psychologique cle.","mt":"Sous pression macro (Fed au biais haussier, sorties ETF) ; rebond conditionne a un retour de l'appetit pour le risque.","lt":"Actif structurant de la classe crypto, mais beta eleve face au cout du capital."},
 "ETH":{"ct":"Baissier, ne capte pas la rotation ; structure technique degradee.","mt":"Surveille la dynamique L2/staking ; reste a la traine du BTC et du SOL.","lt":"Plateforme de reference des smart contracts, mais concurrence accrue (SOL)."},
 "SOL":{"ct":"Plus resilient que BTC/ETH mais teste 68 $ ; momentum neutre.","mt":"Entrees ETF + activite on-chain (DeFi/RWA) = force relative.","lt":"Gagnant de la rotation intra-crypto si l'execution technique se confirme."},
 "HYPE":{"ct":"Tendance encore constructive, mais donnee ADX/ATR indisponible (pas d'OHLC).","mt":"Favorise par la rotation institutionnelle ; jeune actif, volatilite elevee.","lt":"Pari sur l'adoption de l'ecosysteme Hyperliquid ; historique court, a surveiller."},
 "MC.PA":{"ct":"Tendance molle, sous MM cles ; rebond technique fragile.","mt":"Consensus acheteur (OC ~647 €) mais objectifs revus en baisse (Berenberg) ; rebond suspendu a la Chine.","lt":"Leader mondial du luxe, pricing power intact malgre le trou d'air cyclique."},
 "RMS.PA":{"ct":"Sous pression (plus forte contribution baissiere au CAC le 22/06).","mt":"Objectifs abaisses ; valorisation premium = peu de marge d'erreur.","lt":"Modele d'ultra-luxe le plus resilient du secteur sur longue periode."},
 "KER.PA":{"ct":"Tendance fragile, momentum neutre.","mt":"Redressement de Gucci incertain ; decote vs juste prix estime.","lt":"Pari de retournement ; execution de la relance de marque a prouver."},
 "TTE.PA":{"ct":"Technique faible (RSI ~25) malgre un contexte petrole porteur : divergence a surveiller.","mt":"Resultats T1 solides, consensus favorable (OC jusqu'a 93 €) ; risque de surproduction (AIE).","lt":"Major integree avec pivot bas-carbone (~3-4 Md$/an) ; rendement actionnaire eleve."},
 "AIR.PA":{"ct":"Tendance haussiere, momentum sain.","mt":"Cycle aero civil + defense porteur ; points d'entree exigeants (valorisation).","lt":"Duopole mondial, carnet pluriannuel ; visibilite structurelle elevee."},
 "SAF.PA":{"ct":"Haussier, momentum solide (RSI ~62).","mt":"Apres-marche moteurs tres rentable ; valorisation deja riche.","lt":"Position dominante motoriste ; budgets defense soutiennent la trajectoire."},
 "HO.PA":{"ct":"Technique faible (RSI ~38) en contraste avec un sentiment defense fort : divergence nette.","mt":"Commandes Defense +75 % au T1, carnet 53,3 Md$ ; risque exclusion CAC 40 ESG.","lt":"Souverainete technologique europeenne + budgets OTAN = visibilite LT exceptionnelle."},
 "SAN.PA":{"ct":"Technique faible (RSI ~50, sous MM) alors que le sentiment fondamental est solide : divergence.","mt":"Consensus haussier (OC 97 €, +26 %), Dupixent et pipeline en forte croissance.","lt":"Big pharma defensive, decote de valorisation (PER ~8,75), rendement >5 %."},
 "BNP.PA":{"ct":"Tendance haussiere forte, momentum confirme.","mt":"Beneficiaire direct de la hausse BCE (marges) ; meilleure performance des banques FR en 2026.","lt":"Banque universelle diversifiee, ROE >10 %, retour actionnaire soutenu."},
 "GLE.PA":{"ct":"Haussier fort, momentum solide.","mt":"Forte revalorisation sur 1 an ; levier eleve aux taux et a la restructuration.","lt":"Re-rating en cours si la rentabilite se normalise durablement."},
 "STMPA.PA":{"ct":"Haussier, momentum confirme.","mt":"1re hausse du CAC 2026 (+79 %), contrat AWS, objectifs datacenters releves.","lt":"Cycle semis tire par l'IA ; reste cyclique, sensible a la demande finale."},
 "SU.PA":{"ct":"Tendance haussiere forte malgre des degagements ponctuels.","mt":"Exposition datacenters/electrification ; valorisation a surveiller.","lt":"Gagnant structurel de l'electrification et de l'efficacite energetique."},
 "STLAP.PA":{"ct":"Technique tres faible (RSI ~26), tendance baissiere forte.","mt":"Tarifs US (1,6 Md€), dividende suspendu, marge sous pression ; mais consensus 75 % Achat (OC 28 €) sur pari de redressement.","lt":"Devenu un pari de retournement plutot qu'une valeur de rendement."},
 "RNO.PA":{"ct":"Baissier fort, momentum faible.","mt":"Moins expose aux tarifs US, mais taille mondiale limitee.","lt":"Dependance au cycle europeen et a l'execution de la gamme electrifiee."},
}

# ---- SOURCES (regroupees) ----
SOURCES = {
 "Donnees de marche":[
  ("TradingView (websocket data.tradingview.com) - courbes 1D/4h/1h : actions EURONEXT:* et crypto en EUR (BTCEUR/ETHEUR/SOLEUR/HYPEEUR)","https://www.tradingview.com/"),
  ("TradingView (scanner REST scanner.tradingview.com) - fondamentaux Micro : ROIC, ROE, PER, beta par titre","https://www.tradingview.com/"),
 ],
 "Composition (CAC 40 / SBF 120)":[
  ("Euronext - CAC 40 Index Composition (31/03/2026, top 25)","https://live.euronext.com/sites/default/files/documentation/index-composition/CAC_40_Index_Composition.pdf"),
  ("Euronext - SBF 120 Index Composition (31/03/2026, top 22)","https://live.euronext.com/sites/default/files/documentation/index-composition/SBF_120_Index_Composition.pdf"),
  ("ToutSurMesFinances - composition complete CAC 40 (maj 20/03/2026)","https://www.toutsurmesfinances.com/bourse/a/bourse-de-paris-la-composition-de-l-indice-cac-40"),
  ("EasyBourse - composition SBF 120 (live, 27/06/2026)","https://www.easybourse.com/indice-composition/sbf-120/FR0003999481-25"),
  ("ABC Bourse - cotations SBF 120 (live)","https://www.abcbourse.com/marches/indice_sbf120"),
  ("Euronext - resultats revision CAC 40 juin 2026 (sans changement)","https://www.euronext.com/en/about/media/euronext-press-releases/euronext-announces-june-2026-quarterly-review-results-cac-40"),
 ],
 "Macro":[
  ("BCE - decision de politique monetaire du 11/06/2026","https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260611~4d41bd5e83.fr.html"),
  ("Touteleurope - hausse des taux BCE","https://www.touteleurope.eu/economie-et-social/la-bce-augmente-ses-principaux-taux-directeurs-une-premiere-depuis-trois-ans/"),
  ("Federal Reserve - communique FOMC du 17/06/2026","https://www.federalreserve.gov/newsevents/pressreleases/monetary20260617a.htm"),
  ("CNBC - Fed holds rates June 2026","https://www.cnbc.com/2026/06/17/fed-interest-rate-decision-june-2026.html"),
  ("INSEE - prix a la consommation mai 2026 (+2,4 %)","https://www.insee.fr/fr/statistiques/8997720"),
  ("Eurostat / Agence Europe - inflation zone euro 3,2 % mai 2026","https://agenceurope.eu/en/bulletin/article/13879/28/inflation-estimated-at-32-in-may-2026-in-euro-area"),
 ],
 "Sentiment presse / consensus":[
  ("MSN Finance / Capital-Luxe - luxe CAC 40","https://www.msn.com/fr-fr/finance/autres/lvmh-herm%C3%A8s-et-kering-accumulent-un-net-retard-en-bourse-du-potentiel-sur-les-actions-du-luxe-du-cac-40/ar-AA22WcTb"),
  ("EasyBourse - consensus LVMH","https://www.easybourse.com/action-consensus/lvmh/FR0000121014-25"),
  ("Investing.fr - TotalEnergies & petrole","https://fr.investing.com/news/stock-market-news/totalenergies-seffondre-avec-le-petrole--le-pire-estil-a-venir--3397985"),
  ("Cafe de la Bourse - Thales / defense","https://www.cafedelabourse.com/bourse/action-thales-faut-il-investir"),
  ("Le Journal de la Finance - Airbus/Thales/Safran","https://www.lejournaldelafinance.com/airbus-thales-safran-defense/"),
  ("Zonebourse - consensus Sanofi","https://www.zonebourse.com/cours/action/SANOFI-4698/consensus/"),
  ("XTB / BFM Bourse - banques FR & hausse BCE","https://www.xtb.com/fr/analyses-marches/bourse-bnp-paribas-et-societe-generale-bondissent-de-5"),
  ("BFM Bourse - Stellantis & tarifs douaniers","https://www.tradingsat.com/stellantis-NL00150001Q9/actualites/stellantis-les-droits-de-douane-americains-plombent-l-automobile-en-bourse-1131959.html"),
  ("Usine Nouvelle / BFM - STMicroelectronics & IA","https://www.usinenouvelle.com/electronique-informatique/semi-conducteurs-porte-par-le-developpement-de-lia-stmicro-double-son-objectif-de-chiffre-daffaires-pour-2026-dans-les-datacenters.UOP3E6LCCZH77BS5MHMS2IPAUE.html"),
  ("ActuCrypto - flux ETF crypto juin 2026","https://actucrypto.info/etf/etf-crypto-sorties-bitcoin-ethereum-solana-hype/"),
  ("MoneyVox - journal de la bourse 22/06/2026","https://www.moneyvox.fr/bourse/actualites/109381/prudence-pour-le-cac-40-chute-de-hermes-le-journal-de-la-bourse-du-22-juin-2026"),
 ],
}

# ---- Sentiment proxy par secteur macro (pour les valeurs non sourcees individuellement, SBF120) ----
SECTOR_SENT_DEFAULT = {
 "Energie":58, "Defense & Aero":64, "Banques & Assurance":66, "Electrification & Industrie":56,
 "Construction & Infra":47, "Luxe":47, "Automobile":40, "Sante":56, "Conso de base":50,
 "Conso discretionnaire & Services":50, "Utilities":46, "Materiaux":48, "Technologie":52,
 "Telecoms":48, "Immobilier":38, "Crypto":40,
}

MACRO_TODAY = {
 "bce":"BCE : hausse de +25 pb le 11/06/2026 -> taux de depot 2,25 %, refi 2,40 %, facilite de pret marginal 2,65 % (effet 17/06). 1re hausse depuis 2023, motivee par le choc energetique lie au conflit au Moyen-Orient.",
 "fed":"Fed : maintien a 3,50-3,75 % le 17/06/2026 (1re reunion du president Warsh) ; biais d'assouplissement retire, dot median fin 2026 releve a 3,8 % (au moins une hausse anticipee), marche pricant une hausse possible des octobre.",
 "infla":"Inflation : France +2,4 % sur un an en mai 2026 (IPCH 2,8 %) ; zone euro 3,2 % (plus haut depuis sept. 2023), tiree par l'energie (+10,9 %, gaz) sur fond de tensions au Moyen-Orient.",
 "cycle":"Cycle : activite jugee 'solide' par la Fed mais incertitude elevee ; en zone euro, inflation au-dessus de la cible et politique monetaire redevenue restrictive. Petrole Brent ~80 $ (19/06).",
 "agenda":"Agenda semaine 29/06-03/07/2026 (a verifier le jour J sur un calendrier macro) : estimations d'inflation zone euro (Eurostat, fin de mois), indices PMI manufacturiers, et cote US donnees d'emploi de debut de mois. Verifie les horaires/publications avant d'agir.",
}
