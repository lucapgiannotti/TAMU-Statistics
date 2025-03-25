import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pages.templates.menu import navigation_menu, credits
import datetime
import streamlit as st


@st.cache_data
def load_data(file_path):
    with st.spinner('Loading total course data...'):
        return pd.read_csv(file_path)


def filter_dataframe(df, exclude_summer, course_title_search, course_id_search):
    """Filters the DataFrame based on user inputs."""
    if exclude_summer:
        df = df[~df['term'].str.contains('Summer', case=False, na=False)]

    if course_title_search:
        df = df[df["course"].fillna('').str.contains(course_title_search, case=False)]

    if course_id_search:
        df = df[df["course"].fillna('').str.contains(course_id_search, case=False)]



    # Do this before the user gets to the web page
    for instructor in df['instructor'].unique():
        if str(instructor).endswith(course_title_search):
            df.loc[df['instructor'] == instructor, 'instructor'] = instructor[:-4]
    for course in df['course'].unique():
        if str(course)[-3:].startswith('2'):
            instructor = df.loc[df['course'] == course, 'instructor'].iloc[0]
            df.loc[df['course'] == course, 'instructor'] = instructor + " (H)"
            
            
    return df


def process_dataframe(df):
    df = df.sort_values(by=['year', 'term', 'instructor'], ascending=[False, False, True])
    df['instructor'] = df['instructor'].apply(lambda x: x + " (H)" if str(x)[-3:].startswith('2') else x)
    columns = ['instructor', 'year', 'term', 'gpa'] + [col for col in df.columns if
                                                        col not in ['instructor', 'year', 'term', 'gpa']]
    df = df[columns]
    return df

def create_gpa_plot(df):
    import plotly.express as px

    df = df.copy()
    df = df[(df['year'] >= 2019) & (df['year'] <= 2024)]

    term_order = {"Spring": 1, "Summer": 2, "Fall": 3}
    df['term_order'] = df['term'].map(term_order)
    df = df.sort_values(by=['year', 'term_order'])

    df['year_term'] = df['year'].astype(str) + " " + df['term']
    df['year_term'] = pd.Categorical(df['year_term'], categories=df['year_term'].unique(), ordered=True)

    avg_gpa_per_instructor = df.groupby(['instructor', 'year_term'])['gpa'].mean().reset_index()

    fig = px.line(
        avg_gpa_per_instructor,
        x='year_term',
        y='gpa',
        color='instructor',
        title='Average GPA Trend by Instructor (Year & Term)',
        labels={'gpa': 'Average GPA', 'year_term': 'Year & Term'},
        hover_data=['gpa'],
        markers=True
    )
    fig.update_layout(width=1200, height=800, hovermode='closest')
    fig.update_traces(
        hovertemplate='Instructor: %{fullData.name}<br>Year & Term: %{x}<br>GPA: %{y:.2f}'
    )
    return fig

def best_instructors(df):
    current_year = datetime.datetime.now().year
    cutoff = current_year - 2
    recent_df = df[df["year"] >= cutoff]
    best_df = (
        recent_df.groupby("instructor")["gpa"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"gpa": "Average GPA", "instructor": "Instructor"})
    )
    best_df = best_df.set_index(pd.Index(best_df["Instructor"]))
    best_df.drop(columns=["Instructor"], inplace=True)
    st.write("**Best Instructors by Average GPA (Last 2 Years)**")
    st.dataframe(best_df)


def main():
    st.set_page_config(page_title="Grade Distribution", page_icon="📊")
    navigation_menu()
    credits()

    df = load_data("csv_data/gradeDistribution/combined_grade_distribution.csv")

    exclude_summer = st.checkbox("Exclude Summer Terms", value=True)
    course_title_search = st.text_input("Search by Course Title (e.g., CSCE, MATH)")
    course_id_search = st.text_input("Search by Course ID (e.g., 120, 251)")
    with st.spinner('Loading data...'):
        filtered_df = filter_dataframe(df, exclude_summer, course_title_search, course_id_search)
    filtered_df = filter_dataframe(df, exclude_summer, course_title_search, course_id_search)

    if filtered_df.empty:
        st.write("No results found")
    elif course_title_search or course_id_search:
        processed_df = process_dataframe(filtered_df)
        fig = create_gpa_plot(processed_df)
        st.plotly_chart(fig)
        best_instructors(processed_df)
        st.dataframe(processed_df.style.hide(axis="index"), width=2000, height=500)
   


if __name__ == "__main__":
    main()