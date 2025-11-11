from datetime import datetime
import pyowm
import streamlit as st
from matplotlib import dates
from matplotlib import pyplot as plt

# -------------------- API SETUP --------------------
api_key = "15a6b5f4aa2da0e033dca9bac797f0a1"
sign = u"\N{DEGREE SIGN}"
owm = pyowm.OWM(api_key)
mgr = owm.weather_manager()

# -------------------- STREAMLIT UI --------------------
st.title("Weather Forecaster")
st.write("## *Made by Aayush with* :heart:")
st.write("##")
st.write("### Enter the city name, choose a Temperature unit and a graph type from the bottom:")

location = st.text_input("Name of The City :", "")
units = st.selectbox("Select Temperature Unit: ", ('celsius', 'fahrenheit'))
graph = st.selectbox("Select Graph Type:", ('Bar Graph', 'Line Graph'))

degree = 'C' if units == 'celsius' else 'F'

# -------------------- HELPER FUNCTIONS --------------------

def get_temperature():
    """ Get max and min temperature for the next 5 days """
    forecaster = mgr.forecast_at_place(location, '3h')
    forecast = forecaster.forecast

    days = []
    dates_list = []
    temp_min = []
    temp_max = []

    for weather in forecast:
        day = datetime.utcfromtimestamp(weather.reference_time())
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

    return (days, temp_min, temp_max)


def init_plot():
    """ Initialize matplotlib plot """
    plt.style.use('ggplot')
    plt.figure('PyOWM Weather')
    plt.xlabel('Day')
    plt.ylabel(f'Temperature({sign}{degree})')
    plt.title("Weekly Forecast")


def plot_temperature():
    """ Plot min and max temperatures as a bar graph """
    days, temp_min, temp_max = get_temperature()
    days_num = dates.date2num(days)
    bar_x = plt.bar(days_num-0.25, temp_min, width=0.5, color='#42bff4', label='Min')
    bar_y = plt.bar(days_num+0.25, temp_max, width=0.5, color='#ff5349', label='Max')
    plt.legend(fontsize='x-small')
    return (bar_x, bar_y)


def label_xaxis():
    """ Format x-axis dates """
    days, _, _ = get_temperature()
    days_num = dates.date2num(days)
    plt.xticks(days_num)
    axes = plt.gca()
    xaxis_format = dates.DateFormatter('%m/%d')
    axes.xaxis.set_major_formatter(xaxis_format)


def show_max_temp_on_barchart():
    """ Display max/min temperature values on bars """
    bar_x, bar_y = plot_temperature()
    axes = plt.gca()
    y_max = axes.get_ylim()[1]
    label_offset = y_max * 0.1
    for bar_chart in [bar_x, bar_y]:
        for bar in bar_chart:
            height = bar.get_height()
            xpos = bar.get_x() + bar.get_width()/2.0
            ypos = height - label_offset
            plt.text(xpos, ypos, f"{int(height)}{sign}", ha='center', va='bottom', color='white')


def plot_line_graph_temp():
    """ Plot min and max temperatures as line graph """
    st.write("_____________________________________")
    st.title("5 Day Min and Max Temperature")
    init_plot()
    days, temp_min, temp_max = get_temperature()
    days_num = dates.date2num(days)
    plt.xticks(days_num)
    axes = plt.gca()
    axes.xaxis.set_major_formatter(dates.DateFormatter('%m/%d'))
    plt.plot(days_num, temp_min, label='Min', color='#42bff4', marker='o')
    plt.plot(days_num, temp_max, label='Max', color='#ff5349', marker='o')
    plt.legend(fontsize='x-small')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot(plt.show())


def weather_forcast():
    """ Show current weather """
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    icon = weather.weather_icon_url(size='4x')

    temp = weather.temperature(unit=units)['temp']
    temp_felt = weather.temperature(unit=units)['feels_like']
    st.image(icon, caption=(weather.detailed_status).title())
    st.markdown(f"## 🌡️ Temperature: **{round(temp)}{sign}{degree}**")
    st.write(f"### Feels Like: {round(temp_felt)}{sign}{degree}")
    st.write(f"### ☁️ Clouds Coverage: {weather.clouds}%")
    st.write(f"### 💨 Wind Speed: {weather.wind()['speed']}m/s")
    st.write(f"### 💧 Humidity: {weather.humidity}%")
    st.write(f"### ⏲️ Pressure: {weather.pressure['press']}mBar")
    st.write(f"### 🛣️ Visibility: {weather.visibility(unit='kilometers')}km")


def upcoming_weather_alert():
    """ Show upcoming weather alerts """
    forecaster = mgr.forecast_at_place(location, '3h')
    flag = 0
    st.write("_____________________________________")
    st.title("Upcoming Weather Alerts")
    if forecaster.will_have_clouds():
        st.write("### - Cloud Alert ⛅"); flag += 1
    if forecaster.will_have_rain():
        st.write("### - Rain Alert 🌧️"); flag += 1
    if forecaster.will_have_snow():
        st.write("### - Snow Alert ❄️"); flag += 1
    if forecaster.will_have_hurricane():
        st.write("### - Hurricane Alert 🌀"); flag += 1
    if forecaster.will_have_tornado():
        st.write("### - Tornado Alert 🌪️"); flag += 1
    if forecaster.will_have_fog():
        st.write("### - Fog Alert 🌫️"); flag += 1
    if forecaster.will_have_storm():
        st.write("### - Storm Alert 🌩️"); flag += 1
    if flag == 0:
        st.write("### No Upcoming Alerts!")


def sunrise_sunset():
    """ Show sunrise and sunset times """
    st.write("_____________________________________")
    st.title("Sunrise and Sunset")
    obs = mgr.weather_at_place(location)
    weather = obs.weather
    sunrise = datetime.utcfromtimestamp(int(weather.sunrise_time()))
    sunset = datetime.utcfromtimestamp(int(weather.sunset_time()))
    st.write(f"#### Sunrise Date: {sunrise.date()} -- Time: {sunrise.time()}")
    st.write(f"#### Sunset Date: {sunset.date()} -- Time: {sunset.time()}")


def get_humidity():
    """ Get max humidity for next 5 days """
    days, dates_list, humidity_max = [], [], []
    forecaster = mgr.forecast_at_place(location, '3h')
    forecast = forecaster.forecast
    for weather in forecast:
        day = datetime.utcfromtimestamp(weather.reference_time())
        date = day.date()
        if date not in dates_list:
            dates_list.append(date)
            humidity_max.append(None)
            days.append(date)
        humidity = weather.humidity
        if not humidity_max[-1] or humidity > humidity_max[-1]:
            humidity_max[-1] = humidity
    return days, humidity_max


def plot_humidity_graph():
    """ Plot 5-day humidity graph """
    days, humidity = get_humidity()
    st.write("_____________________________________")
    st.title("Humidity Index of 5 days")
    plt.style.use('ggplot')
    plt.figure('PyOWM Weather')
    plt.bar(dates.date2num(days), humidity, color='#42bff4')
    plt.xlabel('Day')
    plt.ylabel('Humidity (%)')
    plt.title('Humidity Forecast')
    plt.xticks(dates.date2num(days), [d.strftime("%m/%d") for d in days])
    for idx, h in enumerate(humidity):
        plt.text(idx, h*0.9, f"{h}%", ha='center', va='bottom', color='white')
    st.pyplot(plt.show())


def plot_bar_graph_temp():
    st.write("_____________________________________")
    st.title("5 Day Min and Max Temperature")
    init_plot()
    plot_temperature()
    label_xaxis()
    show_max_temp_on_barchart()
    st.pyplot(plt.show())


# -------------------- MAIN --------------------
if __name__ == '__main__':
    if st.button('Submit'):
        if location == '':
            st.warning('Provide a city name!!')
        else:
            try:
                weather_forcast()
                if graph == 'Bar Graph':
                    plot_bar_graph_temp()
                elif graph == 'Line Graph':
                    plot_line_graph_temp()
                upcoming_weather_alert()
                sunrise_sunset()
                plot_humidity_graph()
            except Exception as e:
                st.exception(e)
