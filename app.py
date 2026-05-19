import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from streamlit_autorefresh import st_autorefresh
from streamlit_folium import st_folium
import folium
from datetime import datetime
import time

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Smart Wearable Dashboard",
    page_icon="📡",
    layout="wide"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=5000, key="refresh")

# =========================================================
# FIREBASE INIT
# =========================================================

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://smart-wearable-mesh-default-rtdb.firebaseio.com/'
            })
        except Exception as e:
            st.error(f"Firebase initialization failed: {str(e)}")
            return None
    return True

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=5)
def load_firebase_data():
    try:
        init_firebase()
        ref = db.reference("/")
        data = ref.get()
        if data is None:
            data = {}
        return data
    except Exception as e:
        st.error(f"⚠️ Firebase Connection Failed")
        st.info("""
        **Error:** Invalid Firebase credentials
        
        **Fix:** Update your firebase_key.json file:
        1. Go to Firebase Console → Project Settings → Service Accounts
        2. Click "Generate New Private Key"
        3. Replace firebase_key.json with the downloaded file
        4. Restart the app
        """)
        return {
            "Node1": {"Heartbeat": 72, "Status": "AWAKE", "Location": {"Lat": 40.7128, "Lon": -74.0060}},
            "Node2": {"Heartbeat": 65, "Status": "SLEEP", "Location": {"Lat": 34.0522, "Lon": -118.2437}},
            "Node3": {"Heartbeat": 80, "Status": "AWAKE", "Location": {"Lat": 41.8781, "Lon": -87.6298}}
        }

data = load_firebase_data()

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* Background */

.stApp {
    background: linear-gradient(to bottom right, #f8fafc, #eef2ff);
}

/* Title */

.title {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 10px;
}

/* Card */

.card {
    background: white;
    padding: 25px;
    border-radius: 24px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    transition: 0.3s;
    border-left: 8px solid #4f46e5;
    min-height: 320px;
    margin-bottom: 20px;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 8px 25px rgba(79,70,229,0.18);
}

/* Disabled Card */

.disabled-card {
    background: #d1d5db;
    padding: 25px;
    border-radius: 24px;
    opacity: 0.7;
    border-left: 8px solid #9ca3af;
    min-height: 320px;
}

/* Node Title */

.node-title {
    font-size: 30px;
    font-weight: bold;
    color: #111827;
    margin-bottom: 20px;
}

/* Metric Box */

.metric-box {
    background: #f8fafc;
    border-radius: 18px;
    padding: 16px;
    margin-top: 16px;
}

/* Metric Label */

.metric-label {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 8px;
}

/* Metric Value */

.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

/* Heartbeat Animation */

.heartbeat {
    animation: pulse 1.2s infinite;
    color: #ef4444;
}

@keyframes pulse {

    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.08);
    }

    100% {
        transform: scale(1);
    }
}

/* Status Pills */

.status-pill {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 700;
}

/* Awake */

.status-pill.awake {
    background: #d1fae5;
    color: #065f46;
}

/* Sleep */

.status-pill.sleep {
    background: #fef3c7;
    color: #92400e;
}

/* Offline */

.status-pill.offline {
    background: #fee2e2;
    color: #991b1b;
}

/* Footer */

.footer {
    text-align: center;
    color: #6b7280;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="title">📡 Smart Wearable Monitoring Dashboard</div>',
    unsafe_allow_html=True
)

st.caption(
    f"Last Updated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# =========================================================
# GRID LAYOUT
# =========================================================

col1, col2 = st.columns(2)

nodes = ["Node1", "Node2", "Node3", "Node4"]

for index, node in enumerate(nodes):

    current_col = col1 if index % 2 == 0 else col2

    with current_col:

        # =================================================
        # DISABLED NODE
        # =================================================

        if node == "Node4":

            with st.container():
                st.markdown(f'<h3 style="color: #999; opacity: 0.6;">🔒 {node}</h3>', unsafe_allow_html=True)
                
                col_hb, col_status = st.columns(2)
                
                with col_hb:
                    st.markdown('<div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background: #e5e7eb; opacity: 0.6;">', unsafe_allow_html=True)
                    st.metric("❤️ Heartbeat", "-- BPM")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_status:
                    st.markdown('<div style="border: 1px solid #d1d5db; border-radius: 8px; padding: 12px; background: #e5e7eb; opacity: 0.6;">', unsafe_allow_html=True)
                    st.metric("Status", "DISABLED")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.info("📍 This node is disabled")

            continue

        # =================================================
        # NODE DATA
        # =================================================

        node_data = data.get(node, {})

        heartbeat = node_data.get("Heartbeat", 0)

        status = node_data.get("Status", "UNKNOWN")

        lat = node_data.get("Location", {}).get("Lat", 0)

        lon = node_data.get("Location", {}).get("Lon", 0)

        last_seen = node_data.get("LastSeen", time.time())

        # =================================================
        # ONLINE / OFFLINE STATUS
        # =================================================

        current_time = time.time()

        if current_time - last_seen > 20:

            status = "OFFLINE"
            status_class = "offline"

        else:

            if "SLEEP" in status.upper():
                status_class = "sleep"

            else:
                status_class = "awake"

        # (Alerts removed per user request)

        # =================================================
        # NODE CARD
        # =================================================

        with st.container():
            st.markdown(f'<h3 style="color: #111827; margin-top: 0; margin-bottom: 20px;">📡 {node}</h3>', unsafe_allow_html=True)
            
            col_hb, col_status = st.columns(2)
            
            with col_hb:
                st.markdown('<div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; background: #f9fafb;">', unsafe_allow_html=True)
                st.metric("❤️ Heartbeat", f"{heartbeat if heartbeat > 0 else '00'} BPM")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_status:
                st.markdown('<div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; background: #f9fafb;">', unsafe_allow_html=True)
                st.metric("Status", status)
                st.markdown('</div>', unsafe_allow_html=True)

            # =================================================
            # LOCATION VIEW
            # =================================================

            if lat == 0 and lon == 0:

                st.info("📍 Location data unavailable for this node.")

            else:

                with st.expander(f"📍 View {node} Location"):

                    st.write(f"Latitude : {lat}")
                    st.write(f"Longitude : {lon}")

                # Dark Theme Map

                m = folium.Map(
                    location=[lat, lon],
                    zoom_start=18,
                    tiles="CartoDB positron"
                )

                # Marker

                folium.Marker(
                    [lat, lon],
                    popup=f"{node} Location",
                    tooltip=node,
                    icon=folium.Icon(
                        color='red',
                        icon='heartbeat',
                        prefix='fa'
                    )
                ).add_to(m)

                # Render Map

                st_folium(m, width=700, height=350)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown("""
<div class="footer">
Realtime Monitoring System • Smart Wearable 
</div>
""", unsafe_allow_html=True)
