import streamlit as st

def navigation_menu():
    st.sidebar.title("Navigation Menu")
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("app.py", label="Home")
    st.sidebar.page_link("pages/grade_distribution.py", label="Grade Distribution")
    st.sidebar.page_link("pages/gpa_distribution_app.py", label="GPA Distribution")
    st.sidebar.page_link("pages/cumulative_gpa_app.py", label="Cumulative GPA")
    
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("© 2025 TAMU Statistics. All rights reserved.")
    # st.sidebar.markdown("Developed by Luca Giannotti.")
    # st.sidebar.markdown("All data is sourced from the [Registrar Grade Report](https://web-as.tamu.edu/gradereports/).")
    
    
def credits():
    st.sidebar.markdown("---")
    st.sidebar.markdown("All data is sourced from the [Registrar Grade Report](https://web-as.tamu.edu/gradereports/).")

    