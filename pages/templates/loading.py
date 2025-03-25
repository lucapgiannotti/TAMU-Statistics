import streamlit as st
import time

def show_loading_screen():
    """
    Displays a loading screen with a progress bar.
    """
    with st.spinner("Loading data... Please wait."):
        # Simulate a long-running task (replace with your actual data loading)
        time.sleep(2)  # Simulate 2 seconds of loading time