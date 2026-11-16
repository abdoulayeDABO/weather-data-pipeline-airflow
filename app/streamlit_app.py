import math
import os
from sqlalchemy.engine import URL
import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Meteo dashboard", page_icon="🌤️", layout="wide")


# @st.cache_resource
# def get_conn():
#     return st.connection("postgresql", type="sql")


@st.cache_resource
def get_conn():
    url = URL.create(
        "postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=os.environ["POSTGRES_DB"],
    )
    return st.connection(
        "postgresql", type="sql",
        url=url.render_as_string(hide_password=False),
    )

@st.cache_data(ttl="10m")
def load_locations():
    df = get_conn().query("SELECT DISTINCT location FROM weather_daily ORDER BY location;", ttl="10m")
    return df["location"].tolist()


@st.cache_data(ttl="10m")
def load_data(location: str):
    df = get_conn().query(
        """
        SELECT date, avg_temperature, avg_humidity, total_precipitation, max_wind_speed
        FROM weather_daily
        WHERE location = :loc
        ORDER BY date ASC;
        """,
        params={"loc": location},
        ttl="10m",
    )
    df["date"] = pd.to_datetime(df["date"])
    return df


def fmt(value, unit="", decimals=1):
    return "N/A" if pd.isna(value) else f"{value:.{decimals}f}{unit}"


def delta(today_val, prev_val, unit="", decimals=1):
    if pd.isna(today_val) or pd.isna(prev_val):
        return None
    return f"{today_val - prev_val:+.{decimals}f}{unit}"


def date_axis(df):
    """Une graduation par jour (ou tous les N jours si beaucoup de points)."""
    step = max(1, math.ceil(len(df) / 10))
    return alt.Axis(format="%d/%m", tickCount={"interval": "day", "step": step}, labelAngle=0)


# Header
st.header(":blue[Meteo dashboard]")

locations = load_locations()
if not locations:
    st.warning("Aucune donnée disponible.")
    st.stop()

location = st.sidebar.selectbox("Lieu", locations)

data = load_data(location)
if data.empty:
    st.warning("Aucune donnée pour ce lieu.")
    st.stop()

# Options de période adaptées à l'historique disponible
nb_available = (data["date"].max() - data["date"].min()).days + 1
options = ["7 jours"]
if nb_available > 7:
    options.append("30 jours")
if nb_available > 30:
    options.append("Tout")
period = st.sidebar.radio("Période du graphique", options, index=0)

today = data.iloc[-1]
yesterday = data.iloc[-2] if len(data) > 1 else None

st.caption(f"{location} · dernière mise à jour : {today['date']:%d/%m/%Y}")

# Metrics
st.subheader("Indicateurs clés")


def d(col, unit="", decimals=1):
    return None if yesterday is None else delta(today[col], yesterday[col], unit, decimals)


c1, c2, c3, c4 = st.columns(4)
c1.metric("Température", fmt(today["avg_temperature"], " °C"),
          d("avg_temperature", " °C"), border=True, icon=":material/thermostat:")
c2.metric("Humidité", fmt(today["avg_humidity"], " %", 0),
          d("avg_humidity", " %", 0), border=True, icon=":material/water_drop:")
c3.metric("Précipitations", fmt(today["total_precipitation"], " mm"),
          d("total_precipitation", " mm"), delta_color="off", border=True,
          icon=":material/rainy:")
c4.metric("Vent max", fmt(today["max_wind_speed"], " km/h"),
          d("max_wind_speed", " km/h"), delta_color="inverse", border=True,
          icon=":material/air:")

# Charts
st.subheader("Évolution")

# Filtre en jours calendaires (et non en nombre de lignes)
if period == "Tout":
    chart_data = data
else:
    nb_days = 7 if period == "7 jours" else 30
    cutoff = data["date"].max() - pd.Timedelta(days=nb_days - 1)
    chart_data = data[data["date"] >= cutoff]


def line_chart(df, col, title, color):
    return (
        alt.Chart(df)
        .mark_line(point=True, color=color)
        .encode(
            x=alt.X("date:T", title=None, axis=date_axis(df)),
            y=alt.Y(f"{col}:Q", title=title, scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip("date:T", title="Date", format="%d/%m/%Y"),
                     alt.Tooltip(f"{col}:Q", title=title, format=".1f")],
        )
        .properties(height=280)
    )


tab1, tab2, tab3, tab4 = st.tabs(["Température", "Humidité", "Précipitations", "Vent"])

with tab1:
    st.altair_chart(line_chart(chart_data, "avg_temperature", "Température (°C)", "#e4572e"),
                    use_container_width=True)
with tab2:
    st.altair_chart(line_chart(chart_data, "avg_humidity", "Humidité (%)", "#1f77b4"),
                    use_container_width=True)
with tab3:
    bars = (
        alt.Chart(chart_data)
        .mark_bar(color="#4c78a8")
        .encode(
            x=alt.X("yearmonthdate(date):O", title=None,
                    axis=alt.Axis(format="%d/%m", labelAngle=0)),
            y=alt.Y("total_precipitation:Q", title="Précipitations (mm)"),
            tooltip=[alt.Tooltip("date:T", title="Date", format="%d/%m/%Y"),
                     alt.Tooltip("total_precipitation:Q", title="Précipitations (mm)", format=".1f")],
        )
        .properties(height=280)
    )
    st.altair_chart(bars, use_container_width=True)
with tab4:
    st.altair_chart(line_chart(chart_data, "max_wind_speed", "Vent max (km/h)", "#2ca02c"),
                    use_container_width=True)

# Raw data
with st.expander("Voir les données"):
    st.dataframe(data.sort_values("date", ascending=False), use_container_width=True, hide_index=True)