import streamlit as st
import folium
from streamlit_folium import st_folium
import base64
import streamlit.components.v1 as components
from ikicontent import render_tourist_content, render_sidebar_chatbot, load_tourist_spots
st.set_page_config(page_title="Ikikae project -> App demo", layout="wide")

# Custom CSS for styling
# Custom CSS for styling
st.markdown("""
<style>
    /* Import Google Fonts - Nunito (Fun & Rounded) */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');

    /* Global App Background */
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.2)),
                          url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=2000&auto=format&fit=crop'); /* Tropical Beach */
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }
    
    /* Typography */
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Nunito', sans-serif !important;
        font-weight: 800 !important;
        color: #1a237e !important;
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8); /* Changed to white shadow for dark text */
    }
    
    p, div, label, span, li {
        font-family: 'Nunito', sans-serif;
        font-weight: 400;
        color: #004d40; /* Dark teal for readability */
        text-shadow: 0 1px 1px rgba(255,255,255,0.8);
    }
    
    /* Removed the generic div[data-testid="stVerticalBlock"] > div rule to fix "broken" text */
    
    /* Ensure Streamlit's structural containers don't double-background if not needed */
    .stApp > header {
        background: transparent !important;
    }

    /* Card Styling */
    div[data-testid="stContainer"] {
        background: transparent; 
    }
    
    /* Specific styling for bordered containers (Cards) - Glass effect ONLY for cards */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 20px;
        transition: transform 0.3s ease;
        padding: 20px;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15) !important;
    }

    /* Custom Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        color: #333 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 14px rgba(0,0,0,0.15) !important;
    }
    
    /* Primary Button (Discover) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2980b9 0%, #6dd5fa 100%, #ffffff 100%) !important; 
        /* Actually simpler gradient for text readability */
        background: linear-gradient(135deg, #0288d1 0%, #26c6da 100%) !important;
        color: white !important;
        font-weight: 700 !important;
    }

    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(2, 136, 209, 0.4) !important;
    }
    
    /* Divider Styling */
    hr {
        border-color: rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-right: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Image rounded corners */
    img {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'

if st.session_state.current_page == 'ikicontent':
    if st.button("← Back to Main"):
        st.session_state.current_page = 'main'
        st.rerun()
    
    tourist_data = load_tourist_spots()
    render_sidebar_chatbot(tourist_data)
    render_tourist_content()
    st.stop()

def scroll_to(target_id):
    js = f"""
    <script>
        var element = window.parent.document.getElementById('{target_id}');
        if (element) {{
            element.scrollIntoView({{behavior: 'smooth'}});
        }}
    </script>
    """
    return components.html(js, height=0)


# Title Section with centered text
st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-bottom: 0;'>IKI ISLAND</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; font-weight: 300; margin-bottom: 3rem;'>Experience the hidden gem of Japan</p>", unsafe_allow_html=True)

if 'show_about' not in st.session_state:
    st.session_state.show_about = False

# Action Buttons centered
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✨ DISCOVER LOCATIONS", type="primary", use_container_width=True):
            scroll_to("Discover")
    with col_b:
        if st.button("ℹ️ ABOUT PROJECT", use_container_width=True):
            st.session_state.show_about = not st.session_state.show_about

if st.session_state.show_about:
    st.divider()
    st.info("### About the Project")
    st.write("Explanation about the project and how it works...")
    st.write("Here are the statistics and form results.")

st.divider()
st.markdown("<h2 style='text-align: center;'>Explore the Map</h2>", unsafe_allow_html=True)


#MAP STUFF
iki_lat = 33.7492
iki_lon = 129.6914
m = folium.Map(
    location=[36.0, 138.0],
    zoom_start=6,
    tiles="OpenStreetMap"
)
placeholder_image_path = "/Users/niwatorimostiqo/.gemini/antigravity/brain/86904a5a-a2c9-4e4e-9a58-551f7b5ba493/iki_island_placeholder_1767502986414.png"
try:
    with open(placeholder_image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode()
    
    popup_html = f"""
    <div style="width: 200px; text-align: center;">
        <h3 style="margin: 5px 0;">Iki Island</h3>
        <img src="data:image/png;base64,{img_data}" style="width: 180px; height: auto; margin-top: 10px;">
    </div>
    """
except FileNotFoundError:
    popup_html = """
    <div style="width: 200px; text-align: center;">
        <h3 style="margin: 5px 0;">Iki Island</h3>
        <p>Placeholder image not found</p>
    </div>
    """
folium.Marker(
    location=[iki_lat, iki_lon],
    popup=folium.Popup(popup_html, max_width=250),
    tooltip="Click to see Iki Island info",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)
# Centering the map using columns
c_map1, c_map2, c_map3 = st.columns([1, 8, 1])
with c_map2:
    st_folium(m, width=900, height=500)


st.divider()
st.markdown('<div id="Discover"></div>', unsafe_allow_html=True)
st.header("Discover locations")
st.write("Locations are as follows")

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'

c3, c4, c5 = st.columns(3)

with c3:
    # Create a clickable card using a container and button
    with st.container(border=True):
        st.markdown("### Iki Island")
        st.write("Discover the hidden treasures of Iki Island")
        st.image("https://images.unsplash.com/photo-1633703384611-41eb774a6d3b?w=400", use_container_width=True)
        
        if st.button("Explore Iki Island", key="explore_iki", use_container_width=True, type="primary"):
            st.session_state.current_page = 'ikicontent'
            st.rerun()




