import streamlit as st
import requests
import folium
import datetime
import random

from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from folium.plugins import HeatMap

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="SafeReach",
    page_icon="🚨",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main{
    background:#f7f9fc;
}

.block-container{
    padding-top:2rem;
}

.metric{
    background:white;
    padding:15px;
    border-radius:10px;
}

.big-font{
    font-size:28px;
    font-weight:bold;
}

.emergency{
    background:#ff4b4b;
    color:white;
    padding:20px;
    border-radius:15px;
}

</style>
""",unsafe_allow_html=True)

# ---------------------------------------------------
# API KEYS
# ---------------------------------------------------

ORS_API_KEY="YOUR_ORS_KEY"

WEATHER_KEY="YOUR_OPENWEATHER_KEY"

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/2913/2913465.png",
    width=90
)

st.sidebar.title("🚨 SafeReach")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Hospital Finder",
        "Police Finder",
        "Crime Heatmap",
        "AI Risk",
        "Weather",
        "Emergency Guide",
        "SOS"
    ]
)


st.sidebar.markdown("---")

st.sidebar.success("Kakinada Emergency Assistant")

# ---------------------------------------------------
# DATA
# ---------------------------------------------------

hospitals={

"Government General Hospital":[82.2429,16.9868],

"Apollo Hospital":[82.2384,16.9713],

"Medicover Hospital":[82.2361,16.9756],

"Trust Hospital":[82.2403,16.9839],

"Sunrise Hospital":[82.2342,16.9792]

}

police={

"Two Town Police":[82.2490,16.9871],

"Sarpavaram Police":[82.2671,16.9775],

"One Town Police":[82.2454,16.9927],

"Port Police":[82.2550,16.9861]

}

steps={

"Medical":[

"Call 108",

"Provide First Aid",

"Reach nearest hospital"

],

"Accident":[

"Call 112",

"Avoid moving victim",

"Wait for emergency team"

],

"Harassment":[

"Go to public area",

"Call police",

"Share live location"

]

}

# ---------------------------------------------------
# WEATHER
# ---------------------------------------------------

@st.cache_data

def weather():

    try:

        url=f"https://api.openweathermap.org/data/2.5/weather?q=Kakinada&appid={WEATHER_KEY}&units=metric"

        r=requests.get(url)

        d=r.json()

        return{

            "temp":d["main"]["temp"],

            "desc":d["weather"][0]["description"]

        }

    except:

        return{

            "temp":"--",

            "desc":"Unavailable"

        }

# ---------------------------------------------------
# DISTANCE
# ---------------------------------------------------

@st.cache_data

def distance(user,dest):

    url="https://api.openrouteservice.org/v2/directions/driving-car"

    headers={

        "Authorization":ORS_API_KEY,

        "Content-Type":"application/json"

    }

    body={

        "coordinates":[

            user,

            dest

        ]

    }

    try:

        r=requests.post(url,json=body,headers=headers)

        data=r.json()

        d=data["routes"][0]["summary"]["distance"]/1000

        t=data["routes"][0]["summary"]["duration"]/60

        return round(d,2),round(t,1)

    except:

        return 999,999

# ---------------------------------------------------
# AI RISK
# ---------------------------------------------------

def risk_prediction(emergency,weather_desc):

    score=0

    hour=datetime.datetime.now().hour

    if hour<6:

        score+=3

    elif hour>20:

        score+=2

    else:

        score+=1

    if emergency=="Medical":

        score+=2

    elif emergency=="Accident":

        score+=3

    else:

        score+=4

    weather_desc=weather_desc.lower()

    if "rain" in weather_desc:

        score+=3

    elif "cloud" in weather_desc:

        score+=2

    else:

        score+=1

    if score<=4:

        return "🟢 LOW"

    elif score<=7:

        return "🟡 MEDIUM"

    else:

        return "🔴 HIGH"

# ---------------------------------------------------
# LIVE LOCATION
# ---------------------------------------------------

location=get_geolocation()

if location is None:

    st.warning("Allow browser location access.")

    st.stop()

lat=location["coords"]["latitude"]

lon=location["coords"]["longitude"]

user=[lon,lat]

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

if page=="Dashboard":

    st.title("🚨 SafeReach Dashboard")

    col1,col2,col3,col4=st.columns(4)

    w=weather()

    col1.metric("Temperature",f"{w['temp']} °C")

    col2.metric("Weather",w["desc"])

    col3.metric("Latitude",round(lat,4))

    col4.metric("Longitude",round(lon,4))

    st.success("Live location detected")

    st.markdown("---")

    st.subheader("Quick Emergency Numbers")

    c1,c2,c3=st.columns(3)

    c1.error("🚑 Ambulance\n\n108")

    c2.error("👮 Police\n\n100")

    c3.error("☎ Emergency\n\n112")
# ---------------------------------------------------
# HOSPITAL FINDER
# ---------------------------------------------------

elif page == "Hospital Finder":

    st.title("🏥 Nearest Hospital")

    with st.spinner("Finding nearest hospital..."):

        nearest = min(
            hospitals.items(),
            key=lambda x: distance(user, x[1])[0]
        )

        dist, time = distance(user, nearest[1])

    st.success(f"Nearest Hospital: {nearest[0]}")

    col1, col2 = st.columns(2)

    col1.metric("Distance", f"{dist} km")
    col2.metric("Travel Time", f"{time} mins")

    hospital_lat = nearest[1][1]
    hospital_lon = nearest[1][0]

    st.link_button(
        "🗺 Open in Google Maps",
        f"https://www.google.com/maps?q={hospital_lat},{hospital_lon}"
    )

    st.markdown("---")

    st.subheader("Hospital Location")

    hospital_map = folium.Map(
        location=[hospital_lat, hospital_lon],
        zoom_start=15
    )

    folium.Marker(
        [hospital_lat, hospital_lon],
        tooltip=nearest[0],
        icon=folium.Icon(color="red", icon="plus")
    ).add_to(hospital_map)

    folium.Marker(
        [lat, lon],
        tooltip="Your Location",
        icon=folium.Icon(color="blue")
    ).add_to(hospital_map)

    st_folium(hospital_map, width=900, height=500)


# ---------------------------------------------------
# POLICE FINDER
# ---------------------------------------------------

elif page == "Police Finder":

    st.title("👮 Nearest Police Station")

    with st.spinner("Searching nearest police station..."):

        nearest = min(
            police.items(),
            key=lambda x: distance(user, x[1])[0]
        )

        dist, time = distance(user, nearest[1])

    st.success(f"Nearest Police Station: {nearest[0]}")

    col1, col2 = st.columns(2)

    col1.metric("Distance", f"{dist} km")
    col2.metric("Travel Time", f"{time} mins")

    police_lat = nearest[1][1]
    police_lon = nearest[1][0]

    st.link_button(
        "🗺 Open in Google Maps",
        f"https://www.google.com/maps?q={police_lat},{police_lon}"
    )

    st.markdown("---")

    police_map = folium.Map(
        location=[police_lat, police_lon],
        zoom_start=15
    )

    folium.Marker(
        [police_lat, police_lon],
        tooltip=nearest[0],
        icon=folium.Icon(color="green", icon="shield")
    ).add_to(police_map)

    folium.Marker(
        [lat, lon],
        tooltip="Your Location",
        icon=folium.Icon(color="blue")
    ).add_to(police_map)

    st_folium(police_map, width=900, height=500)


# ---------------------------------------------------
# WEATHER PAGE
# ---------------------------------------------------

elif page == "Weather":

    st.title("🌦 Weather Dashboard")

    data = weather()

    col1, col2 = st.columns(2)

    col1.metric(
        "Temperature",
        f"{data['temp']} °C"
    )

    col2.metric(
        "Condition",
        data["desc"].title()
    )

    if "rain" in data["desc"].lower():

        st.warning(
            "⚠ Roads may be slippery. Drive carefully."
        )

    elif "cloud" in data["desc"].lower():

        st.info(
            "☁ Cloudy conditions today."
        )

    else:

        st.success(
            "☀ Weather looks good."
        )


# ---------------------------------------------------
# AI RISK PREDICTION
# ---------------------------------------------------

elif page == "AI Risk":

    st.title("🤖 AI Risk Prediction")

    emergency = st.selectbox(

        "Select Emergency",

        list(steps.keys())

    )

    weather_data = weather()

    prediction = risk_prediction(

        emergency,

        weather_data["desc"]

    )

    st.markdown("---")

    if "HIGH" in prediction:

        st.error(prediction)

    elif "MEDIUM" in prediction:

        st.warning(prediction)

    else:

        st.success(prediction)

    st.markdown("---")

    st.subheader("Risk Factors")

    st.write("✔ Time of Day")

    st.write("✔ Current Weather")

    st.write("✔ Emergency Type")

    st.write("✔ Location Context")


# ---------------------------------------------------
# EMERGENCY GUIDE
# ---------------------------------------------------

elif page == "Emergency Guide":

    st.title("📋 Emergency Safety Guide")

    emergency = st.selectbox(

        "Choose Situation",

        list(steps.keys())

    )

    st.markdown("---")

    st.subheader("Recommended Steps")

    for i, step in enumerate(

        steps[emergency],

        start=1

    ):

        st.write(f"**{i}. {step}**")

    st.markdown("---")

    st.error("Emergency Numbers")

    col1, col2, col3 = st.columns(3)

    col1.metric("Ambulance", "108")

    col2.metric("Police", "100")

    col3.metric("Emergency", "112")
# ---------------------------------------------------
# CRIME HEATMAP
# ---------------------------------------------------

elif page == "Crime Heatmap":

    st.title("🔥 Crime Heatmap")

    st.info(
        "Crime hotspots shown below are simulated for demonstration."
    )

    # ------------------------------------
    # Generate Simulated Crime Data
    # ------------------------------------

    crime_points = []

    center_lat = 16.9891
    center_lon = 82.2475

    for i in range(60):

        crime_points.append([

            center_lat + random.uniform(-0.015,0.015),

            center_lon + random.uniform(-0.015,0.015),

            random.randint(1,5)

        ])

    # ------------------------------------
    # Base Map
    # ------------------------------------

    crime_map = folium.Map(

        location=[lat,lon],

        zoom_start=13,

        control_scale=True

    )

    # ------------------------------------
    # User Marker
    # ------------------------------------

    folium.Marker(

        [lat,lon],

        tooltip="📍 You are here",

        popup="Current Location",

        icon=folium.Icon(

            color="blue",

            icon="user"

        )

    ).add_to(crime_map)

    # ------------------------------------
    # Heat Layer
    # ------------------------------------

    HeatMap(

        crime_points,

        radius=25,

        blur=20,

        min_opacity=0.4

    ).add_to(crime_map)

    # ------------------------------------
    # Random Crime Markers
    # ------------------------------------

    labels = [

        "Vehicle Theft",

        "Robbery",

        "Road Accident",

        "Harassment",

        "Public Disturbance",

        "Pickpocket",

        "Suspicious Activity"

    ]

    for point in crime_points[:15]:

        folium.CircleMarker(

            location=[

                point[0],

                point[1]

            ],

            radius=5,

            color="red",

            fill=True,

            fill_color="red",

            popup=random.choice(labels)

        ).add_to(crime_map)

    # ------------------------------------
    # Display Map
    # ------------------------------------

    st_folium(

        crime_map,

        width=1000,

        height=650

    )

    st.markdown("---")

    # ------------------------------------
    # Statistics
    # ------------------------------------

    st.subheader("📊 Area Safety Statistics")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(

        "Crime Reports",

        random.randint(40,90)

    )

    c2.metric(

        "Accidents",

        random.randint(10,30)

    )

    c3.metric(

        "Police Patrol",

        random.randint(8,18)

    )

    c4.metric(

        "Safety Score",

        f"{random.randint(72,94)}%"

    )

    st.markdown("---")

    # ------------------------------------
    # Safety Level
    # ------------------------------------

    score = random.randint(1,100)

    if score > 70:

        st.success("🟢 Area is currently considered SAFE.")

    elif score > 40:

        st.warning("🟡 Moderate caution advised.")

    else:

        st.error("🔴 High-risk area. Stay alert.")

    st.markdown("---")

    st.subheader("🛡 Safety Recommendations")

    tips = [

        "Avoid isolated roads after dark.",

        "Share your live location with trusted contacts.",

        "Use well-lit streets whenever possible.",

        "Keep emergency numbers accessible.",

        "Avoid displaying valuables in public.",

        "Stay aware of your surroundings.",

        "Prefer public transport during late hours."

    ]

    for tip in tips:

        st.write("✅", tip)
