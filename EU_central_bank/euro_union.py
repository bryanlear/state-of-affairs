from datetime import date, datetime
import pandas as pd
import matplotlib.pyplot as plt
from ecbdata import ecbdata     

START = "2024-01"
END   = date.today().strftime("%Y-%m")

SERIES = {
    # Policy Rates
    "deposit_facility_rate": "FM.D.U2.EUR.4F.KR.DFR.LEV",
    "mro_rate"             : "FM.D.U2.EUR.4F.KR.MRR_FR.LEV",
    "marginal_lending_rate": "FM.D.U2.EUR.4F.KR.MLFR.LEV",
    
    # Inflation and Growth
    "hicp_index"           : "ICP.M.U2.Y.000000.3.INX",
    "gdp_nominal"          : "MNA.Q.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N",
    
    # Labor Market
    "unemployment_rate"    : "LFSI.M.I9.S.UNEHRT.TOTAL0.15_74.T",
    
    # Business and Consumer Surveys
    "economic_sentiment"   : "RTD.M.S0.S.Y_ESIND.F",

    # Foreign Investment (FDI)
    "fdi_liabilities"      : "BPS.Q.N.I9.W1.S1.S1.LE.L.FA.D.FL._Z.EUR._T._X.N.ALL",

    # Exchange Rates
    "eur_eer_nominal_18"   : "EXR.D.E02.EUR.EN00.A",
    "usd_eur_exchange_rate": "EXR.D.USD.EUR.SP00.A",
}

def parse_period(x):
    if 'Q' in str(x):
        # Convert quarterly data (e.g., '2024-Q1' to '2024-01-01')
        year, quarter = x.split('-Q')
        month = (int(quarter) - 1) * 3 + 1
        return f"{year}-{month:02d}-01"
    return x

def fetch(key, name):
    try:
        print(f"\nFetching {name}...")
        raw = ecbdata.get_series(key, start=START, end=END)
    except Exception as e:
        print(f"Could not fetch {name}: {e}")
        return pd.Series(dtype=float)

    idx = "TIME_PERIOD" if "TIME_PERIOD" in raw.columns else "time"
    val = "OBS_VALUE" if "OBS_VALUE" in raw.columns else "value"

    if val not in raw.columns:
        print(f"Warning: Could not find value column ({val}) for {name}")
        return pd.Series(dtype=float)
    
    raw[idx] = raw[idx].apply(parse_period)

    series = (raw
             .rename(columns={val: name})
             .assign(**{idx: pd.to_datetime(raw[idx])})
             .set_index(idx)[name]
             .astype(float)
             .sort_index())
             
    print(f"Got {len(series)} data points for {name}")
    return series

df = pd.concat({n: fetch(k, n) for n, k in SERIES.items()}, axis=1)

plt.figure(figsize=(16, 20))

# Policy Rates
ax1 = plt.subplot(4, 2, 1)
df[["deposit_facility_rate", "mro_rate", "marginal_lending_rate"]].plot(ax=ax1, marker='.')
ax1.set_title("Key ECB Policy Rates")
ax1.set_ylabel("% p.a.")
ax1.grid(True)

# HICP
ax2 = plt.subplot(4, 2, 2)
df["hicp_index"].dropna().plot(ax=ax2, marker='o')
ax2.set_title("HICP All-Items Index (2015 = 100)")
ax2.grid(True)

# GDP and Unemployment
ax3 = plt.subplot(4, 2, 3)
df["gdp_nominal"].dropna().plot(ax=ax3, label="GDP (€ mn)", marker='s')
ax3.set_ylabel("€ million")
ax3.tick_params(axis='y')
ax3.legend(loc="upper left")
ax3.set_title("GDP and Unemployment")
ax3.grid(True)

ax3b = ax3.twinx()
df["unemployment_rate"].dropna().plot(ax=ax3b, ls="--", color="grey", label="Unemployment", marker='o')
ax3b.set_ylabel("% of labour force")
ax3b.tick_params(axis='y')
ax3b.legend(loc="upper right")

# Economic Sentiment
ax4 = plt.subplot(4, 2, 4)
df["economic_sentiment"].dropna().plot(ax=ax4, marker='o')
ax4.set_title("Economic Sentiment Indicator")
ax4.grid(True)

# FDI
ax5 = plt.subplot(4, 2, 5)
df["fdi_liabilities"].dropna().plot(ax=ax5, marker='o', color='purple')
ax5.set_title("FDI Liabilities (€ million)")
ax5.set_ylabel("€ million")
ax5.grid(True)

# Nominal EER-18 (last 6 months)
ax6 = plt.subplot(4, 2, 6)
last_date = df.index.max()
six_months_ago = last_date - pd.DateOffset(months=6)
df_last_6_months = df[df.index >= six_months_ago]
df_last_6_months["eur_eer_nominal_18"].dropna().plot(ax=ax6, marker='.')
ax6.set_title("Nominal EER-18 (Last 6 Months)")
ax6.grid(True)

# USD/EUR Exchange Rate (last 6 months)
ax7 = plt.subplot(4, 2, 7)
df_last_6_months["usd_eur_exchange_rate"].dropna().plot(ax=ax7, marker='.', color='orange')
ax7.set_title("USD/EUR Exchange Rate (Last 6 Months)")
ax7.grid(True)

plt.tight_layout()
plt.show()
