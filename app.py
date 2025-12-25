import streamlit as st
import requests
import json
from streamlit.components.v1 import html

st.set_page_config(page_title="Kakinada People Safety System", layout="wide")

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjRiNGU2M2Q5ZTBmMDRhNjVhNjEwZWEzYWFhMGRjYzBhIiwiaCI6Im11cm11cjY0In0="  # ADD YOUR OPENROUTESERVICE API KEY HERE
OPENWEATHER_API_KEY = "db387806b254dde28cb5eae4f65aad66"  

# Coordinates are approximate and used for demonstration purposes
hospitals = {
    "Government General Hospital (GGH)": [82.2429, 16.9868],
    "Apollo Hospital": [82.2384, 16.9713],
    "Medicover Hospital": [82.2361, 16.9756],
    "Trust Hospital": [82.2403, 16.9839],
    "Sunrise Hospital": [82.2342, 16.9792]
}

police_stations = {
    "Two Town Police Station": [82.2490, 16.9871],
    "Sarpavaram Police Station": [82.2671, 16.9775],
    "One Town Police Station": [82.2454, 16.9927],
    "Port Police Station": [82.2550, 16.9861]
}

emergency_steps = {
    "Medical Emergency": [
        "Call ambulance immediately (108)",
        "Provide first aid if trained",
        "Reach nearest hospital"
    ],
    "Accident": [
        "Ensure personal safety",
        "Call emergency services (112)",
        "Avoid moving injured persons"
    ],
    "Harassment / Threat": [
        "Move to a safe public location",
        "Contact police immediately",
        "Inform trusted contacts"
    ]
}

def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Kakinada&appid={OPENWEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return f"{data['weather'][0]['description'].title()}, {data['main']['temp']} °C"
    except:
        return "Weather data unavailable"

def get_distance(user_loc, dest):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [user_loc, dest]
    }
    res = requests.post(url, json=body, headers=headers).json()
    distance = res["routes"][0]["summary"]["distance"] / 1000
    duration = res["routes"][0]["summary"]["duration"] / 60
    return round(distance, 2), round(duration, 1)

st.title("People Safety & Emergency Assistance – Kakinada")
st.caption("Location-based emergency guidance using open APIs")

location_html = """
<script>
navigator.geolocation.getCurrentPosition(
    (pos) => {
        const data = {
            lat: pos.coords.latitude,
            lon: pos.coords.longitude
        };
        const event = new CustomEvent("streamlit:setComponentValue", {
            detail: JSON.stringify(data)
        });
        window.dispatchEvent(event);
    }
);
</script>
"""

location = html(location_html, height=0)

if location:
    user_data = json.loads(location)
    user_coordinates = [user_data["lon"], user_data["lat"]]

    st.success("Live location detected")

    emergency_type = st.selectbox(
        "Select emergency type",
        list(emergency_steps.keys())
    )

    if st.button("Find Nearest Help"):
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Nearest Hospital", "Nearest Police Station", "Weather", "Safety Instructions"]
        )

        with tab1:
            nearest_hospital = min(
                hospitals.items(),
                key=lambda x: get_distance(user_coordinates, x[1])[0]
            )
            d, t = get_distance(user_coordinates, nearest_hospital[1])
            st.write(nearest_hospital[0])
            st.write(f"Distance: {d} km")
            st.write(f"Estimated travel time: {t} minutes")

        with tab2:
            nearest_police = min(
                police_stations.items(),
                key=lambda x: get_distance(user_coordinates, x[1])[0]
            )
            d, t = get_distance(user_coordinates, nearest_police[1])
            st.write(nearest_police[0])
            st.write(f"Distance: {d} km")
            st.write(f"Estimated travel time: {t} minutes")

        with tab3:
            st.write(get_weather())

        with tab4:
            for step in emergency_steps[emergency_type]:
                st.write(step)

else:
    st.warning("Waiting for location permission from browser")
