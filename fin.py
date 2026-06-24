import streamlit as st
import pandas as pd
import joblib
import folium
import requests
from datetime import datetime
from streamlit_folium import st_folium

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ARIA · Accident Risk Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #080c10 !important;
    color: #c8d8e8 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stAppViewContainer"]::before {
    content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(0,180,255,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(255,60,60,0.04) 0%, transparent 60%),
        repeating-linear-gradient(0deg, transparent 39px, rgba(0,180,255,0.03) 40px),
        repeating-linear-gradient(90deg, transparent 39px, rgba(0,180,255,0.03) 40px);
}
[data-testid="stMain"]   { position: relative; z-index: 1; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

/* ── HEADER ── */
.aria-header {
    display: flex; align-items: center; gap: 1.5rem;
    padding: 1.5rem 2.5rem;
    background: linear-gradient(135deg,rgba(0,180,255,0.06),rgba(255,60,60,0.04));
    border: 1px solid rgba(0,180,255,0.2); border-left: 4px solid #00b4ff;
    margin-bottom: 2rem; position: relative; overflow: hidden;
}
.aria-header::after {
    content:"ARIA"; position:absolute; right:-10px; top:-20px;
    font-family:'Orbitron',monospace; font-size:6rem; font-weight:900;
    color:rgba(0,180,255,0.04); pointer-events:none; user-select:none;
}
.aria-logo {
    font-family:'Orbitron',monospace; font-size:2.2rem; font-weight:900;
    color:#00b4ff; letter-spacing:0.08em; text-shadow:0 0 20px rgba(0,180,255,0.5); line-height:1;
}
.aria-logo span { color:#ff3c3c; }
.aria-subtitle {
    font-family:'Share Tech Mono',monospace; font-size:0.7rem;
    color:rgba(0,180,255,0.6); letter-spacing:0.2em; text-transform:uppercase; margin-top:0.3rem;
}
.aria-tagline { font-family:'Rajdhani',sans-serif; font-size:1rem; color:rgba(200,216,232,0.5); margin-left:auto; font-weight:300; }

/* ── STATUS PILLS ── */
.status-bar { display:flex; gap:1rem; margin-bottom:2rem; flex-wrap:wrap; }
.status-pill {
    display:inline-flex; align-items:center; gap:0.4rem; padding:0.3rem 0.8rem;
    background:rgba(0,180,255,0.06); border:1px solid rgba(0,180,255,0.15);
    font-family:'Share Tech Mono',monospace; font-size:0.65rem;
    color:rgba(0,180,255,0.7); letter-spacing:0.15em; text-transform:uppercase;
}
.status-pill .dot {
    width:6px; height:6px; border-radius:50%;
    background:#00ff88; box-shadow:0 0 6px #00ff88; animation:pulse-dot 2s infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── SEARCH BAR ── */
.search-wrap {
    display:flex; align-items:stretch; gap:0; margin-bottom:1rem;
    border:1px solid rgba(0,180,255,0.3); background:rgba(0,12,24,0.8);
    position:relative;
}
.search-icon {
    display:flex; align-items:center; padding:0 1rem;
    font-size:0.9rem; color:rgba(0,180,255,0.5);
    border-right:1px solid rgba(0,180,255,0.15);
    font-family:'Share Tech Mono',monospace; letter-spacing:0.1em;
    white-space:nowrap;
}
[data-testid="stTextInput"] { flex:1; }
[data-testid="stTextInput"] > div { background:transparent !important; border:none !important; }
[data-testid="stTextInput"] input {
    background:transparent !important; border:none !important;
    color:#c8d8e8 !important; font-family:'Share Tech Mono',monospace !important;
    font-size:0.85rem !important; letter-spacing:0.05em !important;
    padding:0.75rem 1rem !important;
}
[data-testid="stTextInput"] input:focus { box-shadow:none !important; outline:none !important; }
[data-testid="stTextInput"] input::placeholder { color:rgba(0,180,255,0.3) !important; }
[data-testid="stTextInput"] label { display:none !important; }

/* ── SECTION LABELS ── */
.section-label {
    font-family:'Share Tech Mono',monospace; font-size:0.65rem;
    color:rgba(0,180,255,0.5); letter-spacing:0.25em; text-transform:uppercase;
    margin-bottom:0.75rem; display:flex; align-items:center; gap:0.5rem;
}
.section-label::before { content:""; display:block; width:20px; height:1px; background:rgba(0,180,255,0.4); }
.section-label::after  { content:""; display:block; flex:1; height:1px; background:linear-gradient(90deg,rgba(0,180,255,0.2),transparent); }

/* ── COORD DISPLAY ── */
.coord-display {
    background:rgba(0,180,255,0.05); border:1px solid rgba(0,180,255,0.2);
    border-left:3px solid #00b4ff; padding:1rem 1.5rem;
    margin:1rem 0 1.5rem; display:flex; gap:3rem; align-items:center; flex-wrap:wrap;
}
.coord-item { font-family:'Share Tech Mono',monospace; font-size:0.8rem; }
.coord-key  { color:rgba(0,180,255,0.5); font-size:0.6rem; letter-spacing:0.2em; }
.coord-val  { color:#00b4ff; font-size:1.1rem; margin-top:0.2rem; }

/* ── WEATHER PANEL ── */
.wx-panel {
    background:rgba(5,15,28,0.95); border:1px solid rgba(0,180,255,0.2);
    border-top:2px solid #00b4ff; padding:1.2rem 1.5rem; margin:0 0 1.5rem; position:relative;
}
.wx-panel::before {
    content:""; position:absolute; inset:0; pointer-events:none;
    background:radial-gradient(ellipse 60% 80% at 0% 50%,rgba(0,180,255,0.03),transparent);
}
.wx-header {
    display:flex; align-items:center; gap:0.6rem;
    font-family:'Share Tech Mono',monospace; font-size:0.6rem;
    color:rgba(0,180,255,0.6); letter-spacing:0.2em; text-transform:uppercase;
    margin-bottom:1rem; padding-bottom:0.6rem; border-bottom:1px solid rgba(0,180,255,0.1);
}
.wx-live-dot {
    width:7px; height:7px; border-radius:50%;
    background:#00ff88; box-shadow:0 0 8px #00ff88; animation:pulse-dot 1.5s infinite;
}
.wx-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:0.8rem; }
.wx-tile { background:rgba(0,180,255,0.04); border:1px solid rgba(0,180,255,0.1); padding:0.7rem 0.8rem; }
.wx-tile-icon  { font-size:1.2rem; margin-bottom:0.3rem; line-height:1; }
.wx-tile-label { font-family:'Share Tech Mono',monospace; font-size:0.55rem; color:rgba(0,180,255,0.45); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:0.2rem; }
.wx-tile-value { font-family:'Orbitron',monospace; font-size:1rem; font-weight:700; color:#c8d8e8; line-height:1; }
.wx-tile-unit  { font-family:'Share Tech Mono',monospace; font-size:0.6rem; color:rgba(0,180,255,0.5); }
.wx-condition-badge {
    display:inline-flex; align-items:center; gap:0.5rem; padding:0.4rem 1rem; margin-top:1rem;
    background:rgba(0,180,255,0.08); border:1px solid rgba(0,180,255,0.2);
    font-family:'Rajdhani',sans-serif; font-size:0.9rem; font-weight:600; color:#a8c8e8; letter-spacing:0.08em;
}
.wx-override-note {
    font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:rgba(255,170,0,0.6);
    letter-spacing:0.12em; margin-top:0.8rem; padding-top:0.6rem; border-top:1px solid rgba(255,170,0,0.1);
}

/* ── INPUT PANELS ── */
.input-panel {
    background:rgba(10,20,35,0.8); border:1px solid rgba(0,180,255,0.12);
    padding:1.5rem; margin-bottom:1rem; position:relative;
}
.input-panel::before {
    content:""; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,180,255,0.4),transparent);
}
.input-panel-title {
    font-family:'Share Tech Mono',monospace; font-size:0.58rem;
    color:rgba(0,180,255,0.4); letter-spacing:0.2em; text-transform:uppercase; margin-bottom:0.8rem;
}

/* ── SLIDERS ── */
[data-testid="stSlider"] > div > div > div > div { background:linear-gradient(90deg,#00b4ff,#0088cc) !important; }
[data-testid="stSlider"] label {
    font-family:'Rajdhani',sans-serif !important; font-weight:600 !important;
    font-size:0.85rem !important; letter-spacing:0.05em !important;
    color:#8fb8d8 !important; text-transform:uppercase !important;
}
[data-testid="stSlider"] [data-testid="stThumbValue"] { font-family:'Share Tech Mono',monospace !important; color:#00b4ff !important; }

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] label {
    font-family:'Rajdhani',sans-serif !important; font-weight:600 !important;
    font-size:0.85rem !important; letter-spacing:0.05em !important;
    color:#8fb8d8 !important; text-transform:uppercase !important;
}
[data-testid="stSelectbox"] > div > div {
    background:rgba(0,180,255,0.05) !important; border:1px solid rgba(0,180,255,0.2) !important;
    color:#c8d8e8 !important; font-family:'Share Tech Mono',monospace !important; font-size:0.85rem !important;
}
[data-testid="stSelectbox"] > div > div:hover { border-color:rgba(0,180,255,0.5) !important; }

/* ── BUTTON ── */
[data-testid="stButton"] > button {
    background:linear-gradient(135deg,rgba(0,180,255,0.15),rgba(0,100,200,0.1)) !important;
    border:1px solid rgba(0,180,255,0.4) !important; color:#00b4ff !important;
    font-family:'Orbitron',monospace !important; font-size:0.75rem !important;
    font-weight:700 !important; letter-spacing:0.2em !important;
    padding:0.8rem 2.5rem !important; width:100% !important;
    transition:all 0.2s !important; text-transform:uppercase !important;
}
[data-testid="stButton"] > button:hover {
    background:linear-gradient(135deg,rgba(0,180,255,0.3),rgba(0,100,200,0.2)) !important;
    border-color:#00b4ff !important; box-shadow:0 0 20px rgba(0,180,255,0.3) !important;
    transform:translateY(-1px) !important;
}

/* ── RISK CARDS ── */
.risk-result-container { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin:1.5rem 0; }
.risk-card { padding:1.5rem; border:1px solid; }
.risk-card.safe   { background:rgba(0,255,136,0.04); border-color:rgba(0,255,136,0.25); }
.risk-card.severe { background:rgba(255,60,60,0.04);  border-color:rgba(255,60,60,0.25); }
.risk-card-label  { font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; margin-bottom:0.5rem; }
.risk-card.safe .risk-card-label   { color:rgba(0,255,136,0.6); }
.risk-card.severe .risk-card-label { color:rgba(255,60,60,0.6); }
.risk-card-value { font-family:'Orbitron',monospace; font-size:2.5rem; font-weight:900; line-height:1; }
.risk-card.safe .risk-card-value   { color:#00ff88; text-shadow:0 0 20px rgba(0,255,136,0.4); }
.risk-card.severe .risk-card-value { color:#ff3c3c; text-shadow:0 0 20px rgba(255,60,60,0.4); }
.risk-bar-track { height:4px; background:rgba(255,255,255,0.06); margin-top:1rem; overflow:hidden; }
.risk-bar-fill  { height:100%; }
.safe   .risk-bar-fill { background:linear-gradient(90deg,#00ff88,#00cc66); }
.severe .risk-bar-fill { background:linear-gradient(90deg,#ff8800,#ff3c3c); }

/* ── VERDICT ── */
.verdict-banner {
    padding:1.2rem 1.8rem; border:1px solid;
    display:flex; align-items:center; gap:1rem; margin-top:1rem;
    font-family:'Orbitron',monospace; font-size:0.9rem; font-weight:700;
    letter-spacing:0.1em; text-transform:uppercase;
}
.verdict-banner.low      { background:rgba(0,255,136,0.06); border-color:rgba(0,255,136,0.3); color:#00ff88; }
.verdict-banner.moderate { background:rgba(255,136,0,0.06); border-color:rgba(255,136,0,0.3); color:#ff8800; }
.verdict-banner.severe   { background:rgba(255,60,60,0.08);  border-color:rgba(255,60,60,0.4);  color:#ff3c3c; animation:flicker 1.5s infinite; }
@keyframes flicker { 0%,100%{opacity:1} 92%{opacity:1} 93%{opacity:.7} 94%{opacity:1} 96%{opacity:.8} 97%{opacity:1} }
.verdict-icon { font-size:1.4rem; }

/* ── ERROR / NOTICE ── */
.wx-error {
    background:rgba(255,60,60,0.05); border:1px solid rgba(255,60,60,0.2);
    border-left:3px solid #ff3c3c; padding:0.8rem 1.2rem; margin:0.5rem 0;
    font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:rgba(255,100,100,0.8); letter-spacing:0.1em;
}
.search-notice {
    font-family:'Share Tech Mono',monospace; font-size:0.68rem;
    color:rgba(255,170,0,0.7); padding:0.5rem 0.8rem;
    background:rgba(255,170,0,0.05); border:1px solid rgba(255,170,0,0.15);
    margin-top:0.4rem; letter-spacing:0.08em;
}

/* ── MISC ── */
[data-testid="stAlert"]  { display:none !important; }
[data-testid="stIFrame"] { border:1px solid rgba(0,180,255,0.2) !important; }
[data-testid="column"]   { padding:0 0.5rem !important; }
hr { border-color:rgba(0,180,255,0.1) !important; margin:1.5rem 0 !important; }
.aria-footer {
    margin-top:3rem; padding-top:1rem; border-top:1px solid rgba(0,180,255,0.1);
    font-family:'Share Tech Mono',monospace; font-size:0.6rem;
    color:rgba(0,180,255,0.3); letter-spacing:0.15em; text-align:center;
}
::-webkit-scrollbar       { width:4px; }
::-webkit-scrollbar-track { background:#080c10; }
::-webkit-scrollbar-thumb { background:rgba(0,180,255,0.3); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

WMO_CODES = {
    0:("Clear","☀️"),1:("Mainly Clear","🌤️"),2:("Partly Cloudy","⛅"),
    3:("Overcast","☁️"),45:("Fog","🌫️"),48:("Icy Fog","🌫️"),
    51:("Light Drizzle","🌦️"),53:("Moderate Drizzle","🌦️"),55:("Dense Drizzle","🌧️"),
    61:("Slight Rain","🌧️"),63:("Moderate Rain","🌧️"),65:("Heavy Rain","🌧️"),
    71:("Slight Snow","🌨️"),73:("Moderate Snow","🌨️"),75:("Heavy Snow","❄️"),
    77:("Snow Grains","❄️"),80:("Slight Showers","🌦️"),81:("Moderate Showers","🌧️"),
    82:("Violent Showers","⛈️"),85:("Snow Showers","🌨️"),86:("Heavy Snow Showers","❄️"),
    95:("Thunderstorm","⛈️"),96:("Thunderstorm+Hail","⛈️"),99:("Thunderstorm+Hail","⛈️"),
}

def wmo_label(code):
    return WMO_CODES.get(code, ("Unknown","🌡️"))

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ─────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────
def geocode_location(query: str):
    """Nominatim free geocoder → (lat, lng, display_name) or raises."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": "ARIA-AccidentRiskApp/3.0"}
    r = requests.get(url, params=params, headers=headers, timeout=8)
    r.raise_for_status()
    results = r.json()
    if not results:
        raise ValueError(f"No results found for '{query}'")
    top = results[0]
    return float(top["lat"]), float(top["lon"]), top.get("display_name", query)


def fetch_weather(lat, lng):
    """Open-Meteo free weather API — no key needed."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lng}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,weather_code,surface_pressure,wind_speed_10m,visibility"
        f"&wind_speed_unit=mph&temperature_unit=fahrenheit"
        f"&precipitation_unit=inch&timezone=auto"
    )
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    c = r.json()["current"]

    pressure_in = round(c.get("surface_pressure", 1013.0) * 0.02953, 2)
    vis_mi      = round(min(c.get("visibility", 10000) / 1609.34, 15.0), 1)
    temp_f      = round(c.get("temperature_2m", 70), 1)
    feels_f     = round(c.get("apparent_temperature", temp_f), 1)
    humidity    = int(c.get("relative_humidity_2m", 60))
    precip      = round(c.get("precipitation", 0.0), 2)
    wind_mph    = round(c.get("wind_speed_10m", 5), 1)
    wcode       = int(c.get("weather_code", 0))
    label, emoji = wmo_label(wcode)

    now_str = c.get("time", "")
    try:
        now = datetime.fromisoformat(now_str)
        hour, dayofweek, month = now.hour, now.weekday(), now.month
    except Exception:
        now = datetime.utcnow()
        hour, dayofweek, month = now.hour, now.weekday(), now.month

    return dict(
        temperature_f=temp_f, wind_chill_f=feels_f,
        humidity=humidity, pressure_in=pressure_in,
        visibility_mi=vis_mi, wind_speed_mph=wind_mph,
        precipitation_in=precip, weather_label=label,
        weather_emoji=emoji, hour=hour,
        dayofweek=dayofweek, month=month, fetch_time=now_str,
    )

# ─────────────────────────────────────────────────────────
# SESSION STATE — initialise defaults once
# ─────────────────────────────────────────────────────────
_DEFAULTS = dict(
    temperature=70, humidity=60, pressure=30.0,
    visibility=10.0, wind_speed=5, precipitation=0.0,
    hour=12, dayofweek_idx=0,
)
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Track last-loaded coordinate so we only re-fetch on new clicks
if "loaded_coord" not in st.session_state:
    st.session_state.loaded_coord = None
if "wx_cache" not in st.session_state:
    st.session_state.wx_cache = None
if "wx_error" not in st.session_state:
    st.session_state.wx_error = None
if "map_center" not in st.session_state:
    st.session_state.map_center = [40.7128, -74.0060]
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 5
if "search_msg" not in st.session_state:
    st.session_state.search_msg = ""

# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="aria-header">
  <div>
    <div class="aria-logo">ARI<span>A</span></div>
    <div class="aria-subtitle">Accident Risk Intelligence Architecture · v3.1</div>
  </div>
  <div class="aria-tagline">Real-time predictive collision analysis</div>
</div>
<div class="status-bar">
  <div class="status-pill"><span class="dot"></span> Model Online</div>
  <div class="status-pill"><span class="dot"></span> Geo Engine Active</div>
  <div class="status-pill"><span class="dot"></span> Open-Meteo Live</div>
  <div class="status-pill"><span class="dot"></span> Nominatim Search Ready</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────────────────
model = joblib.load("traffic_accident_model.pkl")

# ─────────────────────────────────────────────────────────
# SECTION 01 — LOCATION
# ─────────────────────────────────────────────────────────
st.markdown('<div class="section-label">01 · Target Coordinates</div>', unsafe_allow_html=True)

# ── SEARCH BAR ──────────────────────────────────────────
st.markdown('<div class="search-wrap"><div class="search-icon">⌕ SEARCH</div>', unsafe_allow_html=True)
search_col, btn_col = st.columns([5, 1])
with search_col:
    search_query = st.text_input(
        "_", placeholder="Search city, address, landmark…",
        label_visibility="collapsed", key="search_input"
    )
with btn_col:
    search_clicked = st.button("LOCATE", key="search_btn")
st.markdown('</div>', unsafe_allow_html=True)

# Handle search
if search_clicked and search_query.strip():
    with st.spinner("Resolving location…"):
        try:
            slat, slng, sname = geocode_location(search_query.strip())
            st.session_state.map_center = [slat, slng]
            st.session_state.map_zoom   = 13
            st.session_state.search_msg = f"📍 {sname}"
            # Pre-load as selected location
            st.session_state.loaded_coord = (slat, slng)
            # Fetch weather immediately
            wx = fetch_weather(slat, slng)
            st.session_state.wx_cache = wx
            st.session_state.wx_error = None
            # Push into sliders via session_state
            st.session_state.temperature   = clamp(int(wx["temperature_f"]),   -20, 120)
            st.session_state.humidity      = clamp(int(wx["humidity"]),          0, 100)
            st.session_state.pressure      = clamp(float(wx["pressure_in"]),   25.0, 32.0)
            st.session_state.visibility    = clamp(float(wx["visibility_mi"]),  0.0, 15.0)
            st.session_state.wind_speed    = clamp(int(wx["wind_speed_mph"]),   0,   50)
            st.session_state.precipitation = clamp(float(wx["precipitation_in"]), 0.0, 2.0)
            st.session_state.hour          = clamp(wx["hour"],                  0,   23)
            st.session_state.dayofweek_idx = clamp(wx["dayofweek"],             0,   6)
        except Exception as e:
            st.session_state.search_msg = f"⚠ Search failed: {e}"
            st.session_state.wx_error   = str(e)

if st.session_state.search_msg:
    color = "#ff8800" if st.session_state.search_msg.startswith("⚠") else "#00b4ff"
    st.markdown(
        f'<div class="search-notice" style="color:{color}">{st.session_state.search_msg}</div>',
        unsafe_allow_html=True
    )

# ── MAP ─────────────────────────────────────────────────
st.markdown(
    "<p style='font-family:Share Tech Mono,monospace;font-size:0.68rem;"
    "color:rgba(0,180,255,0.4);letter-spacing:0.1em;margin:0.5rem 0 0.4rem'>"
    "OR CLICK DIRECTLY ON THE MAP</p>",
    unsafe_allow_html=True
)

m = folium.Map(
    location=st.session_state.map_center,
    zoom_start=st.session_state.map_zoom,
    tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attr="© OpenStreetMap contributors © CARTO"
)

# Drop marker on already-selected coord
if st.session_state.loaded_coord:
    lc = st.session_state.loaded_coord
    folium.CircleMarker(
        location=lc,
        radius=8, color="#00b4ff", fill=True, fill_color="#00b4ff", fill_opacity=0.6,
        popup=f"{lc[0]:.4f}, {lc[1]:.4f}"
    ).add_to(m)

map_data = st_folium(m, height=450, width=None, use_container_width=True)

# ── Handle map click ────────────────────────────────────
if map_data and map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lng = map_data["last_clicked"]["lng"]
    new_coord   = (round(clicked_lat, 6), round(clicked_lng, 6))

    # Only re-fetch if this is a genuinely new click
    if new_coord != st.session_state.loaded_coord:
        st.session_state.loaded_coord = new_coord
        st.session_state.search_msg   = ""
        with st.spinner("Acquiring weather data…"):
            try:
                wx = fetch_weather(clicked_lat, clicked_lng)
                st.session_state.wx_cache = wx
                st.session_state.wx_error = None
                # ← Inject into session_state keys (sliders read these)
                st.session_state.temperature   = clamp(int(wx["temperature_f"]),      -20,  120)
                st.session_state.humidity      = clamp(int(wx["humidity"]),              0,  100)
                st.session_state.pressure      = clamp(float(wx["pressure_in"]),      25.0, 32.0)
                st.session_state.visibility    = clamp(float(wx["visibility_mi"]),     0.0, 15.0)
                st.session_state.wind_speed    = clamp(int(wx["wind_speed_mph"]),       0,   50)
                st.session_state.precipitation = clamp(float(wx["precipitation_in"]),  0.0,  2.0)
                st.session_state.hour          = clamp(wx["hour"],                      0,   23)
                st.session_state.dayofweek_idx = clamp(wx["dayofweek"],                 0,    6)
            except Exception as e:
                st.session_state.wx_error = str(e)
                st.session_state.wx_cache = None
        st.rerun()

# ─────────────────────────────────────────────────────────
# Only render the rest once a location is selected
# ─────────────────────────────────────────────────────────
if st.session_state.loaded_coord:
    lat, lng = st.session_state.loaded_coord

    # ── COORD DISPLAY ──
    st.markdown(f"""
    <div class="coord-display">
      <div class="coord-item"><div class="coord-key">Latitude</div><div class="coord-val">{lat:.6f}°</div></div>
      <div class="coord-item"><div class="coord-key">Longitude</div><div class="coord-val">{lng:.6f}°</div></div>
      <div class="coord-item"><div class="coord-key">Status</div>
        <div class="coord-val" style="color:#00ff88;font-size:0.85rem;">● LOCKED</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # SECTION 02 — LIVE WEATHER TELEMETRY
    # ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">02 · Live Weather Telemetry</div>', unsafe_allow_html=True)

    if st.session_state.wx_error:
        st.markdown(
            f'<div class="wx-error">⚠ WEATHER FETCH FAILED — {st.session_state.wx_error}'
            '<br>Sliders using default values. Adjust manually.</div>',
            unsafe_allow_html=True
        )
        # Fallback wx for display
        wx_disp = dict(
            temperature_f=70, wind_chill_f=70, humidity=60,
            pressure_in=30.0, visibility_mi=10.0, wind_speed_mph=5,
            precipitation_in=0.0, weather_label="Clear", weather_emoji="☀️",
            hour=12, fetch_time="N/A",
        )
    else:
        wx_disp = st.session_state.wx_cache or {}

    if wx_disp:
        ft = str(wx_disp.get("fetch_time", ""))[:16].replace("T", " ")
        st.markdown(f"""
        <div class="wx-panel">
          <div class="wx-header">
            <div class="wx-live-dot"></div>
            Live Weather Feed &nbsp;·&nbsp; {ft} local
          </div>
          <div class="wx-grid">
            <div class="wx-tile">
              <div class="wx-tile-icon">🌡️</div>
              <div class="wx-tile-label">Temperature</div>
              <div class="wx-tile-value">{wx_disp["temperature_f"]}<span class="wx-tile-unit"> °F</span></div>
            </div>
            <div class="wx-tile">
              <div class="wx-tile-icon">💧</div>
              <div class="wx-tile-label">Humidity</div>
              <div class="wx-tile-value">{wx_disp["humidity"]}<span class="wx-tile-unit"> %</span></div>
            </div>
            <div class="wx-tile">
              <div class="wx-tile-icon">🌬️</div>
              <div class="wx-tile-label">Wind</div>
              <div class="wx-tile-value">{wx_disp["wind_speed_mph"]}<span class="wx-tile-unit"> mph</span></div>
            </div>
            <div class="wx-tile">
              <div class="wx-tile-icon">👁️</div>
              <div class="wx-tile-label">Visibility</div>
              <div class="wx-tile-value">{wx_disp["visibility_mi"]}<span class="wx-tile-unit"> mi</span></div>
            </div>
            <div class="wx-tile">
              <div class="wx-tile-icon">🌧️</div>
              <div class="wx-tile-label">Precip</div>
              <div class="wx-tile-value">{wx_disp["precipitation_in"]}<span class="wx-tile-unit"> in</span></div>
            </div>
            <div class="wx-tile">
              <div class="wx-tile-icon">📊</div>
              <div class="wx-tile-label">Pressure</div>
              <div class="wx-tile-value">{wx_disp["pressure_in"]}<span class="wx-tile-unit"> in</span></div>
            </div>
            <div class="wx-tile">
              <div class="wx-tile-icon">🥶</div>
              <div class="wx-tile-label">Feels Like</div>
              <div class="wx-tile-value">{wx_disp["wind_chill_f"]}<span class="wx-tile-unit"> °F</span></div>
            </div>
            <div class="wx-tile">
              <div class="wx-tile-icon">🕐</div>
              <div class="wx-tile-label">Local Hour</div>
              <div class="wx-tile-value">{wx_disp["hour"]:02d}<span class="wx-tile-unit">:00</span></div>
            </div>
          </div>
          <div class="wx-condition-badge">{wx_disp["weather_emoji"]}&nbsp; {wx_disp["weather_label"]}</div>
          <div class="wx-override-note">⚙ Sliders below auto-populated from live data — drag to override</div>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # SECTION 03 — ENVIRONMENTAL PARAMETERS
    # Sliders use key= so session_state drives their values.
    # Weather inject writes to session_state BEFORE sliders render,
    # so they always reflect the latest fetched data automatically.
    # ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">03 · Environmental Parameters</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="input-panel"><div class="input-panel-title">Atmospheric</div>', unsafe_allow_html=True)
        temperature = st.slider("Temperature (°F)", -20, 120, key="temperature")
        humidity    = st.slider("Humidity (%)",       0, 100, key="humidity")
        pressure    = st.slider("Pressure (in)",    25.0, 32.0, key="pressure")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="input-panel"><div class="input-panel-title">Conditions</div>', unsafe_allow_html=True)
        visibility    = st.slider("Visibility (mi)",    0.0, 15.0, key="visibility")
        wind_speed    = st.slider("Wind Speed (mph)",   0,   50,   key="wind_speed")
        precipitation = st.slider("Precipitation (in)", 0.0,  2.0, key="precipitation")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="input-panel"><div class="input-panel-title">Temporal</div>', unsafe_allow_html=True)
        hour = st.slider("Hour of Day", 0, 23, key="hour")
        dayofweek = st.selectbox(
            "Day of Week", DAYS,
            index=st.session_state.dayofweek_idx,
            key="dayofweek_select"
        )
        dayofweek_num = DAYS.index(dayofweek)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # SECTION 04 — ROAD INFRASTRUCTURE
    # ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">04 · Road Infrastructure</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        traffic_signal = st.selectbox("Traffic Signal", [0,1], format_func=lambda x:"Present" if x else "Absent")
    with col5:
        junction = st.selectbox("Junction", [0,1], format_func=lambda x:"Present" if x else "Absent")
    with col6:
        crossing = st.selectbox("Crossing", [0,1], format_func=lambda x:"Present" if x else "Absent")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    # SECTION 05 — PREDICT
    # ─────────────────────────────────────────────────────
    if st.button("⬡  RUN RISK ANALYSIS"):
        wx_now = st.session_state.wx_cache or {}
        weather_label = wx_now.get("weather_label", "Clear")
        wind_chill    = wx_now.get("wind_chill_f",  temperature)
        month_val     = wx_now.get("month",          datetime.utcnow().month)

        input_data = pd.DataFrame({
            "Start_Lat":         [lat],
            "Start_Lng":         [lng],
            "Temperature(F)":    [temperature],
            "Humidity(%)":       [humidity],
            "Pressure(in)":      [pressure],
            "Visibility(mi)":    [visibility],
            "Wind_Speed(mph)":   [wind_speed],
            "Wind_Chill(F)":     [wind_chill],
            "Precipitation(in)": [precipitation],
            "Distance(mi)":      [0.5],
            "Weather_Condition": [weather_label],
            "Traffic_Signal":    [traffic_signal],
            "Crossing":          [crossing],
            "Junction":          [junction],
            "Station":           [0], "Stop":[0], "Amenity":[0],
            "Bump":              [0], "Give_Way":[0],
            "Hour":              [hour],
            "DayOfWeek":         [dayofweek_num],
            "Month":             [month_val],
            "Weekend":           [1 if dayofweek_num >= 5 else 0],
        })

        input_data["Temp_Humidity"]      = input_data["Temperature(F)"] * input_data["Humidity(%)"]
        input_data["Wind_Visibility"]    = input_data["Wind_Speed(mph)"] * input_data["Visibility(mi)"]
        input_data["Weather_Visibility"] = input_data["Visibility(mi)"] * input_data["Precipitation(in)"]
        input_data = pd.get_dummies(input_data)

        try:
            input_data = input_data.reindex(columns=model.feature_name_, fill_value=0)
        except Exception:
            pass

        prob        = model.predict_proba(input_data)
        safe_prob   = prob[0][0] * 100
        severe_prob = prob[0][1] * 100

        st.markdown('<div class="section-label">05 · Risk Assessment Output</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="risk-result-container">
          <div class="risk-card safe">
            <div class="risk-card-label">Safe Probability</div>
            <div class="risk-card-value">{safe_prob:.1f}<span style="font-size:1rem">%</span></div>
            <div class="risk-bar-track"><div class="risk-bar-fill" style="width:{int(safe_prob)}%"></div></div>
          </div>
          <div class="risk-card severe">
            <div class="risk-card-label">Severe Risk Probability</div>
            <div class="risk-card-value">{severe_prob:.1f}<span style="font-size:1rem">%</span></div>
            <div class="risk-bar-track"><div class="risk-bar-fill" style="width:{int(severe_prob)}%"></div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if severe_prob > 50:
            vc, icon, text = "severe",   "🚨", "SEVERE ACCIDENT RISK DETECTED"
        elif severe_prob > 30:
            vc, icon, text = "moderate", "⚠",  "MODERATE RISK — EXERCISE CAUTION"
        else:
            vc, icon, text = "low",      "✓",  "LOW RISK — CONDITIONS NOMINAL"

        st.markdown(f"""
        <div class="verdict-banner {vc}">
          <span class="verdict-icon">{icon}</span>{text}
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="aria-footer">
  ARIA SYSTEM v3.1 · WEATHER: OPEN-METEO.COM (CC BY 4.0) · GEOCODING: NOMINATIM / OSM · FOR ANALYTICAL PURPOSES ONLY
</div>
""", unsafe_allow_html=True)