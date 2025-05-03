import streamlit as st
from pydantic import BaseModel
import datetime

from data.venues import venues


class OnboardingForm(BaseModel):
    location: str
    budget: str
    guests: int
    date: str
    theme: str

    def to_string(self):
        return f"Location: {self.location}, Budget: {self.budget}, Guests: {self.guests}, Date: {self.date}, Theme: {self.theme}"


st.set_page_config(
    page_title="Monica – Wedding Planner AI",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


from src.chat import Chat

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


async def homepage():
    # Header with gradient background
    _, col1, _ = st.columns([1, 3, 1])
    with col1:
        st.markdown(
            """
            <div style='background: linear-gradient(to right, #ff6b6b, #ff8e8e);
                       padding: 2rem;
                       border-radius: 15px;
                       margin-bottom: 2rem;
                       color: white;'>
            <h1 style='margin: 0;'>💍 Monica – Your Wedding Planner Assistant</h1>
            <p style='margin: 0.5rem 0 0 0;'>Hello! I'm Monica, your AI wedding planner. Let's get started with a few quick details.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.form("onboarding_form"):
            col1, col2 = st.columns(2)
            with col1:
                location = st.text_input(
                    "📍 Where is the wedding?", value="San Diego, CA"
                )
                budget = st.text_input("💸 What's your budget?", value="$30,000")
            with col2:
                guests = st.number_input(
                    "👥 Number of guests", min_value=1, max_value=1000, value=100
                )
                date = st.date_input(
                    "📅 Wedding Date", value=datetime.date(2025, 6, 15)
                )

            theme = st.text_input(
                "🎨 Do you have a theme or style in mind?", value="Modern and elegant"
            )

            submitted = st.form_submit_button(
                "Save and Start Chat", use_container_width=True
            )

        if submitted:
            st.success("Great! Let's start planning.")
            st.session_state.onboarding = OnboardingForm(
                location=location,
                budget=budget,
                guests=guests,
                theme=theme,
                date=str(date),
            )

        if "onboarding" in st.session_state:
            st.markdown("### 💬 Chat with Monica")

            if "chat" not in st.session_state:
                st.session_state.chat = Chat(st.session_state.onboarding)
                # Add initial form message
                initial_message = st.session_state.onboarding.to_string()
                st.session_state.chat_history = [
                    {"role": "user", "content": initial_message}
                ]

                # Get and display initial response
                response = await st.session_state.chat.run(initial_message)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )

            # Display chat history
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            # Chat input for subsequent messages
            if prompt := st.chat_input("What would you like to know?"):
                st.chat_message("user").markdown(prompt)
                st.session_state.chat_history.append(
                    {"role": "user", "content": prompt}
                )

                response = await st.session_state.chat.run(prompt)
                st.chat_message("assistant").markdown(response)
