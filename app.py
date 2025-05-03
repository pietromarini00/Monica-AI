import streamlit as st
from src.chat import handle_user_message  # Make sure this function exists

st.set_page_config(page_title="Monica – Wedding Planner AI", page_icon="💍")
st.title("💍 Monica – Your Wedding Planner Assistant")

st.write("Hello! I'm Monica, your AI wedding planner. Let's get started with a few quick details.")

# Onboarding form
with st.form("onboarding_form"):
    location = st.text_input("📍 Where is the wedding?")
    budget = st.text_input("💸 What's your budget?")
    guests = st.number_input("👥 Number of guests", min_value=1, max_value=1000, value=100)
    theme = st.text_input("🎨 Do you have a theme or style in mind?")
    date = st.date_input("📅 Wedding Date")

    submitted = st.form_submit_button("Save and Continue")

if submitted:
    st.success("Great! Let's start planning.")
    st.session_state.onboarding = {
        "location": location,
        "budget": budget,
        "guests": guests,
        "theme": theme,
        "date": str(date),
    }

# Check if onboarding was completed
if "onboarding" in st.session_state:
    st.subheader("💬 Chat with Monica")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("What can I help you with now?")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        response = handle_user_message(user_input)
        st.chat_message("assistant").markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})