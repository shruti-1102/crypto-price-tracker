import requests
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st_autorefresh(interval = 10000, limit = None, key = "refresh")

st.sidebar.markdown("### 🔁 Auto-Refresh Settings")

enable_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value= True)

refresh_interval = st.sidebar.selectbox(
    "Refresh interval (seconds)",
    options= [5, 10, 20, 30, 60],
    index= 1
)
refresh_key = f"refresh_{enable_refresh}_{refresh_interval}"

if enable_refresh:
    st_autorefresh(interval= refresh_interval * 1000, limit = None, key = "refresh_key")


def  fetch_crypto_prices(vs_currency = "usd", per_page = 10):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(url, params= params)
    data = response.json()
    df = pd.DataFrame(data)
    return df[['id', 'symbol', 'name', 'current_price', 'market_cap', 'price_change_percentage_24h']]


st.set_page_config(page_title = "Crypto Tracker", layout = "wide")

st.title("📈Real-Time Crypto Price Tracker")
st.markdown("Stay updated with the latest market prices of top cryptocurrencies. Powered by CoinGecko API.")

df = fetch_crypto_prices()

if df is not None:
    st.dataframe(df, use_container_width = True)
else:
    st.error("Failed to fetch data. Try again later.")


if 'price_history' not in st.session_state:
    st.session_state.price_history = {}

coin = st.selectbox("Select a coin to track:", options = ["bitcoin", "ethereum", "solana"])

def fetch_price(coin):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    response = requests.get(url)
    return response.json()[coin]["usd"]

price = fetch_price(coin)
timestamp = datetime.now().strftime("%H:%M:%S")

if coin not in st.session_state.price_history:
    st.session_state.price_history[coin] = pd.DataFrame(columns=["Time", "Price"])

coin_df = st.session_state.price_history[coin]
new_entry = pd.DataFrame({"Time": [timestamp], "Price": [price]})
st.session_state.price_history[coin] = pd.concat([coin_df, new_entry], ignore_index=True).tail(50)

st.line_chart(data = st.session_state.price_history[coin].set_index("Time"))
