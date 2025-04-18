import streamlit as st
from streamlit_chat import message
import requests
import pandas as pd
from url_handler import is_url, extract_url, get_job

# App Configuration
API_ENDPOINT = "https://shl-recommendation-system-fpr1.onrender.com/recommend"
PROJECT_LINK = "https://github.com/jazz023/SHL-Recommendation-System"

# Dark Theme with SHL Logo Complementary Colors
st.markdown("""
<style>
    /* Main Dark Theme */
    .stApp {
        background-color: #1E1E1E !important;
        color: #E0E0E0;
    }
    
    /* Text colors */
    h1, h2, h3 {
        color: #E0E0E0 !important;
    }
    p {
        color: #CCCCCC !important;
    }
    
    /* Green Accent from SHL logo */
    .accent {   
        color: #7CCD32 !important;
    }
    
    /* Cards and containers */
    .dark-card {
        background-color: #2D2D2D;
        border: 1px solid #3D3D3D;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Button hover effect with SHL green */
    .stButton>button:hover {
        background-color: #7CCD32 !important;
        border-color: #7CCD32 !important;
        color: #1E1E1E !important;
        transition: all 0.3s ease;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #3D3D3D;
        color: #E0E0E0;
        border: 1px solid #7CCD32;
        transition: all 0.3s ease;
    }
    
    /* Data tables */
    [data-testid="stDataFrame"] {
        background-color: #2D2D2D;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #2D2D2D !important;
        border: 1px solid #3D3D3D;
    }
    
    /* Links */
    a {
        color: #7CCD32 !important;
    }
    a:hover {
        color: #9DE057 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_name_mapping():
    df = pd.read_csv("app/data/shl_product_details.csv")
    return pd.Series(df.Name.values, index=df.URL.str.strip()).to_dict()

def main():
    st.markdown("""
        <style>
            /* Logo styling */
            [data-testid="column"]:first-child {
                background-color: #2D2D2D;
                border-radius: 8px;
                padding: 10px !important;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* Image background */
            [data-testid="stImage"] {
                background-color: #F5F5F5;
                border-radius: 8px;
                padding: 10px;
            }
        </style>
        """, unsafe_allow_html=True)
    
    url_to_name = load_name_mapping()
    
    # Header with light box for logo
    col1, col2 = st.columns([1,6])
    with col1:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image("app/data/shl-logo.png", width=80)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div style="text-align: right; padding-top: 15px;"><a href="{PROJECT_LINK}">GitHub Repository →</a></div>', 
            unsafe_allow_html=True
        )
    
    # Welcome Page
    if 'conversation' not in st.session_state:
        st.title("SHL Assessment Recommender")
        st.markdown("""
        <div class="dark-card">
            <h3 style="margin-bottom: 1rem;">🚀 Get Started</h3>
            <p>Welcome to the SHL Assessment Recommendation System!</p>
            <p>Describe your hiring needs in natural language or paste a job description below.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📘 Quick Start Guide", expanded=False):
            st.markdown("""
            **Try these sample queries:**
            - "Java developers collaborating with business teams, 40 mins max"
            - "Python analysts with SQL skills under 60 minutes"
            - "Cognitive tests for analysts in 45 mins"
            
            **Features:**
            
            ✅ Natural language processing  
            ✅ Multi-criteria recommendations  
            ✅ Instant JSON export
            """)
        
        st.session_state.conversation = []

    # Chat Interface
    user_input = st.chat_input("💬 Describe your hiring needs...")
    
    if user_input:
        # Add user message
        if is_url(user_input):
            with st.spinner("📥 Analyzing job description URL..."):
                try:
                    url = extract_url(user_input)
                    processed_url = get_job(url)   
                    
                    st.session_state.conversation.append({
                        'role': 'user',
                        'content': user_input,
                        'avatar_style': 'micah'
                    })
                    user_input = user_input + "\n" + processed_url
                    st.session_state.conversation.append({
                        'role': 'user',
                        'content': 'Extracted JD:\n' + processed_url,
                        'avatar_style': 'micah'
                    })
                except Exception as e:
                    st.error("⚠️ Failed to extract job description from URL. Kindly manually enter job description.")
        else:
            st.session_state.conversation.append({
            'role': 'user',
            'content': user_input,
            'avatar_style': "micah"
            })   
            
        
        try:
            # API Call
            with st.spinner("🔍 Finding best assessments..."):
                response = requests.post(
                    API_ENDPOINT,
                    json={"query": user_input}
                )
            
            if response.status_code == 200:
                recommendations = response.json()['recommended_assessments']
                
                # Add bot response
                st.session_state.conversation.append({
                    'role': 'assistant',
                    'content': recommendations,
                    'avatar_style': "bottts"
                })
            else:
                st.warning("⚠️ API request failed. Please try again.")
                
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection Error: Please ensure the API server is running")

    # Display Conversation
    for idx, msg in enumerate(st.session_state.conversation):
        if msg['role'] == 'user':
            message(msg['content'], 
                    is_user=True, 
                    key=f"user_{idx}",
                    avatar_style="micah")
        else:
            with st.container():
                message("📋 Recommended Assessments", 
                       key=f"bot_{idx}", 
                       avatar_style="bottts")
                
                # Create styled dataframe
                try:
                    
                    data = msg['content']
                        
                    # Create DataFrame with proper column handling
                    df = pd.DataFrame([{
                        "name": url_to_name.get(item.get('url', ''), "Unknown Assessment"),
                        "duration": str(item.get('duration')) or "N/A",
                        "test_type": ", ".join(
                            item.get('test_type', []) if isinstance(item.get('test_type', []), list)
                            else item.get('test_type', '').split(', ')
                        ),
                        "remote_support": item.get('remote_support', 'No'),
                        "adaptive_support": item.get('adaptive_support', 'No'),
                        "url": item.get('url', '')
                    } for item in data if isinstance(item, dict)])
                    
                    # Display table with 1-based index
                    df.index = df.index + 1  # Start from 1 instead of 0
                    
                    st.dataframe(
                        df.style
                        .set_properties(**{'color': '#E0E0E0', 'background-color': '#2D2D2D'})
                        .map(lambda x: 'color: #7CCD32; font-weight: 500' if str(x) == 'Yes' else '', 
                                subset=['remote_support','adaptive_support']),
                        use_container_width=True,   
                        height=400,
                        column_config={
                            "url": st.column_config.LinkColumn(
                                "Assessment Link",
                                help="Click to view assessment details",
                                display_text="View Assessment"
                            )
                        }
                    )
                except Exception as e:
                    st.error(f"Error displaying results: {str(e)}")
                    st.json(msg['content'])
                
                # Download button
                st.download_button(
                    label="📥 Download Recommendations",
                    data=pd.DataFrame(msg['content']).to_json(indent=2),
                    file_name="shl_recommendations.json",
                    mime="application/json",
                    help="Download all recommendations in JSON format",
                    key=f"download_{idx}"
                )

if __name__ == "__main__":
    main()