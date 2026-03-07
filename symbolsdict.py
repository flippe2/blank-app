#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package d'indices boursiers et ETF pour banque privée suisse.
Ce module contient les définitions des actions SMI, DAX, FTSE, CAC40
et des ETF recommandés par les banques privées suisses.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os

do_download = True
do_daily = True

# Dictionnaire des actions Nasdaq (classées par ordre alphabétique)
nasdaq_actions = [
    {"symbol": "AAPL", "nom": "Apple Inc.", "secteur": "Technologie", "capitalisation_usd": 3500e9},
    {"symbol": "ADBE", "nom": "Adobe Inc.", "secteur": "Technologie", "capitalisation_usd": 220e9},
    {"symbol": "ADI", "nom": "Analog Devices Inc.", "secteur": "Semiconducteurs", "capitalisation_usd": 100e9},
    {"symbol": "ADP", "nom": "Automatic Data Processing Inc.", "secteur": "Services", "capitalisation_usd": 100e9},
    {"symbol": "AMAT", "nom": "Applied Materials Inc.", "secteur": "Semiconducteurs", "capitalisation_usd": 150e9},
    {"symbol": "AMD", "nom": "Advanced Micro Devices Inc.", "secteur": "Semiconducteurs", "capitalisation_usd": 220e9},
    {"symbol": "AMGN", "nom": "Amgen Inc.", "secteur": "Santé", "capitalisation_usd": 140e9},
    {"symbol": "AMZN", "nom": "Amazon.com Inc.", "secteur": "Commerce électronique", "capitalisation_usd": 1800e9},
    {"symbol": "APP", "nom": "AppLovin Corp.", "secteur": "Technologie", "capitalisation_usd": 30e9},
    {"symbol": "ARM", "nom": "Arm Holdings PLC", "secteur": "Semiconducteurs", "capitalisation_usd": 120e9},
    {"symbol": "ASML", "nom": "ASML Holding NV", "secteur": "Semiconducteurs", "capitalisation_usd": 300e9},
    {"symbol": "AVGO", "nom": "Broadcom Inc.", "secteur": "Semiconducteurs", "capitalisation_usd": 600e9},
    {"symbol": "AZN", "nom": "AstraZeneca PLC", "secteur": "Santé", "capitalisation_usd": 210e9},
    {"symbol": "BKNG", "nom": "Booking Holdings Inc.", "secteur": "Voyages", "capitalisation_usd": 120e9},
    {"symbol": "CDNS", "nom": "Cadence Design Systems Inc.", "secteur": "Technologie", "capitalisation_usd": 80e9},
    {"symbol": "CEG", "nom": "Constellation Energy Corp.", "secteur": "Énergie", "capitalisation_usd": 50e9},
    {"symbol": "CMCSA", "nom": "Comcast Corp.", "secteur": "Médias", "capitalisation_usd": 150e9},
    {"symbol": "COST", "nom": "Costco Wholesale Corp.", "secteur": "Distribution", "capitalisation_usd": 350e9},
    {"symbol": "CRWD", "nom": "CrowdStrike Holdings Inc.", "secteur": "Cybersécurité", "capitalisation_usd": 70e9},
    {"symbol": "CSCO", "nom": "Cisco Systems Inc.", "secteur": "Réseaux", "capitalisation_usd": 200e9},
    {"symbol": "DASH", "nom": "DoorDash Inc.", "secteur": "Livraison", "capitalisation_usd": 50e9},
    {"symbol": "GILD", "nom": "Gilead Sciences Inc.", "secteur": "Santé", "capitalisation_usd": 90e9},
    {"symbol": "GOOGL", "nom": "Alphabet Inc. (Class A)", "secteur": "Technologie", "capitalisation_usd": 1700e9},
    {"symbol": "HON", "nom": "Honeywell International Inc.", "secteur": "Industrie", "capitalisation_usd": 130e9},
    {"symbol": "INTC", "nom": "Intel Corp.", "secteur": "Semiconducteurs", "capitalisation_usd": 120e9},
    {"symbol": "INTU", "nom": "Intuit Inc.", "secteur": "Technologie", "capitalisation_usd": 170e9},
    {"symbol": "ISRG", "nom": "Intuitive Surgical Inc.", "secteur": "Santé", "capitalisation_usd": 140e9},
    {"symbol": "KLAC", "nom": "KLA Corp.", "secteur": "Semiconducteurs", "capitalisation_usd": 90e9},
    {"symbol": "LIN", "nom": "Linde PLC", "secteur": "Chimie", "capitalisation_usd": 200e9},
    {"symbol": "LRCX", "nom": "Lam Research Corp.", "secteur": "Semiconducteurs", "capitalisation_usd": 100e9},
    {"symbol": "MELI", "nom": "MercadoLibre Inc.", "secteur": "Commerce électronique", "capitalisation_usd": 80e9},
    {"symbol": "META", "nom": "Meta Platforms Inc.", "secteur": "Médias sociaux", "capitalisation_usd": 1200e9},
    {"symbol": "MSFT", "nom": "Microsoft Corp.", "secteur": "Technologie", "capitalisation_usd": 3000e9},
    {"symbol": "MSTR", "nom": "MicroStrategy Inc.", "secteur": "Technologie/Blockchain", "capitalisation_usd": 25e9},
    {"symbol": "MU", "nom": "Micron Technology Inc.", "secteur": "Semiconducteurs", "capitalisation_usd": 100e9},
    {"symbol": "NFLX", "nom": "Netflix Inc.", "secteur": "Streaming", "capitalisation_usd": 250e9},
    {"symbol": "NVDA", "nom": "NVIDIA Corp.", "secteur": "Semiconducteurs", "capitalisation_usd": 3200e9},
    {"symbol": "PANW", "nom": "Palo Alto Networks Inc.", "secteur": "Cybersécurité", "capitalisation_usd": 100e9},
    {"symbol": "PDD", "nom": "PDD Holdings Inc.", "secteur": "Commerce électronique", "capitalisation_usd": 150e9},
    {"symbol": "PEP", "nom": "PepsiCo Inc.", "secteur": "Consommation", "capitalisation_usd": 230e9},
    {"symbol": "PLTR", "nom": "Palantir Technologies Inc.", "secteur": "Technologie", "capitalisation_usd": 150e9},
    {"symbol": "QCOM", "nom": "Qualcomm Inc.", "secteur": "Semiconducteurs", "capitalisation_usd": 170e9},
    {"symbol": "SBUX", "nom": "Starbucks Corp.", "secteur": "Restauration", "capitalisation_usd": 110e9},
    {"symbol": "SHOP", "nom": "Shopify Inc.", "secteur": "Commerce électronique", "capitalisation_usd": 100e9},
    {"symbol": "SNPS", "nom": "Synopsys Inc.", "secteur": "Technologie", "capitalisation_usd": 80e9},
    {"symbol": "TMUS", "nom": "T-Mobile US Inc.", "secteur": "Télécoms", "capitalisation_usd": 220e9},
    {"symbol": "TSLA", "nom": "Tesla Inc.", "secteur": "Automobile", "capitalisation_usd": 500e9},
    {"symbol": "TXN", "nom": "Texas Instruments Inc.", "secteur": "Semiconducteurs", "capitalisation_usd": 160e9},
    {"symbol": "VRTX", "nom": "Vertex Pharmaceuticals Inc.", "secteur": "Santé", "capitalisation_usd": 110e9},
]

smi_actions = [
    {"rank": 1, "symbol": "NESN.SW", "nom": "Nestlé S.A.", "capitalisation_usd": 264.83e9},
    {"rank": 2, "symbol": "ROG.SW", "nom": "Roche Holding AG", "capitalisation_usd": 221.14e9},
    {"rank": 3, "symbol": "NOVN.SW", "nom": "Novartis AG", "capitalisation_usd": 214.03e9},
    {"rank": 4, "symbol": "ABBN.SW", "nom": "ABB Ltd", "capitalisation_usd": 101.69e9},
    {"rank": 5, "symbol": "UBSG.SW", "nom": "UBS Group AG", "capitalisation_usd": 96.71e9},
    {"rank": 6, "symbol": "CFR.SW", "nom": "Compagnie Financière Richemont SA", "capitalisation_usd": 89.96e9},
    {"rank": 7, "symbol": "ZURN.SW", "nom": "Zurich Insurance Group AG", "capitalisation_usd": 76.43e9},
    {"rank": 8, "symbol": "HOLN.SW", "nom": "Holcim Ltd", "capitalisation_usd": 51.88e9},
    {"rank": 9, "symbol": "SIKA.SW", "nom": "Sika AG", "capitalisation_usd": 46.00e9},
    {"rank": 10, "symbol": "GIVN.SW", "nom": "Givaudan SA", "capitalisation_usd": 44.90e9},
    {"rank": 11, "symbol": "ALC.SW", "nom": "Alcon Inc.", "capitalisation_usd": 44.56e9},
    {"rank": 12, "symbol": "LONN.SW", "nom": "Lonza Group AG", "capitalisation_usd": 40.46e9},
    {"rank": 13, "symbol": "SREN.SW", "nom": "Swiss Re AG", "capitalisation_usd": 35.49e9},
    {"rank": 14, "symbol": "PGHN.SW", "nom": "Partners Group Holding AG", "capitalisation_usd": 35.31e9},
    {"rank": 15, "symbol": "KNIN.SW", "nom": "Kuehne + Nagel International AG", "capitalisation_usd": 34.31e9},
    {"rank": 16, "symbol": "SCMN.SW", "nom": "Swisscom AG", "capitalisation_usd": 29.72e9},
    {"rank": 17, "symbol": "SLHN.SW", "nom": "Swiss Life Holding AG", "capitalisation_usd": 21.24e9},
    {"rank": 18, "symbol": "GEBN.SW", "nom": "Geberit AG", "capitalisation_usd": 20.09e9},
    {"rank": 19, "symbol": "SOON.SW", "nom": "Sonova Holding AG", "capitalisation_usd": 17.45e9},
    {"rank": 20, "symbol": "LOGN.SW", "nom": "Logitech International S.A.", "capitalisation_usd": 14.52e9},
]

dax_actions = [
    {"rank": 1, "symbol": "SAP.DE", "nom": "SAP SE", "capitalisation_usd": 232.81e9},
    {"rank": 2, "symbol": "SIEGY", "nom": "Siemens AG", "capitalisation_usd": 142.39e9}, # Alternative: "SIE.DE"
    {"rank": 3, "symbol": "ALV.DE", "nom": "Allianz SE", "capitalisation_usd": 108.12e9},
#   {"rank": 4, "symbol": "DEU.DE", "nom": "Deutsche Telekom AG", "capitalisation_usd": 107.74e9}, # Alternative: "DTEGY"
    {"rank": 5, "symbol": "AIR.DE", "nom": "Airbus SE", "capitalisation_usd": 107.43e9}, # Note: Airbus est cotée sur plusieurs places
    {"rank": 6, "symbol": "MUV2.DE", "nom": "Münchener Rückversicherungs-Gesellschaft AG", "capitalisation_usd": 62.52e9},
    {"rank": 7, "symbol": "MBG.DE", "nom": "Mercedes-Benz Group AG", "capitalisation_usd": 61.37e9},
    {"rank": 8, "symbol": "BAS.DE", "nom": "BASF SE", "capitalisation_usd": 41.97e9},
    {"rank": 9, "symbol": "VOW3.DE", "nom": "Volkswagen AG (Preference Shares)", "capitalisation_usd": 41.65e9}, # Actions préférentielles, les plus liquides
    {"rank": 10, "symbol": "BMW.DE", "nom": "Bayerische Motoren Werke AG", "capitalisation_usd": 41.58e9},
    {"rank": 11, "symbol": "DB1.DE", "nom": "Deutsche Börse AG", "capitalisation_usd": 39.26e9},
    {"rank": 12, "symbol": "BAYN.DE", "nom": "Bayer AG", "capitalisation_usd": 35.85e9},
    {"rank": 13, "symbol": "IFX.DE", "nom": "Infineon Technologies AG", "capitalisation_usd": 35.13e9},
    {"rank": 14, "symbol": "ADS.DE", "nom": "adidas AG", "capitalisation_usd": 34.85e9},
    {"rank": 15, "symbol": "RWE.DE", "nom": "RWE AG", "capitalisation_usd": 27.47e9},
    {"rank": 16, "symbol": "FRE.DE", "nom": "Fresenius SE & Co. KGaA", "capitalisation_usd": 17.48e9},
    {"rank": 17, "symbol": "HEI.DE", "nom": "Heidelberg Materials AG", "capitalisation_usd": 16.49e9},
    {"rank": 18, "symbol": "SY1.DE", "nom": "Symrise AG", "capitalisation_usd": 16.30e9},
    {"rank": 19, "symbol": "HEN3.DE", "nom": "Henkel AG & Co. KGaA (Preference Shares)", "capitalisation_usd": 14.85e9},
    {"rank": 20, "symbol": "DTG.DE", "nom": "Daimler Truck Holding AG", "capitalisation_usd": 13.93e9}, # Alternative: "MBG.DE" pour l'ancien groupe
    {"rank": 21, "symbol": "MRK.DE", "nom": "Merck KGaA", "capitalisation_usd": 13.79e9},
    {"rank": 22, "symbol": "ZAL.DE", "nom": "Zalando SE", "capitalisation_usd": 13.68e9}, # Note: Zalando est relativement récent dans l'indice
    {"rank": 23, "symbol": "SHL.DE", "nom": "Siemens Healthineers AG", "capitalisation_usd": 12.67e9},
    {"rank": 24, "symbol": "HNR1.DE", "nom": "Hannover Rück SE", "capitalisation_usd": 12.18e9},
    {"rank": 25, "symbol": "BEI.DE", "nom": "Beiersdorf AG", "capitalisation_usd": 11.60e9},
    {"rank": 26, "symbol": "CBK.DE", "nom": "Commerzbank AG", "capitalisation_usd": 11.22e9},
    {"rank": 27, "symbol": "QIA.DE", "nom": "Qiagen N.V.", "capitalisation_usd": 9.61e9},
#   {"rank": 28, "symbol": "CON.DE", "nom": "Continental AG", "capitalisation_usd": 9.32e9},
    {"rank": 29, "symbol": "PUM.DE", "nom": "Puma SE", "capitalisation_usd": 8.63e9},
    {"rank": 30, "symbol": "RAA.DE", "nom": "Rheinmetall AG", "capitalisation_usd": 8.07e9}, # Note: Rheinmetall est entré récemment dans le DAX
    {"rank": 31, "symbol": "FPE3.DE", "nom": "Fuchs Petrolub SE (Preference Shares)", "capitalisation_usd": 5.98e9},
    {"rank": 32, "symbol": "LEG.DE", "nom": "LEG Immobilien SE", "capitalisation_usd": 5.50e9},
    {"rank": 33, "symbol": "TKA.DE", "nom": "thyssenkrupp AG", "capitalisation_usd": 4.82e9},
    {"rank": 34, "symbol": "VNA.DE", "nom": "Vonovia SE", "capitalisation_usd": 4.57e9}, # Note: Vonovia est dans l'immobilier
    {"rank": 35, "symbol": "SDF.DE", "nom": "K+S AG", "capitalisation_usd": 3.86e9},
    {"rank": 36, "symbol": "SAX.DE", "nom": "Sartorius AG (Preference Shares)", "capitalisation_usd": 3.70e9},
    {"rank": 37, "symbol": "SRT3.DE", "nom": "Sartorius Stedim Biotech S.A.", "capitalisation_usd": 3.45e9}, # Note: Cotée aussi à Paris
    {"rank": 38, "symbol": "EVK.DE", "nom": "Evonik Industries AG", "capitalisation_usd": 3.36e9},
#   {"rank": 39, "symbol": "BRN.DE", "nom": "Brenntag SE", "capitalisation_usd": 2.98e9},
    {"rank": 40, "symbol": "HFG.DE", "nom": "HelloFresh SE", "capitalisation_usd": 2.87e9},
]

ftse_actions = [
    {"rank": 1, "symbol": "AZN.L", "nom": "AstraZeneca PLC", "poids_pourcentage": 8.92},
    {"rank": 2, "symbol": "HSBA.L", "nom": "HSBC Holdings PLC", "poids_pourcentage": 8.44},
    {"rank": 3, "symbol": "SHEL.L", "nom": "Shell PLC", "poids_pourcentage": 6.51},
    {"rank": 4, "symbol": "ULVR.L", "nom": "Unilever PLC", "poids_pourcentage": 4.57},
    {"rank": 5, "symbol": "RR.L", "nom": "Rolls-Royce Holdings PLC", "poids_pourcentage": 4.32},
    {"rank": 6, "symbol": "BATS.L", "nom": "British American Tobacco p.l.c.", "poids_pourcentage": 3.60},
    {"rank": 7, "symbol": "GSK.L", "nom": "GSK plc", "poids_pourcentage": 3.43},
    {"rank": 8, "symbol": "RIO.L", "nom": "Rio Tinto PLC", "poids_pourcentage": 2.89},
    {"rank": 9, "symbol": "BP.L", "nom": "BP p.l.c.", "poids_pourcentage": 2.87},
    {"rank": 10, "symbol": "NG.L", "nom": "National Grid PLC", "poids_pourcentage": 2.67},
    {"rank": 11, "symbol": "BARC.L", "nom": "Barclays PLC", "poids_pourcentage": 2.52},
    {"rank": 12, "symbol": "BA.L", "nom": "BAE Systems plc", "poids_pourcentage": 2.40},
    {"rank": 13, "symbol": "LLOY.L", "nom": "Lloyds Banking Group PLC", "poids_pourcentage": 2.36},
    {"rank": 14, "symbol": "GLEN.L", "nom": "Glencore PLC", "poids_pourcentage": 2.03},
    {"rank": 15, "symbol": "NWG.L", "nom": "NatWest Group PLC", "poids_pourcentage": 1.93},
    {"rank": 16, "symbol": "RKT.L", "nom": "Reckitt Benckiser Group PLC", "poids_pourcentage": 1.65},
    {"rank": 17, "symbol": "DGE.L", "nom": "Diageo plc", "poids_pourcentage": 1.58},
    {"rank": 18, "symbol": "REL.L", "nom": "RELX PLC", "poids_pourcentage": 1.55},
    {"rank": 19, "symbol": "AAL.L", "nom": "Anglo American PLC", "poids_pourcentage": 1.50},
    {"rank": 20, "symbol": "LSEG.L", "nom": "London Stock Exchange Group PLC", "poids_pourcentage": 1.48},
    {"rank": 21, "symbol": "HLN.L", "nom": "Haleon plc", "poids_pourcentage": 1.42},
    {"rank": 22, "symbol": "CPG.L", "nom": "Compass Group PLC", "poids_pourcentage": 1.37},
    {"rank": 23, "symbol": "III.L", "nom": "3i Group PLC", "poids_pourcentage": 1.32},
    {"rank": 24, "symbol": "STAN.L", "nom": "Standard Chartered PLC", "poids_pourcentage": 1.25},
    {"rank": 25, "symbol": "SSE.L", "nom": "SSE plc", "poids_pourcentage": 1.23},
    {"rank": 26, "symbol": "TSCO.L", "nom": "Tesco PLC", "poids_pourcentage": 1.22},
    {"rank": 27, "symbol": "PRU.L", "nom": "Prudential plc", "poids_pourcentage": 1.10},
    {"rank": 28, "symbol": "IMB.L", "nom": "Imperial Brands PLC", "poids_pourcentage": 0.96},
    {"rank": 29, "symbol": "EXPN.L", "nom": "Experian plc", "poids_pourcentage": 0.89},
    {"rank": 30, "symbol": "AHT.L", "nom": "Ashtead Group plc", "poids_pourcentage": 0.85},
    {"rank": 31, "symbol": "VOD.L", "nom": "Vodafone Group Public Limited Company", "poids_pourcentage": 0.84},
    {"rank": 32, "symbol": "AV.L", "nom": "Aviva PLC", "poids_pourcentage": 0.75},
    {"rank": 33, "symbol": "CCEP.L", "nom": "Coca-Cola Europacific Partners PLC", "poids_pourcentage": 0.62},
    {"rank": 34, "symbol": "IHG.L", "nom": "InterContinental Hotels Group PLC", "poids_pourcentage": 0.60},
    {"rank": 35, "symbol": "LGEN.L", "nom": "Legal & General Group PLC", "poids_pourcentage": 0.59},
    {"rank": 36, "symbol": "IAG.L", "nom": "International Airlines Group SA", "poids_pourcentage": 0.58},
    {"rank": 37, "symbol": "NXT.L", "nom": "Next plc", "poids_pourcentage": 0.58},
    {"rank": 38, "symbol": "HLMA.L", "nom": "Halma plc", "poids_pourcentage": 0.57},
    {"rank": 39, "symbol": "SMT.L", "nom": "Scottish Mortgage Investment Trust PLC", "poids_pourcentage": 0.53},
]

cac40_actions = [
    {"rank": 1, "symbol": "SU.PA", "nom": "Schneider Electric SE", "poids_pourcentage": 8.28}, # SCHN dans certaines sources [citation:1]
    {"rank": 2, "symbol": "TTE.PA", "nom": "TotalEnergies SE", "poids_pourcentage": 7.13}, # TTEF dans certaines sources [citation:1]
    {"rank": 3, "symbol": "MC.PA", "nom": "LVMH Moët Hennessy Louis Vuitton SE", "poids_pourcentage": 7.09}, # LVMH [citation:1][citation:5]
    {"rank": 4, "symbol": "AIR.PA", "nom": "Airbus SE", "poids_pourcentage": 6.33}, # AIR [citation:1][citation:3]
    {"rank": 5, "symbol": "SAF.PA", "nom": "Safran SA", "poids_pourcentage": 5.86}, # SAF [citation:1][citation:5]
    {"rank": 6, "symbol": "BNP.PA", "nom": "BNP Paribas SA", "poids_pourcentage": 5.38}, # BNPP [citation:1][citation:8]
    {"rank": 7, "symbol": "SAN.PA", "nom": "Sanofi SA", "poids_pourcentage": 5.17}, # SASY dans certaines sources [citation:1]
    {"rank": 8, "symbol": "AI.PA", "nom": "Air Liquide SA", "poids_pourcentage": 4.41}, # L'Air Liquide [citation:1][citation:7]
    {"rank": 9, "symbol": "OR.PA", "nom": "L'Oréal SA", "poids_pourcentage": 4.27}, # L'Oreal [citation:1][citation:4][citation:7]
    {"rank": 10, "symbol": "EL.PA", "nom": "EssilorLuxottica SA", "poids_pourcentage": 4.07}, # ESLX [citation:1][citation:5]
    {"rank": 11, "symbol": "CS.PA", "nom": "AXA SA", "poids_pourcentage": 4.50}, # Données Ramify [citation:8]
    {"rank": 12, "symbol": "DG.PA", "nom": "Vinci SA", "poids_pourcentage": 4.20}, # Estimation
    {"rank": 13, "symbol": "KER.PA", "nom": "Kering SA", "poids_pourcentage": 3.80}, # [citation:6]
    {"rank": 14, "symbol": "CDI.PA", "nom": "Christian Dior SE", "poids_pourcentage": 3.50}, 
    {"rank": 15, "symbol": "RMS.PA", "nom": "Hermès International SCA", "poids_pourcentage": 3.40},
    {"rank": 16, "symbol": "CAP.PA", "nom": "Capgemini SE", "poids_pourcentage": 3.20},
#   {"rank": 17, "symbol": "STM.PA", "nom": "STMicroelectronics NV", "poids_pourcentage": 2.90},
    {"rank": 18, "symbol": "ENGI.PA", "nom": "Engie SA", "poids_pourcentage": 2.80}, # [citation:6]
    {"rank": 19, "symbol": "VIE.PA", "nom": "Veolia Environnement SA", "poids_pourcentage": 2.60}, # [citation:6]
    {"rank": 20, "symbol": "ORA.PA", "nom": "Orange SA", "poids_pourcentage": 2.50},
    {"rank": 21, "symbol": "LR.PA", "nom": "Legrand SA", "poids_pourcentage": 2.40},
    {"rank": 22, "symbol": "SGO.PA", "nom": "Compagnie de Saint-Gobain SA", "poids_pourcentage": 2.30}, # [citation:6][citation:7]
    {"rank": 23, "symbol": "BN.PA", "nom": "Danone SA", "poids_pourcentage": 2.20}, # [citation:4][citation:6][citation:7]
    {"rank": 24, "symbol": "ML.PA", "nom": "Cie Générale des Établissements Michelin SCA", "poids_pourcentage": 2.10}, # [citation:6][citation:7]
    {"rank": 25, "symbol": "ACA.PA", "nom": "Crédit Agricole SA", "poids_pourcentage": 2.00},
    {"rank": 26, "symbol": "GLE.PA", "nom": "Société Générale SA", "poids_pourcentage": 1.90}, # [citation:4][citation:7]
    {"rank": 27, "symbol": "CA.PA", "nom": "Carrefour SA", "poids_pourcentage": 1.80}, # [citation:7]
    {"rank": 28, "symbol": "HO.PA", "nom": "Thales SA", "poids_pourcentage": 1.70}, # [citation:8]
    {"rank": 29, "symbol": "RNO.PA", "nom": "Renault SA", "poids_pourcentage": 1.60}, # [citation:6][citation:7]
    {"rank": 30, "symbol": "EN.PA", "nom": "Bouygues SA", "poids_pourcentage": 1.50}, # [citation:6][citation:8]
    {"rank": 31, "symbol": "AC.PA", "nom": "Accor SA", "poids_pourcentage": 1.40}, # [citation:6]
    {"rank": 32, "symbol": "PUB.PA", "nom": "Publicis Groupe SA", "poids_pourcentage": 1.30},
    {"rank": 33, "symbol": "ERF.PA", "nom": "Eurofins Scientific SE", "poids_pourcentage": 1.20}, # [citation:8]
    {"rank": 34, "symbol": "ATE.PA", "nom": "Alstom SA", "poids_pourcentage": 1.10},
    {"rank": 35, "symbol": "TEP.PA", "nom": "Teleperformance SE", "poids_pourcentage": 1.00}, # [citation:6]
    {"rank": 36, "symbol": "STLAP.PA", "nom": "Stellantis NV", "poids_pourcentage": 0.90}, # [citation:8]
    {"rank": 37, "symbol": "VIV.PA", "nom": "Vivendi SE", "poids_pourcentage": 0.80}, # [citation:8] note: pourrait être sorti selon certaines sources
    {"rank": 38, "symbol": "BVI.PA", "nom": "Bureau Veritas SA", "poids_pourcentage": 0.70}, # [citation:8]
    {"rank": 39, "symbol": "WLN.PA", "nom": "Worldline SA", "poids_pourcentage": 0.60},
    {"rank": 40, "symbol": "URW.PA", "nom": "Unibail-Rodamco-Westfield SE", "poids_pourcentage": 0.50}, # [citation:6]
]

private_banking_etfs = [
    # ===== CORE PORTFOLIO (BASE DU PORTEFEUILLE) =====
    # ETF Actions Monde - Large diversification
    {"categorie": "Core - Monde", "nom": "iShares Core MSCI World UCITS ETF", "symbol": "EUNL.DE", "ter": 0.20, "encours_milliards": 77, "description": "Référence mondiale, 1 500+ valeurs, liquidité exceptionnelle [citation:7]"},
    {"categorie": "Core - Monde", "nom": "Vanguard FTSE All-World UCITS ETF", "symbol": "VWCE.DE", "ter": 0.22, "encours_milliards": 18, "description": "Inclut les marchés émergents, diversification complète [citation:7]"},
    {"categorie": "Core - Monde", "nom": "Amundi MSCI World UCITS ETF", "symbol": "CW8.PA", "ter": 0.38, "encours_milliards": 5.2, "description": "Alternative éligible PEA, track record solide"},
    {"categorie": "Core - Monde", "nom": "SPDR MSCI World UCITS ETF", "symbol": "SWRD.L", "ter": 0.12, "encours_milliards": 1.5, "description": "Frais très compétitifs, réplication physique"},
    
    # ===== EXPOSITION SUISSE (SWISS FINISH) =====
    # Indispensable pour la stabilité et l'exposition au CHF
    {"categorie": "Suisse", "nom": "UBS MSCI Switzerland 20/35 UCITS ETF", "symbol": "CHSPI.SW", "ter": 0.20, "encours_milliards": 2.5, "description": "Meilleur choix pour exposition suisse, frais bas, encours élevé [citation:2][citation:3]"},
    {"categorie": "Suisse", "nom": "iShares SLI UCITS ETF", "symbol": "CSSLI.SW", "ter": 0.51, "encours_milliards": 0.57, "description": "Suit l'indice Swiss Leader Index (30 valeurs) [citation:3]"},
#   {"categorie": "Suisse", "nom": "Xtrackers Swiss Large Cap UCITS ETF", "symbol": "XSC0.DE", "ter": 0.30, "encours_milliards": 1.8, "description": "20 plus grandes capitalisations suisses [citation:3]"},
    {"categorie": "Suisse - ESG", "nom": "UBS MSCI Switzerland IMI Socially Responsible", "symbol": "CHSRI.SW", "ter": 0.28, "encours_milliards": 0.26, "description": "Approche durable, 60+ valeurs suisses [citation:2][citation:3]"},
    
    # ===== EXPOSITION AMÉRIQUE =====
    # Surpondération possible pour saisir le potentiel US
    {"categorie": "USA", "nom": "iShares Core S&P 500 UCITS ETF", "symbol": "CSPX.L", "ter": 0.07, "encours_milliards": 72, "description": "Référence absolue sur le S&P 500, frais minimes"},
    {"categorie": "USA", "nom": "Vanguard S&P 500 UCITS ETF", "symbol": "VUSA.L", "ter": 0.07, "encours_milliards": 51, "description": "Version distribuante du S&P 500"},
    {"categorie": "USA", "nom": "Invesco EQQQ Nasdaq-100 UCITS ETF", "symbol": "EQQU.L", "ter": 0.30, "encours_milliards": 6.4, "description": "Exposition aux géants technologiques"},
    
    # ===== EXPOSITION EUROPE =====
    {"categorie": "Europe", "nom": "Amundi STOXX Europe 600 UCITS ETF", "symbol": "MEUD.PA", "ter": 0.07, "encours_milliards": 5.8, "description": "Frais ultra-compétitifs, large diversification européenne"},
    {"categorie": "Europe", "nom": "iShares Core MSCI Europe UCITS ETF", "symbol": "IMEU.L", "ter": 0.12, "encours_milliards": 9.2, "description": "Alternative solide sur l'Europe"},
    {"categorie": "Europe ex-UK", "nom": "Xtrackers MSCI Europe ex UK UCITS ETF", "symbol": "XMEU.DE", "ter": 0.15, "encours_milliards": 1.1, "description": "Europe sans Royaume-Uni, souvent préféré des banques suisses"},
    
    # ===== MARCHÉS ÉMERGENTS =====
    {"categorie": "Emergents", "nom": "iShares Core MSCI Emerging Markets IMI UCITS ETF", "symbol": "EIMI.L", "ter": 0.18, "encours_milliards": 10.5, "description": "Large exposition aux émergents, small caps incluses"},
    {"categorie": "Emergents", "nom": "Amundi MSCI Emerging Markets UCITS ETF", "symbol": "AEEM.PA", "ter": 0.20, "encours_milliards": 3.2, "description": "Alternative compétitive"},
    {"categorie": "Emergents", "nom": "Xtrackers MSCI Emerging Markets UCITS ETF", "symbol": "XMME.DE", "ter": 0.18, "encours_milliards": 1.8, "description": "Réplication physique"},
    
    # ===== SMALL & MID CAPS =====
    # Pour diversification supplémentaire et potentiel de croissance
    {"categorie": "Small Caps USA", "nom": "iShares MSCI USA Small Cap UCITS ETF", "symbol": "CUSS.L", "ter": 0.35, "encours_milliards": 2.1, "description": "Small caps américaines"},
#   {"categorie": "Small Caps Europe", "nom": "iShares MSCI Europe Small Cap UCITS ETF", "symbol": "IESC.L", "ter": 0.35, "encours_milliards": 1.8, "description": "Small caps européennes"},
#   {"categorie": "Small Caps Suisse", "nom": "UBS MSCI Switzerland Small Cap UCITS ETF", "symbol": "CHSSI.SW", "ter": 0.30, "encours_milliards": 0.35, "description": "Small caps suisses, complément des large caps"},
    
    # ===== SECTEURS SPÉCIFIQUES (SATELLITE) =====
    {"categorie": "Secteur - Santé", "nom": "iShares Healthcare Innovation UCITS ETF", "symbol": "HEAL.L", "ter": 0.40, "encours_milliards": 0.8, "description": "Innovation santé, biotech"},
    {"categorie": "Secteur - Technologie", "nom": "iShares Digitalisation UCITS ETF", "symbol": "DGTL.L", "ter": 0.40, "encours_milliards": 1.2, "description": "Thématique digitalisation"},
#   {"categorie": "Secteur - Luxe", "nom": "Amundi MSCI Europe Consumer Goods", "symbol": "LUX.L", "ter": 0.30, "encours_milliards": 0.5, "description": "Exposition au luxe européen"},
    {"categorie": "Secteur - Infrastructure", "nom": "iShares Global Infrastructure UCITS ETF", "symbol": "INFR.L", "ter": 0.65, "encours_milliards": 0.4, "description": "Infrastructures mondiales"},
    
    # ===== OBLIGATIONS (STABILISATEURS) =====
    # Critiques pour réduire la volatilité du portefeuille [citation:5]
#    {"categorie": "Obligations - Govt CHF", "nom": "iShares Swiss Domestic Government Bond", "symbol": "CH05.SW", "ter": 0.20, "encours_milliards": 1.1, "description": "Obligations d'État suisses en CHF"},
    {"categorie": "Obligations - Govt Global", "nom": "iShares Global Government Bond UCITS ETF", "symbol": "IGLO.L", "ter": 0.25, "encours_milliards": 2.5, "description": "Diversification obligataire mondiale"},
#   {"categorie": "Obligations - Corp EUR", "nom": "iShares Euro Corporate Bond UCITS ETF", "symbol": "IBSE.L", "ter": 0.20, "encours_milliards": 15.3, "description": "Obligations d'entreprises européennes"},
    {"categorie": "Obligations - Corp USD", "nom": "iShares $ Corporate Bond UCITS ETF", "symbol": "LQDE.L", "ter": 0.20, "encours_milliards": 23.1, "description": "Obligations d'entreprises américaines"},
    {"categorie": "Obligations - High Yield", "nom": "iShares Global High Yield Corp Bond", "symbol": "HYLD.L", "ter": 0.55, "encours_milliards": 2.8, "description": "Rendement élevé, risque plus important"},
    
    # ===== THÉMATIQUES DURABLES (ESG) =====
    {"categorie": "ESG - Monde", "nom": "iShares MSCI World SRI UCITS ETF", "symbol": "SUSW.L", "ter": 0.20, "encours_milliards": 5.6, "description": "Sélection ESG stricte sur le monde"},
#   {"categorie": "ESG - USA", "nom": "iShares MSCI USA SRI UCITS ETF", "symbol": "SUSL.L", "ter": 0.15, "encours_milliards": 4.2, "description": "SRI sur les valeurs américaines"},
#   {"categorie": "ESG - Europe", "nom": "iShares MSCI Europe SRI UCITS ETF", "symbol": "SUSE.L", "ter": 0.15, "encours_milliards": 3.8, "description": "SRI sur les valeurs européennes"},
    {"categorie": "ESG - Climat", "nom": "Amundi MSCI World Climate Transition", "symbol": "WCLD.PA", "ter": 0.25, "encours_milliards": 0.6, "description": "Transition climatique"},
    
    # ===== FACTEURS ET STRATÉGIES =====
    {"categorie": "Facteur - Value", "nom": "iShares MSCI World Value Factor", "symbol": "IWVL.L", "ter": 0.30, "encours_milliards": 0.9, "description": "Stratégie value"},
    {"categorie": "Facteur - Momentum", "nom": "iShares MSCI World Momentum Factor", "symbol": "IWMO.L", "ter": 0.30, "encours_milliards": 0.7, "description": "Stratégie momentum"},
    {"categorie": "Dividendes", "nom": "Vanguard FTSE All-World High Dividend Yield", "symbol": "VHYL.L", "ter": 0.29, "encours_milliards": 6.8, "description": "ETF à dividendes élevés"},
#   {"categorie": "Dividendes", "nom": "SPDR S&P Global Dividend Aristocrats", "symbol": "SPYW.L", "ter": 0.45, "encours_milliards": 1.2, "description": "Aristocrates du dividende"},
    
    # ===== IMMOBILIER =====
#   {"categorie": "Immobilier", "nom": "iShares Global REIT UCITS ETF", "symbol": "REIT.L", "ter": 0.24, "encours_milliards": 0.9, "description": "REITs mondiaux"},
#   {"categorie": "Immobilier", "nom": "UBS ETF (CH) SXI Real Estate", "symbol": "UBSRE.SW", "ter": 0.20, "encours_milliards": 0.5, "description": "Immobilier suisse"},
]

# indices for world situation appreciation on daily data

ind_global = [
    {"symbol": "^DJI", "nom": "Dow Jones Industrial Average"},
    {"symbol": "^GSPC", "nom": "S&P 500"},
    {"symbol": "^IXIC", "nom": "Nasdaq Composite"},
    {"symbol": "^RUT", "nom": "Russell 2000"},
    {"symbol": "^FTSE", "nom": "FTSE 100"},
    {"symbol": "^GDAXI", "nom": "DAX Performance Index"},
    {"symbol": "^FCHI", "nom": "CAC 40"},
    {"symbol": "^SSMI", "nom": "Swiss Market Index"},
    {"symbol": "^N225", "nom": "Nikkei 225"},
    {"symbol": "^HSI", "nom": "Hang Seng Index"},
    {"symbol": "000001.SS", "nom": "Shanghai Composite"},
    {"symbol": "^AXJO", "nom": "S&P/ASX 200 Australia"}
]

ind_emergent = [
    {"symbol": "EEM", "nom": "MSCI Emerging Markets ETF"},
    {"symbol": "^BVSP", "nom": "Bovespa Brazil Index"},
    {"symbol": "^NSEI", "nom": "Nifty 50 India"},
    {"symbol": "^KS11", "nom": "KOSPI Composite South Korea"},
    {"symbol": "^TWII", "nom": "Taiwan Weighted Index"}
]

ind_commod = [
    {"symbol": "GC=F", "nom": "Gold Futures"},
    {"symbol": "SI=F", "nom": "Silver Futures"},
    {"symbol": "CL=F", "nom": "Crude Oil WTI Futures"},
    {"symbol": "BZ=F", "nom": "Brent Crude Oil Futures"},
    {"symbol": "NG=F", "nom": "Natural Gas Futures"},
    {"symbol": "HG=F", "nom": "Copper Futures"},
    {"symbol": "ZW=F", "nom": "Wheat Futures"},
    {"symbol": "ZC=F", "nom": "Corn Futures"}
]

ind_macro = [
    {"symbol": "^VIX", "nom": "CBOE Volatility Index"},
    {"symbol": "^TNX", "nom": "US 10 Year Treasury Yield"},
    {"symbol": "^IRX", "nom": "US 3 Month Treasury Yield"},
    {"symbol": "DX-Y.NYB", "nom": "US Dollar Index"},
    {"symbol": "BTC-USD", "nom": "Bitcoin USD"}
]

ind_sector = [
    {"symbol": "^SOX", "nom": "Philadelphia Semiconductor Index"},
    {"symbol": "XLK", "nom": "Technology Select Sector SPDR"},
    {"symbol": "XLE", "nom": "Energy Select Sector SPDR"},
    {"symbol": "ITA", "nom": "US Aerospace and Defense ETF"},
    {"symbol": "XLF", "nom": "Financial Select Sector SPDR"},
    {"symbol": "XLV", "nom": "Health Care Select Sector SPDR"},
    {"symbol": "XLI", "nom": "Industrial Select Sector SPDR"},
    {"symbol": "XLY", "nom": "Consumer Discretionary Select Sector SPDR"},
    {"symbol": "XLP", "nom": "Consumer Staples Select Sector SPDR"}
]


symbols = nasdaq_actions + smi_actions + dax_actions + ftse_actions + cac40_actions + private_banking_etfs
symbols = ind_global + ind_emergent + ind_commod + ind_macro + ind_sector
# symbols = nasdaq_actions


if __name__ == "__main__":
    """
    Si le fichier est exécuté directement (et non importé comme module),
    cette section affiche la liste complète des symboles sur le terminal.
    """
    for s in symbols:
        print(s["symbol"])

    if do_download :
        base_folder = "data/"
        print("downloading to folder", base_folder)

        # Calculer la date de début (7 jours max)
        end_date = datetime.now()
        # 7 jours maximum pour du 1m
        end_date = end_date - timedelta(days=0*7)   # to get older data
        start_date = end_date - timedelta(days=7)   # 7 jours maximum pour du 1m
        print(f"from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        # Créer le dossier racine s'il n'existe pas
        Path(base_folder).mkdir(parents=True, exist_ok=True)
    
        for s in symbols:
            symbol = s["symbol"]
            print(symbol)
            
            # Télécharger les données
            if do_daily :
                df = yf.download(symbol, interval='1d',
                                 auto_adjust=True, progress=False)
                if df.empty:
                    print(f"  ⚠️ Aucune donnée pour {symbol}")
                    continue
                
                # Nettoyer les noms de colonnes
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # Sauvegarder les données du jour
                filename = base_folder + symbol + ".csv"
                df.to_csv(filename)
                    
            else :
                df = yf.download(symbol, interval='1m',
                                 start=start_date, end=end_date,
                                 auto_adjust=True, progress=False)
                if df.empty:
                    print(f"  ⚠️ Aucune donnée pour {symbol}")
                    continue
                
                # Nettoyer les noms de colonnes
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                # Ajouter une colonne avec la date pour faciliter le filtrage
                df['Date'] = df.index.date
                    
                 # Grouper par jour et sauvegarder
                saved_days = 0
                for date, daily_data in df.groupby('Date'):
                    # Convertir la date en string YYYY-MM-DD
                    date_str = date.strftime('%Y-%m-%d')
                    
                    # Créer le sous-dossier pour cette date
                    day_folder = os.path.join(base_folder, date_str)
                    Path(day_folder).mkdir(parents=True, exist_ok=True)
                    
                    # Sauvegarder les données du jour
                    filename = os.path.join(day_folder, f"{symbol}.csv")
                    # Supprimer la colonne Date avant sauvegarde
                    daily_data_without_date = daily_data.drop('Date', axis=1)
                    daily_data_without_date.to_csv(filename)

                    saved_days += 1
                    print(f"{date_str}: {len(daily_data)} lignes")

                # Afficher le dernier prix
                if 'Close' in df.columns:
                    dernier_prix = df['Close'].iloc[-1]
                    if pd.notna(dernier_prix):
                        print(f"{symbol}: {dernier_prix:.2f}")

    print("Terminated")
    


