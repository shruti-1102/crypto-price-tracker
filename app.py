import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

st.set_page_config(page_title="Crypto Price Tracker", layout="wide")

st.sidebar.title("⚙️ Settings")
crypto_options = ['bitcoin', 'ethereum', 'ripple', 'dogecoin']
selected_crypto = st.sidebar.selectbox("Select Cryptocurrency", crypto_options, key="crypto_select")

interval_options = {
    "5 seconds": 5,
    "10 seconds": 10,
    "20 seconds": 20,
    "No Auto-refresh": 0
}
selected_interval_label = st.sidebar.selectbox("Auto-Refresh Interval", list(interval_options.keys()), key="refresh_select")
refresh_interval = interval_options[selected_interval_label]

if refresh_interval > 0:
    st_autorefresh(interval=refresh_interval * 1000, key=f"refresh_{refresh_interval}")

def fetch_crypto_prices(crypto_id):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": crypto_id,
            "order": "market_cap_desc",
            "per_page": 1,
            "page": 1,
            "sparkline": False
        }
        response = requests.get(url, params=params)
        data = response.json()
        df = pd.DataFrame(data)
        if df.empty:
            return None
        return df[['name', 'current_price', 'market_cap', 'price_change_percentage_24h']]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

df = fetch_crypto_prices(selected_crypto)

if df is None or df.empty:
    st.warning("No data available. Try a different selection.")
else:
    st.title(f"📈 {selected_crypto.capitalize()} Live Stats")

    st.metric("Current Price", f"${df['current_price'][0]:,.2f}")
    st.metric("Market Cap", f"${df['market_cap'][0]:,.0f}")
    st.metric("24h Change", f"{df['price_change_percentage_24h'][0]:.2f}%")

    fig = px.bar(df, x='name', y='current_price', title='Current Price')
    st.plotly_chart(fig, use_container_width=True)
