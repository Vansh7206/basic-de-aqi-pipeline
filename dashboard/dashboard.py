import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

st.set_page_config(page_title="AQI Dashboard", layout="wide")

ICONS = {
    "Good": "🟢",
    "Moderate": "🟡",
    "Unhealthy for Sensitive Groups": "🟠",
    "Unhealthy": "🔴",
    "Very Unhealthy": "🟣",
    "Hazardous": "🟤",
}


@st.cache_resource
def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
    )
    return create_engine(url)


@st.cache_data(ttl=300)
def load_data():
    return pd.read_sql(
        "SELECT * FROM clean_aqi ORDER BY observed_at", get_engine()
    )


st.title("Air Quality: Mumbai, Delhi, Bengaluru")

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

df = load_data()
if df.empty:
    st.warning("clean_aqi is empty. Run the pipeline first.")
    st.stop()

cities = st.sidebar.multiselect(
    "Cities", sorted(df["city"].unique()), default=sorted(df["city"].unique())
)
df = df[df["city"].isin(cities)]

if df.empty:
    st.info("Select at least one city in the sidebar.")
    st.stop()

latest = df.sort_values("observed_at").groupby("city").tail(1)

st.subheader("Latest reading")
columns = st.columns(len(latest))
for col, (_, row) in zip(columns, latest.iterrows()):
    with col:
        st.metric(row["city"], int(row["us_aqi"]))
        st.write(f"{ICONS.get(row['aqi_category'], '')} {row['aqi_category']}")
        st.caption(f"Observed {row['observed_at']:%d %b, %H:%M}")

st.subheader("US AQI over time")
trend = df.pivot(index="observed_at", columns="city", values="us_aqi")
st.line_chart(trend)

st.subheader("PM2.5 and PM10 right now (µg/m³)")
st.bar_chart(latest.set_index("city")[["pm2_5", "pm10"]])

st.subheader("All pollutants, latest reading")
st.dataframe(latest.drop(columns=["fetched_at"]).reset_index(drop=True))