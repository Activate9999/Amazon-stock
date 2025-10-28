import streamlit as st
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go
import time


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Amazon Live Stock",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&display=swap');
body {
  background: linear-gradient(135deg, #283E51, #485563) !important;
  font-family: 'Montserrat', sans-serif !important;
}
h1, h2, h3, .main-header, .price-value { font-family: 'Montserrat', sans-serif !important; }
.bg-anim {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh; z-index: -2;
  background: radial-gradient(ellipse at center, #444d60 0%, #232526 80%);
  opacity: 0.8;
  animation: bgpulse 7s ease-in-out infinite alternate;
}
@keyframes bgpulse {
  0% { filter: blur(0px); }
  100% { filter: blur(6px); }
}
.glow-card {
    background: rgba(30,38,70, .95);
    box-shadow: 0 0 32px 5px #FBB03490;
    border-radius: 22px;
    padding: 2em 3em;
    margin: 0 auto 2em auto;
    max-width: 510px;
    text-align: center;
}
.price-value {
    font-size: 4.4rem;
    color: #FBB034;
    font-weight: 800;
    letter-spacing: 3px;
    margin-bottom: 0.3em;
    filter: drop-shadow(0 0 10px #FBB03499);
}
.info-bar {
    display: flex; justify-content: center; gap: 2em; margin-top: 35px;
}
.info-box {
    background: rgba(255,255,255,0.09);
    border-radius: 15px;
    padding: 1em 2em;
    min-width: 134px;
    color: #FFFFFF;
    box-shadow: 0 2px 10px #FBB03430;
}
.metric-label {
    text-transform: uppercase;
    font-size: 0.96em;
    color: #FBB034;
    letter-spacing: 1.2px;
}
.metric-value {
    font-size: 1.58em;
    font-weight: 700;
    color: #FFFDE4;
}
.price-diff-up { color: #38ef7d; font-weight: bold; }
.price-diff-down { color: #ff3232; font-weight: bold; }
.plotly-chart { border-radius:20px; overflow:hidden; }
.clock {
    text-align:center;
    color:#fbb034;
    font-size:1.2em;
    letter-spacing:2px;
    margin-top:2em;
}
@media (max-width: 600px) {
    .glow-card { padding:18px; }
    .info-bar { flex-direction: column; gap: 1em; }
}
</style>
<div class="bg-anim"></div>
""", unsafe_allow_html=True)


# ---------- FETCH DATA ----------
def get_amzn():
    amzn = yf.Ticker("AMZN")
    # 1 minute interval, today's data
    data = amzn.history(period="1d", interval="1m")
    info = amzn.info
    if data.empty: return None
    price = data['Close'].iloc[-1]
    prev = info.get('previousClose', price)
    diff = price - prev
    pct = (diff / prev)*100 if prev else 0
    return {
        "name": info.get("shortName", "Amazon.com, Inc."),
        "price": price,
        "change": diff,
        "pct": pct,
        "high": data["High"].max(),
        "low": data["Low"].min(),
        "volume": int(data["Volume"].iloc[-1]),
        "chart": data
    }

def plot_candle(data):
    fig = go.Figure(go.Candlestick(
        x=data.index,
        open=data["Open"], high=data["High"],
        low=data["Low"], close=data["Close"],
        name='AMZN'
    ))
    fig.update_layout(
        title='AMZN Intraday Price',
        template="plotly_dark",
        xaxis_title=None, yaxis_title=None,
        margin=dict(l=6, r=6, t=25, b=6), height=410,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Montserrat")
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='#FBB034', gridcolor='#232526')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='#232526', gridcolor="#444d60")
    return fig

# ---------- APP UI ----------
def main():
    # HEADER
    st.markdown('<h1 class="main-header" style="color:#FFFDE4;text-shadow:0 2.5px 22px #fbb034aa,0 0px 0px #333;">🟠 Amazon Stock Live Dashboard</h1>', unsafe_allow_html=True)

    amzn = get_amzn()
    if not amzn:
        st.error("Failed to fetch Amazon data (market closed or no data).")
        return
    change_sign = "+" if amzn["change"] >= 0 else "-"
    change_cls = "price-diff-up" if amzn["change"] >= 0 else "price-diff-down"
    st.markdown(f"""
    <div class="glow-card">
        <div style="font-size:1.4em; letter-spacing:1.5px; color:#FFF;">Amazon.com Inc. <b style='color:#fbb034;'>AMZN</b></div>
        <div class="price-value">${amzn["price"]:.2f}</div>
        <span class="{change_cls}">{change_sign}${abs(amzn["change"]):,.2f} ({change_sign}{abs(amzn["pct"]):.2f}%)</span>
    </div>
    """, unsafe_allow_html=True)

    # key metrics row
    st.markdown("""
    <div class="info-bar">
        <div class="info-box">
            <span class="metric-label">High</span><br>
            <span class="metric-value">${:,.2f}</span>
        </div>
        <div class="info-box">
            <span class="metric-label">Low</span><br>
            <span class="metric-value">${:,.2f}</span>
        </div>
        <div class="info-box">
            <span class="metric-label">Volume</span><br>
            <span class="metric-value">{:,}</span>
        </div>
    </div>
    """.format(amzn["high"], amzn["low"], amzn["volume"]), unsafe_allow_html=True)

    # Candlestick chart
    st.plotly_chart(plot_candle(amzn["chart"]), use_container_width=True)

    # Clock
    st.markdown(f'<div class="clock">Last refreshed {datetime.now().strftime("%H:%M:%S")} IST</div>', unsafe_allow_html=True)
    st.info("Market data auto-refreshes every 60 sec.")
    time.sleep(60)
    st.rerun()

if __name__ == "__main__":
    main()
