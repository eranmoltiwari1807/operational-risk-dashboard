# Fixed Operational Risk Dashboard Code

python
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# =========================
# 🎨 CLEAN THEME-SAFE STYLE
# =========================
st.markdown("""
<style>

.block-container {
    padding:2rem;
}

.card {
    background-color: var(--background-color);
    color: var(--text-color);
    padding:18px;
    border-radius:14px;
    border:1px solid rgba(128,128,128,0.2);
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

.kpi {
    padding:18px;
    border-radius:14px;
    text-align:center;
    border:1px solid rgba(128,128,128,0.2);
}

table {
    border-collapse: collapse;
    width: 100%;
}

th {
    background-color: rgba(128,128,128,0.15);
    padding: 10px;
    text-align: left;
    font-weight:600;
}

td {
    padding: 10px;
}

tr:hover {
    background-color: rgba(128,128,128,0.08);
}

p {
    color: var(--text-color);
}

</style>
""", unsafe_allow_html=True)

GREEN = "#22C55E"
ORANGE = "#F59E0B"
RED = "#EF4444"

# =========================
# HEADER
# =========================
st.markdown("<h1 style='text-align:center;'>🧠 Operational Risk Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Anmol Tiwari | NFR | Operational Resilience</p>", unsafe_allow_html=True)

st.markdown(
"<p style='text-align:center; font-size:13px; color:gray; max-width:800px; margin:auto;'>"
"Market data is sourced from Yahoo Finance, and operational risk indicators are derived using proxy models based on volatility."
"</p>", unsafe_allow_html=True
)

st.divider()

# =========================
# INPUT
# =========================
user_input = st.text_input("Enter Company or Ticker", "AAPL")


def resolve_ticker(x):
    mapping = {
        "apple": "AAPL",
        "tesla": "TSLA",
        "microsoft": "MSFT",
        "citi": "C",
        "citigroup": "C",
        "sap": "SAP.DE",
        "bmw": "BMW.DE",
        "siemens": "SIE.DE"
    }
    return mapping.get(x.lower().strip(), x.upper())


# Resolve ticker
ticker = resolve_ticker(user_input)

st.caption(f"🔎 Using ticker: {ticker}")

# =========================
# MAIN
# =========================
if ticker:

    data = yf.download(ticker, period="6mo")

    if data.empty:
        st.error("Invalid ticker")
        st.stop()

    data.columns = data.columns.get_level_values(0)

    ticker_obj = yf.Ticker(ticker)

    # =========================
    # SAFE INFO FETCH
    # =========================
    try:
        info = ticker_obj.info
    except:
        info = {
            "longName": ticker,
            "sector": "N/A",
            "country": "N/A",
            "longBusinessSummary": "Company information temporarily unavailable due to Yahoo Finance rate limits.",
            "marketCap": 0
        }

    name = info.get("longName", ticker)
    sector = info.get("sector", "N/A")
    country = info.get("country", "N/A")

    # =========================
    # PROFILE
    # =========================
    col1, col2 = st.columns([1,2])

    with col1:
        st.markdown(f"""
        <div class="card">
        <h3>{name}</h3>
        <p><b>Sector:</b> {sector}</p>
        <p><b>Country:</b> {country}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        summary = info.get("longBusinessSummary", "No data")

        st.markdown(f"""
        <div class="card">
        <p>
        {summary}
        </p>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # CALCULATIONS
    # =========================
    data["Returns"] = data["Close"].pct_change()
    volatility = data["Returns"].std() * 100
    data["MA30"] = data["Close"].rolling(30).mean()

    trend = "Upward 📈" if data["Close"].iloc[-1] > data["Close"].iloc[0] else "Downward 📉"

    ict = int(volatility * 2)
    downtime = round(volatility * 1.5, 2)
    control = max(0, 100 - volatility * 2)

    score = round(volatility * 0.6 + ict * 0.3, 2)

    if score < 2:
        level = "Low"
    elif score < 4:
        level = "Medium"
    else:
        level = "High"

    # =========================
    # ALERT
    # =========================
    if level == "High":
        st.error("🚨 HIGH RISK")
    elif level == "Medium":
        st.warning("⚠️ Moderate Risk")
    else:
        st.success("✅ Low Risk")

    # =========================
    # KPI
    # =========================
    k1, k2, k3, k4 = st.columns(4)

    def kpi(title, value, level_type):

        if level_type == "Low":
            color = GREEN
            bg = "#22C55E20"

        elif level_type == "Medium":
            color = ORANGE
            bg = "#F59E0B20"

        else:
            color = RED
            bg = "#EF444420"

        return f"""
        <div class="kpi" style="background:{bg};">
        <p>{title}</p>
        <h2 style="color:{color};">{value}</h2>
        </div>
        """

    k1.markdown(kpi("Risk Score", score, level), unsafe_allow_html=True)
    k2.markdown(kpi("Volatility", f"{volatility:.2f}%", level), unsafe_allow_html=True)
    k3.markdown(kpi("Trend", trend, "Low" if "Upward" in trend else "High"), unsafe_allow_html=True)
    k4.markdown(kpi("Risk Level", level, level), unsafe_allow_html=True)

    # =========================
    # CHART + KRI
    # =========================
    col_left, col_right = st.columns([2,1])

    with col_left:

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            name="Price"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["MA30"],
            name="MA30"
        ))

        fig.update_layout(template="plotly")

        st.plotly_chart(fig, use_container_width=True)

    with col_right:

        st.markdown("### ⚙️ Key Risk Indicators")

        def kri(title, val, color):
            return f"""
            <div class="card" style="border-left:5px solid {color}; margin-bottom:10px;">
            <b>{title}</b><br>{val}
            </div>
            """

        st.markdown(kri("ICT Incidents", ict, RED), unsafe_allow_html=True)
        st.markdown(kri("Downtime", downtime, ORANGE), unsafe_allow_html=True)
        st.markdown(kri("Control Effectiveness", f"{control:.1f}%", GREEN), unsafe_allow_html=True)

    # =========================
    # DORA REGISTER
    # =========================
    st.markdown("### 📋 Dynamic Compliance & DORA Risk Register")

    market_cap = info.get("marketCap", 0)

    if country in ["Germany", "France", "Luxembourg", "Netherlands", "Italy", "Spain"]:
        region = "EU (DORA Applicable)"
    else:
        region = "Non-EU"

    vol_factor = min(3, max(1, int(volatility)))

    if market_cap > 200_000_000_000:
        size_factor = 3
    elif market_cap > 50_000_000_000:
        size_factor = 2
    else:
        size_factor = 1

    risk_df = pd.DataFrame({
        "Framework": ["DORA", "DORA", "GDPR", "Operational", "ICT"],
        "Risk Type": [
            "ICT Third-Party Risk",
            "Operational Resilience Failure",
            "Data Privacy Breach",
            "Business Continuity Failure",
            "Cybersecurity Incident"
        ],
        "Region": [region] * 5,
        "Likelihood": [vol_factor, max(1, vol_factor - 1), 2, 2, vol_factor],
        "Impact": [size_factor, size_factor, 3, 2, size_factor],
        "Control Effectiveness": [
            "Needs Improvement",
            "Effective",
            "Needs Improvement",
            "Effective",
            "Needs Improvement"
        ],
        "Status": [
            "Open",
            "Monitoring",
            "Open",
            "Mitigated",
            "Monitoring"
        ]
    })

    risk_df["Inherent Score"] = risk_df["Likelihood"] * risk_df["Impact"]

    def control_adj(ctrl):
        return 0.5 if ctrl == "Effective" else 0.8

    risk_df["Residual Score"] = risk_df.apply(
        lambda x: x["Inherent Score"] * control_adj(x["Control Effectiveness"]), axis=1
    )

    def classify(score):
        if score >= 6:
            return "High"
        elif score >= 3:
            return "Medium"
        else:
            return "Low"

    risk_df["Risk Level"] = risk_df["Residual Score"].apply(classify)

    def color_tag(val, color):
        return f'<span style="background:{color}20;color:{color};padding:6px 12px;border-radius:12px;font-weight:600;">{val}</span>'

    risk_df["Risk Level"] = risk_df["Risk Level"].apply(
        lambda x: color_tag(x, RED if x == "High" else ORANGE if x == "Medium" else GREEN)
    )

    risk_df["Control Effectiveness"] = risk_df["Control Effectiveness"].apply(
        lambda x: color_tag(x, GREEN if x == "Effective" else ORANGE)
    )

    risk_df["Status"] = risk_df["Status"].apply(
        lambda x: color_tag(x, RED if x == "Open" else ORANGE if x == "Monitoring" else GREEN)
    )

    st.write(risk_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # =========================
    # SUMMARY
    # =========================
    st.markdown("### 🧠 Executive Summary")

    st.info(f"""
    {name} shows a {level} operational risk profile.

    • Volatility: {volatility:.2f}%
    • ICT Incidents: {ict}
    • Control Effectiveness: {control:.1f}%
    """)

# ✅ Your file should end like THIS:

```python id="o95d6y"
# FOOTER
st.markdown("---")
st.markdown("<p style='text-align:center;'>Operational Risk Dashboard</p>", unsafe_allow_html=True)
```

