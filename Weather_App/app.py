from datetime import datetime
import pyowm
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib import dates as mdates

# ------------------ API Key ------------------
# Use Streamlit secrets: set in Streamlit Cloud → Secrets
# [weather]
# OWM_API_KEY = "your_api_key_here"
api_key = st.secrets["weather"]["OWM_API_KEY"]

owm = pyowm.OWM(api_key)
mgr = owm.weather_manager()

st.title("Weather Forecaster")
st.write("## *Made by Aayush with* :heart:")
st.write("### Enter the city name, choose a Temperature unit and a graph type:")

location = st.text_input("Name of The City :", "")
units = st.selectbox("Select Temperature Unit: ", ('celsius', 'fahrenheit'))
graph = st.selectbox("Select Graph Type:", ('Bar Graph', 'Line Graph'))

degree = 'C' if units == 'celsius' else 'F'
sign = u"\N{DEGREE SIGN}"

def get_temperature():
    forecaster = mgr.forecast_at_place(location, '3h')
    forecast = forecaster.forecast

    days, temp_min, temp_max, dates_list = [], [], [], []

    for weather in forecast:
        day = datetime.fromtimestamp(weather.reference_time(), datetime.UTC)
        date = day.date()
        if date not in dates_list:
            dates_list.append(date)
            temp_min.append(None)
            temp_max.append(None)
            days.append(date)

        temp = weather.temperature(unit=units)['temp']
        if not temp_min[-1] or temp < temp_min[-1]:
            temp_min[-1] = temp
        if not temp_max[-1] or temp > temp_max[-1]:
            temp_max[-1] = temp

    return days, temp_min, temp_max

def init_plot(title="Weekly Forecast"):
    fig, ax = plt.subplots()
    ax.set_xlabel('Day')
    ax.set_ylabel(f'Temperature({sign}{degree})')
    ax.set_title(title)
    return fig, ax

def plot_temperature(ax):
    days, temp_min, temp_max = get_temperature()
    days_num = mdates.date2num(days)
    ax.bar(days_num-0.25, temp_min, width=0.5, color='#42bff4', label='Min')
    ax.bar(days_num+0.25, temp_max, width=0.5, color='#ff5349', label='Max')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.legend(fontsize='x-small')
    return ax

def plot_line_graph_temp():
    st.write("_____________________________________")
    st.title("5 Day Min and Max Temperature")
    fig, ax = init_plot()
    days, temp_min, temp_max = get_temperature()
    days_num = mdates.date2num(days)
    ax.plot(days_num, temp_min, label='Min', color='#42bff4', marker='o')
    ax.plot(days_num, temp_max, label='Max', color='#ff5349', marker='o')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.legend(fontsize='x-small')
    st.pyplot(fig)

def weather_forecast():
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    icon = weather.weather_icon_url(size='4x')
    temp = weather.temperature(unit=units)['temp']
    temp_felt = weather.temperature(unit=units)['feels_like']
    st.image(icon, caption=weather.detailed_status.title())
    st.markdown(f"## 🌡️ Temperature: **{round(temp)}{sign}{degree}**")
    st.write(f"### Feels Like: {round(temp_felt)}{sign}{degree}")
    st.write(f"### ☁️ Clouds Coverage: {weather.clouds}%")
    st.write(f"### 💨 Wind Speed: {weather.wind()['speed']} m/s")
    st.write(f"### 💧 Humidity: {weather.humidity}%")
    st.write(f"### ⏲️ Pressure: {weather.pressure['press']} mBar")
    visibility = weather.visibility(unit='kilometers')
    st.write(f"### 🛣️ Visibility: {visibility} km")

if st.button('Submit'):
    if location == '':
        st.warning('Provide a city name!!')
    else:
        try:
            weather_forecast()
            if graph == 'Bar Graph':
                fig, ax = init_plot()
                plot_temperature(ax)
                st.pyplot(fig)
            elif graph == 'Line Graph':
                plot_line_graph_temp()
        except:
            st.exception("Location Not Found!!\nTo make search more precise, put the city's name, comma, 2-letter country code (city, XY)")
