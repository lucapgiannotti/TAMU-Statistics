import streamlit as st
import pandas as pd
from pages.menu import navigation_menu, credits
import matplotlib.pyplot as plt


st.set_page_config(page_title="Grade Distribution", page_icon="📊")
navigation_menu()
credits()


# Load data once
df = pd.read_csv("csv_data/gradeDistribution/combined_grade_distribution.csv")

# Add a button to filter out summer terms
exclude_summer = st.checkbox("Exclude Summer Terms", value=True)

# Filter out summer terms if the box is checked
if exclude_summer:
    df = df[~df['term'].str.contains('Summer', case=False, na=False)]

# Create search bars
course_title_search = st.text_input("Search by Course Title")
course_id_search = st.text_input("Search by Course ID")

# Filter data based on search criteria
filtered_df = df.copy()
if course_title_search:
    filtered_df = filtered_df[filtered_df["course"].fillna('').str.contains(course_title_search, case=False)]
if course_id_search:
    filtered_df = filtered_df[filtered_df["course"].fillna('').str.contains(course_id_search, case=False)]
# Display the filtered DataFrame
if filtered_df.empty:
    st.write("No results found")
if course_title_search == "" or course_id_search == "":
    pass
else:
    filtered_df = filtered_df.sort_values(by=['year', 'term', 'instructor'], ascending=[False, False, True])
    # Reorder columns to put 'instructor' on the far left
    filtered_df['instructor'] = filtered_df['instructor'].apply(lambda x: x + " (H)" if str(x)[-3:].startswith('2') else x)
    columns = ['instructor', 'year', 'term', 'gpa'] + [col for col in filtered_df.columns if col not in ['instructor', 'year', 'term', 'gpa']]
    filtered_df = filtered_df[columns]
    st.dataframe(filtered_df.style.hide(axis="index"), width=2000, height=500)
    # Group by instructor and calculate average GPA over the years
    avg_gpa_per_instructor = filtered_df.groupby(['instructor', 'year'])['gpa'].mean().reset_index()

    # Filter years from 2019 to 2024
    avg_gpa_per_instructor = avg_gpa_per_instructor[(avg_gpa_per_instructor['year'] >= 2019) & (avg_gpa_per_instructor['year'] <= 2024)]

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size as needed

    # Iterate through each instructor and plot their GPA trend
    for instructor in avg_gpa_per_instructor['instructor'].unique():
        instructor_data = avg_gpa_per_instructor[avg_gpa_per_instructor['instructor'] == instructor]
        ax.plot(instructor_data['year'], instructor_data['gpa'], label=instructor)

    # Customize the plot
    ax.set_xlabel('Year')
    ax.set_ylabel('Average GPA')
    ax.set_title('Average GPA Trend by Instructor Over Years')
    ax.legend(title='Instructor', bbox_to_anchor=(1.05, 1), loc='upper left')  # Place legend outside the plot
    ax.grid(True)

    # Show the plot in Streamlit
    st.pyplot(fig)
    