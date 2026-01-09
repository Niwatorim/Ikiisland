import streamlit as st
import json
import os
import traceback
import time
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from dotenv import load_dotenv
import utils

# LangChain-related imports: support multiple package layout versions with fallbacks
try:
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
except Exception:
    ChatGoogleGenerativeAI = None
    GoogleGenerativeAIEmbeddings = None

try:
    # newer split packages
    from langchain_community.vectorstores import FAISS
except Exception:
    try:
        from langchain.vectorstores import FAISS
    except Exception:
        FAISS = None

try:
    from langchain_core.documents import Document
except Exception:
    try:
        from langchain.schema import Document
    except Exception:
        Document = None

try:
    from langchain.chains import ConversationalRetrievalChain
except Exception:
    try:
        from langchain_core.chains import ConversationalRetrievalChain
    except Exception:
        ConversationalRetrievalChain = None

load_dotenv()

# st.set_page_config(page_title="Iki Island Tourist Spots", layout="wide")

def load_tourist_spots():
    json_path = os.path.join(os.path.dirname(__file__), 'tourist_spots.json')
    if not os.path.exists(json_path):
        return []
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tourist_spots(data):
    json_path = os.path.join(os.path.dirname(__file__), 'tourist_spots.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_review(spot_id, user_review):
    """Save a new review to the JSON file"""
    spots = load_tourist_spots()
    for spot in spots:
        if spot.get('id') == spot_id:
            if 'user_reviews' not in spot:
                spot['user_reviews'] = []
            spot['user_reviews'].append({
                "content": user_review,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            break
    save_tourist_spots(spots)

@st.cache_resource
def load_llm():
    """Cache the LLM instance to prevent reload delays"""
    api_key = os.getenv("GEMINI_API_KEY")
    if ChatGoogleGenerativeAI is None:
        raise ImportError("ChatGoogleGenerativeAI is not available. Install 'langchain-google-genai' and restart the app.")
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0)

def get_vector_store(data):
    INDEX_PATH = "faiss_index"
    api_key = os.getenv("GEMINI_API_KEY")
    if GoogleGenerativeAIEmbeddings is None:
        raise ImportError("GoogleGenerativeAIEmbeddings is not available. Install 'langchain-google-genai' and restart the app.")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key) 

    if os.path.exists(INDEX_PATH):
        if FAISS is None:
            raise ImportError("FAISS vectorstore not available. Install 'langchain_community' or compatible 'langchain' package.")
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    
    if data:
        documents = []
        for item in data:
            content = f"Spot Name: {item.get('name')}. Category: {item.get('category')}. " \
                      f"Description: {item.get('shortDescription')}. Highlights: {', '.join(item.get('highlights', []))}"
            if Document is None:
                raise ImportError("Document class is not available from LangChain. Install compatible 'langchain_core' or 'langchain' package.")
            documents.append(Document(page_content=content, metadata={"name": item.get("name")}))
        
        if FAISS is None:
            raise ImportError("FAISS vectorstore not available. Install 'langchain_community' or compatible 'langchain' package.")

        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(INDEX_PATH)
        return vector_store
    return None

def render_sidebar_chatbot(tourist_data):
    st.sidebar.header("Iki Island AI Guide")
    
    avatar_placeholder = st.sidebar.empty()
    avatar_placeholder.image("idle.png", use_container_width=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "vector_store" not in st.session_state:
        avatar_placeholder.image("thinking.png", use_container_width=True)
        with st.sidebar:
            with st.spinner("Preparing AI Guide..."):
                st.session_state.vector_store = get_vector_store(tourist_data)
        avatar_placeholder.image("idle.png", use_container_width=True)

    chat_container = st.sidebar.container(height=450)
    for message in st.session_state.chat_history:
        with chat_container.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.sidebar.chat_input("Ask about Iki Island..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)
        avatar_placeholder.image("thinking.png", use_container_width=True)
        
        with st.sidebar:
            llm = load_llm()
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=st.session_state.vector_store.as_retriever(search_kwargs={"k": 3}),
            )

            with chat_container.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    # Build chat history as pairs of (human_message, ai_message) tuples
                    history_tuples = []
                    messages = st.session_state.chat_history[:-1]  # Exclude current user message
                    for i in range(0, len(messages) - 1, 2):
                        if messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant":
                            history_tuples.append((messages[i]["content"], messages[i + 1]["content"]))
                    
                    stream_res = qa_chain.stream({
                        "question": prompt, 
                        "chat_history": history_tuples
                    })
                    
                    has_started_speaking = False
                    
                    for chunk in stream_res:
                        if 'answer' in chunk:
                            if not has_started_speaking:
                                avatar_placeholder.image("speaking.png", use_container_width=True)
                                has_started_speaking = True
                            
                            content_chunk = chunk['answer']
                            full_response += content_chunk
                            response_placeholder.markdown(full_response + "▌")
                            
                    response_placeholder.markdown(full_response)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    print(traceback.format_exc())  # Print full traceback to console
                    st.error(f"Error: {type(e).__name__}: {e}")
                
                finally:
                    time.sleep(2)  # Keep speaking avatar visible for 2 seconds after response
                    avatar_placeholder.image("idle.png", use_container_width=True)

def render_tourist_content():
    """Render the category filter and tourist spots grid"""
    
    tourist_spots = load_tourist_spots()
    
    
    if 'active_category' not in st.session_state:
        st.session_state.active_category = 'All'
    
    
    categories = ['All'] + sorted(list(set(spot['category'] for spot in tourist_spots)))
    
    
    st.markdown("---")
    st.markdown("### Explore by Category")
    
    cols = st.columns(len(categories))
    for idx, category in enumerate(categories):
        with cols[idx]:
            if st.button(
                category,
                key=f"cat_{category}",
                use_container_width=True,
                type="primary" if st.session_state.active_category == category else "secondary"
            ):
                st.session_state.active_category = category
    
    st.markdown("---")
    
    
    filtered_spots = tourist_spots if st.session_state.active_category == 'All' else [
        spot for spot in tourist_spots if spot['category'] == st.session_state.active_category
    ]

    # Add hover animation CSS for st.container(border=True)
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    
    st.markdown("### Tourist Spots")
    
    for i in range(0, len(filtered_spots), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(filtered_spots):
                spot = filtered_spots[i + j]
                with cols[j]:
                    with st.container(border=True):
    
                        st.markdown(f"""
                                    <div class="card-image">
                                        <img src="{spot['imageUrl']}" />
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

    
                        st.markdown(f"**{spot['category']}**")
                        

                        st.markdown(f"### {spot['name']}")
                        

                        st.markdown(spot['shortDescription'])
                        

                        info_cols = st.columns(3)
                        with info_cols[0]:
                            st.caption(f"Location: {spot['distance']}")
                        with info_cols[1]:
                            st.caption(f"Duration: {spot['duration']}")
                        with info_cols[2]:
                            st.caption(f"Best Time: {spot['bestTime']}")
                        

                        with st.expander("Highlights"):
                            for highlight in spot['highlights']:
                                st.markdown(f"• {highlight}")
                        
    
                        view_map_key = f"view_map_{spot.get('id', i+j)}"
                        if st.button("View on map", key=view_map_key, use_container_width=True):
                            st.session_state['map_center'] = spot.get('coordinates')
                            st.session_state['map_zoom'] = 15
                            st.session_state['scroll_to_map'] = True
                            st.rerun()

                        # User Reviews Section
                        with st.expander("User Reviews"):
                            reviews = spot.get('user_reviews', [])
                            if reviews:
                                for review in reviews:
                                    st.markdown(f"**{review.get('timestamp', 'Recent')}**")
                                    st.info(review.get('content'))
                            else:
                                st.write("No reviews yet. Be the first to write one!")
                            
                            st.divider()
                            review_key = f"review_input_{spot.get('id')}"
                            new_review = st.text_area("Write a review", key=review_key)
                            if st.button("Submit Review", key=f"submit_{spot.get('id')}"):
                                if new_review.strip():
                                    add_review(spot.get('id'), new_review)
                                    st.success("Review saved!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.warning("Please write something before submitting.")

    
    st.markdown("""
        <style>
        .floating-map-button {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
            background: linear-gradient(90deg, #4ECDC4 0%, #556270 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            cursor: pointer;
            border: none;
            transition: all 0.3s ease;
        }
        
        .floating-map-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }
        </style>
        
        <a href="#map-section" style="text-decoration: none;">
            <button class="floating-map-button">
                 View Map
            </button>
        </a>
        """, unsafe_allow_html=True)

    # Map section anchor
    st.markdown('<div id="map-section"></div>', unsafe_allow_html=True)

    # Scroll logic if triggered
    if st.session_state.get('scroll_to_map', False):
        components.html(
            """
            <script>
                // Use a slight delay to ensure the DOM is ready
                setTimeout(function() {
                    const element = window.parent.document.getElementById('map-section');
                    if (element) {
                        element.scrollIntoView({behavior: 'smooth'});
                    }
                }, 100);
            </script>
            """,
            height=0
        )
        st.session_state['scroll_to_map'] = False


    if tourist_spots:

        default_center = tourist_spots[0].get('coordinates', [33.75, 129.69])
        map_center = st.session_state.get('map_center', default_center)
        map_zoom = st.session_state.get('map_zoom', 11)
        
        map_all = folium.Map(location=map_center, zoom_start=map_zoom, tiles="OpenStreetMap")

        marker_cluster = MarkerCluster()
        bounds = []
        for spot in tourist_spots:
            coords = spot.get('coordinates')
            if coords and len(coords) >= 2:
                popup_html = f"<b>{spot['name']}</b><br><img src=\"{spot.get('imageUrl')}\" style=\"width:180px;max-width:90%;height:auto;\"><br>{spot.get('shortDescription','')}"
                folium.Marker(
                    location=coords,
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=spot['name']
                ).add_to(marker_cluster)
                bounds.append(coords)

        marker_cluster.add_to(map_all)
        
        if 'map_center' not in st.session_state and bounds:
             map_all.fit_bounds(bounds, padding=(30, 30))

        st.markdown("---")
        st.markdown("### See all locations on the map")
        st_folium(map_all, width="100%", height=480)
    else:
        st.warning("No tourist spots found to display on the map.")

    st.markdown("---")

def main():
    st.set_page_config(page_title="Iki Island Tourist Spots", layout="wide")
    # Load Custom CSS
    st.header("IKI ISLAND", anchor="ikiisland")
    st.title("Discover Iki Island")
    st.markdown("Explore the hidden treasures of Iki Island")
    
    tourist_data = load_tourist_spots()
    render_sidebar_chatbot(tourist_data)
    render_tourist_content()

if __name__ == "__main__":
    main()
