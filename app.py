import streamlit as st
import utils
import pandas as pd
import time

# Page Config
st.set_page_config(
    page_title="Rural Japan Explorer",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
try:
    utils.load_css('styles.css')
except FileNotFoundError:
    st.error("styles.css not found. Please ensure it exists.")

import streamlit as st
import utils
import pandas as pd
import time

# Page Config
st.set_page_config(
    page_title="Rural Japan Explorer",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS
try:
    utils.load_css('styles.css')
except FileNotFoundError:
    st.error("styles.css not found. Please ensure it exists.")

# Session State Initialization
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'selected_location' not in st.session_state:
    st.session_state.selected_location = None

# Navigation Helper Functions
def navigate_to(page_name):
    st.session_state.page = page_name

def select_location(location_name):
    st.session_state.selected_location = location_name
    st.session_state.page = "Detail"

# Sidebar (Simplified)
st.sidebar.title("Navigation")
if st.sidebar.button("Home"):
    navigate_to("Home")
if st.sidebar.button("Marketplace"):
    navigate_to("Marketplace")
if st.sidebar.button("User Ratings"):
    navigate_to("User Ratings")

# --- HOME PAGE ---
if st.session_state.page == "Home":
    # Hero Section
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h1 class="hero-title">IKIGAI<br>TRAVEL</h1>', unsafe_allow_html=True)
        st.markdown('<p class="hero-subtitle">Discover the hidden soul of rural Japan. Beyond the neon lights, find peace, tradition, and untouched nature.</p>', unsafe_allow_html=True)
        
        # Call to Action changes page state
        if st.button("Start Your Journey", use_container_width=True):
             navigate_to("Marketplace")
             st.rerun()
    
    with col2:
        if utils.get_base64_of_bin_file("assets/iki_hero.png"):
             st.image("assets/iki_hero.png", use_container_width=True)
        else:
             st.info("Generating assets...")
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Features Section
    st.markdown("### Why Go Rural?")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="glass-card">
            <h3>🌿 Nature</h3>
            <p>Experience pristine landscapes, from ancient forests to turquoise waters.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-card">
            <h3>⛩️ Tradition</h3>
            <p>Immerse yourself in centuries-old customs, festivals, and spiritual heritage.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="glass-card">
            <h3>🍱 Gastronomy</h3>
            <p>Taste the freshest local ingredients, from sea urchin to mountain vegetables.</p>
        </div>
        """, unsafe_allow_html=True)

# --- MARKETPLACE PAGE ---
elif st.session_state.page == "Marketplace":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("Explore Destinations")
    st.write("Find your perfect rural escape. Click on a card to see more.")
    
    # Grid Layout Logic
    cols = st.columns(3)
    
    for idx, (loc_name, details) in enumerate(utils.LOCATIONS.items()):
        col = cols[idx % 3]
        
        # We use a container to group the "Card" visually
        with col:
            # Display image
            img_path = details["image"] if details["image"] else "assets/iki_hero.png" 
            
            # Using a button that looks like a card content is tricky in Streamlit.
            # We will use the standard button but stylized or a specialized component.
            # For simplicity in standard Streamlit, we render the image/text and a "View Details" button.
            
            with st.container(border=True): # Streamlit 1.30+ container border
                st.image(img_path, use_container_width=True)
                st.subheader(loc_name)
                st.markdown(f"**{details.get('price', 'N/A')}**")
                st.write(details['description'][:80] + "...")
                st.markdown(f"⭐ **{details['rating']}**")
                
                if st.button(f"Explore {loc_name}", key=f"btn_{loc_name}"):
                    select_location(loc_name)
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- DETAIL VIEW PAGE ---
elif st.session_state.page == "Detail":
    loc_name = st.session_state.selected_location
    if not loc_name or loc_name not in utils.LOCATIONS:
        st.error("Location not found.")
        if st.button("Back to Marketplace"):
            navigate_to("Marketplace")
            st.rerun()
    else:
        data = utils.LOCATIONS[loc_name]
        
        # Back Button
        if st.button("← Back to Marketplace"):
            navigate_to("Marketplace")
            st.rerun()
            
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        # Hero Image for Detail
        if data["image"]:
            st.image(data["image"], use_container_width=True)
            
        st.title(loc_name)
        st.markdown(f"### {data.get('price', '')}")
        st.markdown(f"⭐ **{data['rating']}** (Based on community reviews)")
        
        st.write(data.get("detail_text", data["description"]))
        
        st.markdown("---")
        
        # Gallery
        st.subheader("Gallery")
        g_cols = st.columns(3)
        # Just repeating the main image for demo purposes since we lack varied assets
        for i in range(3):
            with g_cols[i]:
                st.image(data["gallery"][0], use_container_width=True, caption=f"View {i+1}")
        
        st.markdown("---")
        
        # Reviews
        st.subheader("What Travelers Say")
        
        # Generate some random reviews specific to this location
        # In a real app, this would filter the main list
        mock_reviews = utils.generate_ratings(3)
        for review in mock_reviews:
            st.markdown(f"""
            <div class="review-card">
                <strong>{review['user']}</strong> <span style="color:#f1c40f;">{'★' * review['score']}</span>
                <p>"{review['comment']}"</p>
                <small style="color:#bdc3c7;">Visited in {review['date']}</small>
            </div>
            """, unsafe_allow_html=True)
            
        st.button("Book This Experience", type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)


# --- USER RATINGS PAGE ---
elif st.session_state.page == "User Ratings":
    st.title("Community Voices")
    if st.button("← Back to Marketplace"):
        navigate_to("Marketplace")
        st.rerun()
    
    # Search Filter
    search_term = st.text_input("Search reviews by location or keyword", "")
    
    # Mock Data
    if 'ratings_data' not in st.session_state:
        st.session_state.ratings_data = utils.generate_ratings(15)
    
    df = pd.DataFrame(st.session_state.ratings_data)
    
    if search_term:
        df = df[df['location'].str.contains(search_term, case=False) | df['comment'].str.contains(search_term, case=False)]
    
    # Display Ratings
    for idx, row in df.iterrows():
        st.markdown(f"""
        <div class="glass-card fade-in" style="padding: 1rem;">
            <div style="display: flex; justify-content: space-between;">
                <strong>{row['user']}</strong>
                <span style="color: #888;">{row['date']}</span>
            </div>
            <div style="color: #FFD700;">{'★' * row['score']}</div>
            <p style="margin-top: 0.5rem;"><em>"{row['comment']}"</em></p>
            <small style="color: #666;">Visited: {row['location']}</small>
        </div>
        """, unsafe_allow_html=True)
