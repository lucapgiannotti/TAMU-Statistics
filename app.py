import streamlit as st
from pages.menu import navigation_menu, credits

st.set_page_config(page_title="TAMU Statistics", page_icon="📊")

st.title("Welcome to the TAMU Statistics App!")
st.write("This is a simple Streamlit app that demonstrates how to use Streamlit for building interactive web applications. The app includes a navigation menu to explore different features or pages.")

# Description of each navigation_menu option
st.subheader("Navigation Menu Options:")
st.write("""
1. **Home**: The main landing page of the app with a welcome message and overview.
2. **Grade Distribution**: Search for a specific class (CSCE 120, ENGR 181) and view average GPA by year, term, and professor.
3. **GPA Distribution**: View graphs and statistics about a specific college (Engineering, Public Health), including total students, average GPA, and more.
4. **Cumulative GPA**: WORK IN PROGRESS.
""")

# Footer
st.markdown("---")
st.markdown("© 2025 TAMU Statistics. All rights reserved.")
st.markdown("Developed by Luca Giannotti.")
navigation_menu()
credits()