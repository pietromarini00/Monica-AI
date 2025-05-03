import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Monica – Wedding Planner AI",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from src.chat import handle_user_message

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        background-color: #fafafa;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stChatMessage.user {
        background-color: #e3f2fd;
    }
    .stChatMessage.assistant {
        background-color: #f5f5f5;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
        padding: 0.5rem 1rem;
    }
    .stButton > button {
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 2rem;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stForm {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

def homepage():
    # Header with gradient background
    _, col1, _ = st.columns([1, 3, 1])
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(to right, #ff6b6b, #ff8e8e);
                       padding: 2rem;
                       border-radius: 15px;
                       margin-bottom: 2rem;
                       color: white;'>
            <h1 style='margin: 0;'>💍 Monica – Your Wedding Planner Assistant</h1>
            <p style='margin: 0.5rem 0 0 0;'>Hello! I'm Monica, your AI wedding planner. Let's get started with a few quick details.</p>
        </div>
        """, unsafe_allow_html=True)

        # Onboarding form with better styling
        with st.form("onboarding_form"):
            col1, col2 = st.columns(2)
            with col1:
                location = st.text_input("📍 Where is the wedding?")
                budget = st.text_input("💸 What's your budget?")
            with col2:
                guests = st.number_input("👥 Number of guests", min_value=1, max_value=1000, value=100)
                date = st.date_input("📅 Wedding Date")

            theme = st.text_input("🎨 Do you have a theme or style in mind?")

            submitted = st.form_submit_button("Save and Start Chat", use_container_width=True)

        if submitted:
            st.success("Great! Let's start planning.")
            st.session_state.onboarding = {
                "location": location,
                "budget": budget,
                "guests": guests,
                "theme": theme,
                "date": str(date),
            }

        # Chat interface
        if "onboarding" in st.session_state:
            st.markdown("### 💬 Chat with Monica")

            # Initialize chat history
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Display chat messages
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Chat input with custom styling
            user_input = st.chat_input(
                "What can I help you with now?",
                key="chat_input"
            )

            if user_input:
                st.chat_message("user").markdown(user_input)
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                response = handle_user_message(user_input)
                st.chat_message("assistant").markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
