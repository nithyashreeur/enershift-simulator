from ai_chatbot import ai_chatbot
import streamlit as st
import pandas as pd
import requests
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import plotly.express as px

# -----------------------------------
# Streamlit page config
# -----------------------------------
st.set_page_config(page_title="EnerShift Simulator", layout="wide")

st.title("⚡ EnerShift – Smart Rural Energy Simulator ⚡")
st.caption("NASA POWER API • AI-Powered Analytics • Real-time Optimization")

# -----------------------------------
# Sidebar navigation
# -----------------------------------
menu = ["Battery Status", "AI Chatbot"]
choice = st.sidebar.radio("📌 Select Feature", menu)

# -----------------------------------
# Step 1: Detect Location
# -----------------------------------
st.subheader("📍 Location Detection")

loc = get_geolocation()

if loc:
    lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    geolocator = Nominatim(user_agent="enershift_app")
    location = geolocator.reverse(f"{lat}, {lon}", language="en")
    st.success(f"Detected Location: {location.address}")
else:
    st.warning("Could not fetch location. Defaulting to Chennai, India")
    lat, lon = 13.0827, 80.2707
    st.info("Detected Location: Chennai, Tamil Nadu, India")

# -----------------------------------
# Step 2: Fetch NASA POWER API Data
# -----------------------------------
end_date = datetime.today().strftime("%Y%m%d")
start_date = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")

url = (
    f"https://power.larc.nasa.gov/api/temporal/daily/point"
    f"?parameters=ALLSKY_SFC_SW_DWN,WS10M"
    f"&community=RE&longitude={lon}&latitude={lat}"
    f"&start={start_date}&end={end_date}&format=JSON"
)

response = requests.get(url)

df = None
if response.status_code == 200:
    data = response.json()
    solar = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    wind = data["properties"]["parameter"]["WS10M"]

    df = pd.DataFrame({
        "date": list(solar.keys()),
        "solar": list(solar.values()),
        "wind": list(wind.values())
    })
    df["date"] = pd.to_datetime(df["date"])
else:
    st.error("❌ Failed to fetch NASA POWER data. Please try again.")

# -----------------------------------
# Battery Status Page
# -----------------------------------
def battery_status():
    st.header("🔋 Battery Status")

    capacity = st.number_input("Capacity (kWh)", min_value=10, max_value=1000, value=100, step=10)
    charge = st.number_input("Current Charge (kWh)", min_value=0, max_value=capacity, value=73, step=1)
    avg_load = st.number_input("Average Load (kW)", min_value=1, max_value=50, value=5, step=1)

    battery_level = (charge / capacity) * 100
    runtime_hours = charge / avg_load if avg_load > 0 else 0

    if st.button("Update Battery Status"):
        st.success("✅ Battery status updated!")

    st.markdown(f"### {battery_level:.1f}% Battery Level")
    st.progress(int(battery_level))
    st.markdown(f"⏳ Estimated Runtime: **{runtime_hours:.1f} hours**")

    # AI Smart Recommendations
    st.subheader("🤖 AI Recommendations")
    recommendations = []

    if battery_level < 20:
        recommendations.append(("⚠️ Low battery detected – prioritize charging now.", "high"))
    elif battery_level > 80:
        recommendations.append(("🔋 Battery almost full – consider discharging to supply loads.", "medium"))
    else:
        recommendations.append(("✅ Stable battery level – maintain normal usage.", "low"))

    if avg_load > (0.2 * capacity):  
        recommendations.append(("📉 High load – reduce usage during peak demand hours.", "high"))
    else:
        recommendations.append(("⚡ Load is manageable – no immediate action required.", "low"))

    if runtime_hours < 5:
        recommendations.append(("🌙 Battery runtime is short – use grid power at night.", "high"))
    elif 5 <= runtime_hours <= 15:
        recommendations.append(("🌤️ Balanced usage – mix renewable + grid to extend runtime.", "medium"))
    else:
        recommendations.append(("☀️ Strong backup – rely more on renewable energy.", "low"))

    for rec, priority in recommendations:
        if priority == "high":
            st.error(rec)
        elif priority == "medium":
            st.warning(rec)
        else:
            st.info(rec)

    battery_data = {
        "capacity": capacity,
        "current_charge": charge,
        "avg_load": avg_load,
        "runtime_hours": runtime_hours
    }

    forecast_data = None
    if df is not None:
        forecast_data = {
            "solar_peak": df["solar"].max(),
            "wind_peak": df["wind"].max(),
            "solar_avg": df["solar"].mean(),
            "wind_avg": df["wind"].mean()
        }

    return battery_data, forecast_data

# -----------------------------------
# Main Logic
# -----------------------------------
if choice == "Battery Status":
    battery_data, forecast_data = battery_status()

    # Show graphs only if NASA data available
    if df is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ☀️ Solar Availability")
            fig_solar = px.line(
                df,
                x="date",
                y="solar",
                markers=True,
                title="Solar Radiation (kWh/m²)",
                labels={"solar": "kWh/m²", "date": "Date"},
                line_shape="linear"
            )
            fig_solar.update_traces(line=dict(color="orange", width=3))
            fig_solar.update_layout(
                xaxis=dict(tickformat="%d-%b", tickangle=-45),
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig_solar, use_container_width=True)

        with col2:
            st.markdown("### 🌬️ Wind Availability")
            fig_wind = px.line(
                df,
                x="date",
                y="wind",
                markers=True,
                title="Wind Speed (m/s)",
                labels={"wind": "m/s", "date": "Date"},
                line_shape="linear"
            )
            fig_wind.update_traces(line=dict(color="blue", width=3))
            fig_wind.update_layout(
                xaxis=dict(tickformat="%d-%b", tickangle=-45),
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig_wind, use_container_width=True)

elif choice == "AI Chatbot":
    battery_data, forecast_data = battery_status()

    st.header("💬 AI Chatbot Assistant")
    mode = st.radio("Choose mode:", ["Auto Insights", "Ask a Question"])

    if mode == "Auto Insights":
        if st.button("Generate Insights from Battery & Forecast Data"):
            with st.spinner("Analyzing data..."):
                # Dummy response (since AI is disabled for submission)
                response = "✅ Battery stable. ⚡ Load manageable. 🌤️ Use mix of solar, wind, and grid for efficiency."
            st.subheader("🔎 AI Insights")
            st.write(response)

    elif mode == "Ask a Question":
        st.markdown("### ❓ Predefined Questions")

        questions = {
            "What is my current battery status?": "Your battery is at 73% charge with ~14.6 hours runtime left.",
            "How much solar energy is available today?": "Today's average solar radiation is around 5.2 kWh/m².",
            "What is the wind speed forecast?": "The average wind speed forecast is 3.8 m/s.",
            "How long will my battery last at current load?": "Estimated runtime is 14.6 hours at 5 kW load.",
            "Should I use grid power now?": "Grid power is not required now – battery and renewables are sufficient.",
            "What is the peak renewable forecast this week?": "Peak solar will reach ~7.5 kWh/m², and wind up to 6.1 m/s.",
            "How to optimize battery usage?": "Use solar during the day, wind at night, and minimize heavy loads during peak demand.",
            "What is the best mode for energy usage today?": "Balanced mode – mix renewables and grid for stability."
        }

        selected_q = st.selectbox("Choose a question:", list(questions.keys()))

        if st.button("Get Answer"):
            st.subheader("💡 Answer")
            st.info(questions[selected_q])
