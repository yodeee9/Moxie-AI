import streamlit as st


def update_chat_history(message, sender):
    """Appends a new message to the chat history stored in the Streamlit session state."""
    chat_history = st.session_state.get("chat_history", [])
    chat_history.append({"sender": sender, "message": message})
    st.session_state.chat_history = chat_history
