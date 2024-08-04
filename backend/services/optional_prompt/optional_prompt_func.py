from config import PROMPT_EXAMPLES
from services.LLM.generate_answer import generate_answer
from services.optional_prompt.prompts import (
    SYSTEM_PROMPT_ERROR_JP,
    SYSTEM_PROMPT_SUMMARY_JP,
    SYSTEM_PROMPT_MOST_VISIT_JP,
)
import streamlit as st
import pandas as pd
from services.search_data.error_list_search import get_error_details
from services.search_data.log_search import search_data
from services.update_chat import update_chat_history
from services.search_data.manual_vector_search import search_vector_store



def execute_optional_prompt(prompt_id):
    st.session_state.waiting_for_user_id = True
    st.session_state.selected_prompt_id = prompt_id
    update_chat_history(f"{PROMPT_EXAMPLES[prompt_id]}", "user")
    update_chat_history("Please provide a user ID.", "ai")

