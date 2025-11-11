from datetime import datetime, timezone
import pyowm
import streamlit as st
from matplotlib import dates as mdates
from matplotlib import pyplot as plt

# -------------- API KEY ----------------
api_key = st.secrets["weather"]["OWM_API_KEY"]

owm = pyowm.OWM(api_key)
mgr = owm.weather_manager()

st.title("Weather Forecaster")
st.write("## *Ayush Singh*")
st.write("### Enter the city name, choose a Temperature unit and a graph type:")

location = st.text_input("Name of The City :", "")
units = st.selectbox("Select Temperature Unit: ", ('celsius', 'fahrenheit'))
graph = st.selectbox("Select Graph Type:", ('Bar Graph', 'Line Graph'))

degree = 'C' if units == 'celsius' else 'F'

def get_temperature():
    """ Get the max and min temperature for the next 5 days """
    forecaster = mgr.forecast_at_place(location, '3h')
    forecast = forecaster.forecast
    days = []
    temp_min = []
    temp_max = []
    
    for weather in forecast:
        day = datetime.fromtimestamp(weather.reference_time(), tz=timezone.utc)
        date = day.date()
        if date not in days:
            days.append(date)
            temp_min.append(None)
            temp_max.append(None)
        temp = weather.temperature(unit=units)['temp']
        if temp_min[-1] is None or temp < temp_min[-1]:
            temp_min[-1] = temp
        if temp_max[-1] is None or temp > temp_max[-1]:
            temp_max[-1] = temp
    return days, temp_min, temp_max

def init_plot(title="Weekly Forecast", ylabel=f"Temperature ({sign}{degree})"):
    """ Initialize the plot and labels """
    fig, ax = plt.subplots()
    ax.set_xlabel('Day')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True)
    return fig, ax

def plot_temperature(ax):
    """ Plot bar graph of min and max temperatures """
    days, temp_min, temp_max = get_temperature()
    days_num = mdates.date2num(days)
    bar_min = ax.bar(days_num-0.25, temp_min, width=0.5, color='#42bff4', label='Min')
    bar_max = ax.bar(days_num+0.25, temp_max, width=0.5, color='#ff5349', label='Max')
    ax.legend(fontsize='x-small')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    return bar_min, bar_max, days_num

def show_max_temp_on_barchart(ax, bar_min, bar_max):
    """ Show min/max temp labels on bars """
    y_max = ax.get_ylim()[1]
    offset = y_max * 0.1
    for bars in [bar_min, bar_max]:
        for bar in bars:
            height = bar.get_height()
            xpos = bar.get_x() + bar.get_width()/2.0
            ypos = height - offset
            ax.text(xpos, ypos, f"{int(height)}{sign}", ha='center', va='bottom', color='white')

def plot_line_graph_temp():
    st.write("_____________________________________")
    st.title("5 Day Min and Max Temperature")
    fig, ax = init_plot()
    days, temp_min, temp_max = get_temperature()
    days_num = mdates.date2num(days)
    ax.plot(days_num, temp_min, label='Min', color='#42bff4', marker='o')
    ax.plot(days_num, temp_max, label='Max', color='#ff5349', marker='o')
    ax.legend(fontsize='x-small')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    st.pyplot(fig)

def weather_forecast():
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    icon = weather.weather_icon_url(size='4x')
    temp = weather.temperature(unit=units)['temp']
    temp_felt = weather.temperature(unit=units)['feels_like']
    st.image(icon, caption=(weather.detailed_status).title())
    st.markdown(f"## 🌡️ Temperature: **{round(temp)}{sign}{degree}**")
    st.write(f"### Feels Like: {round(temp_felt)}{sign}{degree}")
    st.write(f"### ☁️ Clouds Coverage: {weather.clouds}%")
    st.write(f"### 💨 Wind Speed: {weather.wind()['speed']} m/s")
    st.write(f"### 💧 Humidity: {weather.humidity}%")
    st.write(f"### ⏲️ Pressure: {weather.pressure['press']} mBar")
    visibility = weather.visibility(unit='kilometers')
    st.write(f"### 🛣️ Visibility: {visibility} km")

def upcoming_weather_alert():
    forecaster = mgr.forecast_at_place(location, '3h')
    st.write("_____________________________________")
    st.title("Upcoming Weather Alerts")
    flag = 0
    if forecaster.will_have_clouds(): st.write("### - Cloud Alert ⛅"); flag += 1
    if forecaster.will_have_rain(): st.write("### - Rain Alert 🌧️"); flag += 1
    if forecaster.will_have_snow(): st.write("### - Snow Alert ❄️"); flag += 1
    if forecaster.will_have_hurricane(): st.write("### - Hurricane Alert 🌀"); flag += 1
    if forecaster.will_have_tornado(): st.write("### - Tornado Alert 🌪️"); flag += 1
    if forecaster.will_have_fog(): st.write("### - Fog Alert 🌫️"); flag += 1
    if forecaster.will_have_storm(): st.write("### - Storm Alert 🌩️"); flag += 1
    if flag == 0: st.write("### No Upcoming Alerts!")

def sunrise_sunset():
    st.write("_____________________________________")
    st.title("Sunrise and Sunset")
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    sunrise = datetime.fromtimestamp(int(weather.sunrise_time()), tz=timezone.utc)
    sunset = datetime.fromtimestamp(int(weather.sunset_time()), tz=timezone.utc)
    st.write(f"#### Sunrise Date: {sunrise.date()}")
    st.write(f"### --Sunrise Time: {sunrise.time()}")
    st.write(f"#### Sunset Date: {sunset.date()}")
    st.write(f"### --Sunset Time: {sunset.time()}")

# ---------------- Main ----------------
if __name__ == '__main__':
    if st.button('Submit'):
        if location == '':
            st.warning('Provide a city name!!')
        else:
            try:
                weather_forecast()
                if graph == 'Bar Graph':
                    fig, ax = init_plot("5 Day Min and Max Temperature")
                    bar_min, bar_max, days_num = plot_temperature(ax)
                    show_max_temp_on_barchart(ax, bar_min, bar_max)
                    st.pyplot(fig)
                elif graph == 'Line Graph':
                    plot_line_graph_temp()
                upcoming_weather_alert()
                sunrise_sunset()
            except:
                error1 = NameError(
                    "Location Not Found!!\nTo make search more precise put the city's name, comma, 2-letter country code. Like this one- (city, XY)"
                )
                st.exception(error1)
