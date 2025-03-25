import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from pages.templates.menu import navigation_menu, credits

navigation_menu()

DATA_DIR = "csv_data/gpaDistribution"

@st.cache_data
def load_file_info(data_dir):
    with st.spinner('Loading data...'):
        file_list = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        file_info = []
        for file in file_list:
            parts = file.replace(".csv", "").split("_")
            year, semester, college_name = parts[0], parts[1], " ".join(parts[2:])
            file_info.append({"year": year, "semester": semester, "college": college_name, "file_path": os.path.join(data_dir, file)})
        
        return file_info

def load_data(file_path):
    with st.spinner("Loading data...", show_time=True):
        try:
            data = pd.read_csv(file_path)
            return data
        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
            st.stop()
        except pd.errors.EmptyDataError:
            st.error(f"No data in file: {file_path}")
            st.stop()
        except Exception as e:
            st.error(f"Error reading file: {file_path}. Error: {e}")
            st.stop()
        

def extract_gpa_midpoint(gpa_group):
    if gpa_group == '4.000':
        return 4.0
    else:
        lower, upper = gpa_group.split('-')
        return (float(lower) + float(upper)) / 2

def calculate_weighted_average_gpa(row, gender):
    total = 0
    weighted_sum = 0
    for year in ['Freshman', 'Sophomore', 'Junior', 'Senior']:
        count = row[f'{year} {gender}']
        weighted_sum += count
        total += count
    return weighted_sum if total > 0 else 0

def calculate_gpa_stats(df, class_level, gender):
    total_students = df[f'{class_level} {gender}'].sum()
    total_gpa = (df['GPA Midpoint'] * df[f'{class_level} {gender}']).sum()
    average_gpa = total_gpa / total_students if total_students > 0 else 0
    return average_gpa

def descriptive_statistics(data):
    st.write("## 1. Descriptive Statistics")
    st.write("#### 1.1. Basic Statistics of GPA Groups")
    st.write(data['GPA Group'].describe())

    data['Total Students'] = data[['Freshman Total', 'Sophomore Total', 'Junior Total', 'Senior Total']].sum(axis=1)
    overall_total_students = data['Total Students'].sum()
    data['Percentage'] = (data['Total Students'] / overall_total_students) * 100

    st.write("#### 1.1.1. Total Students and Percentage by GPA Group")
    st.write(f"**Total Students:** {overall_total_students:,}")
    st.dataframe(data[['GPA Group', 'Total Students', 'Percentage']])

    st.write("#### 1.2. Aggregated Data: Gender-wise Performance")
    gender_summary = data[[col for col in data.columns if 'Male' in col or 'Female' in col]].sum()
    new_index = [label.split('.')[0] for label in gender_summary.index]
    gender_summary.index = new_index
    st.dataframe(gender_summary)

def hypothesis_testing(data):
    st.write("## 2. Hypothesis Testing")
    st.write("#### 2.1. GPA across class levels")
    data_melted = pd.melt(data, id_vars=['GPA Group'], value_vars=['Freshman Total', 'Sophomore Total', 'Junior Total', 'Senior Total'], var_name='Class Level', value_name='Student Count')
    
    st.write("##### Box Plots: GPA Distributions by Class Level")
    fig_box, ax_box = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='Class Level', y='Student Count', data=data_melted, ax=ax_box)
    st.pyplot(fig_box)

def trend_pattern_analysis(data):
    st.write("## 3. Trend/Pattern Analysis")
    st.write("#### 3.1. Patterns across different GPA ranges and class years")
    st.write("##### Line Plot: GPA Trends across Class Years")
    fig_line, ax_line = plt.subplots(figsize=(12, 6))
    for class_level in ['Freshman Total', 'Sophomore Total', 'Junior Total', 'Senior Total']:
        ax_line.plot(data['GPA Group'], data[class_level], marker='o', label=class_level)
    ax_line.set_xlabel('GPA Group')
    ax_line.set_ylabel('Number of Students')
    ax_line.set_title('GPA Trends across Class Years')
    ax_line.tick_params(axis='x', rotation=45)
    ax_line.legend()
    st.pyplot(fig_line)

def college_visualization(data):
    st.write("## 4. Visualization for Each College")
    st.write("#### 4.1. Distribution of GPA groups for male and female students")
    st.write("##### Stacked Bar Plot: Gender Distribution across Class Levels")
    fig_stacked, ax_stacked = plt.subplots(figsize=(12, 6))
    data[['GPA Group', 'Freshman Male', 'Freshman Female']].set_index('GPA Group').plot(kind='bar', stacked=True, ax=ax_stacked)
    ax_stacked.set_xlabel('GPA Group')
    ax_stacked.set_ylabel('Number of Students')
    ax_stacked.set_title('Gender Distribution across Class Levels')
    ax_stacked.tick_params(axis='x', rotation=45)
    st.pyplot(fig_stacked)

    st.write("#### 4.2. Box Plots: Compare GPA distributions by class level (already shown above)")
    st.write("#### 4.3. Stacked Bar Plots: Show gender distribution across class levels (already shown above)")

def gender_based_gpa_comparison(data):
    st.write("## 5. Gender-Based GPA Comparison")

    data['Male GPA'] = data.apply(lambda row: calculate_weighted_average_gpa(row, 'Male'), axis=1)
    data['Female GPA'] = data.apply(lambda row: calculate_weighted_average_gpa(row, 'Female'), axis=1)

    total_male_students = data[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male']].sum().sum()
    total_female_students = data[['Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum().sum()

    total_male_gpa = (data['GPA Midpoint'] * data['Male GPA']).sum()
    total_female_gpa = (data['GPA Midpoint'] * data['Female GPA']).sum()

    average_male_gpa = total_male_gpa / total_male_students if total_male_students > 0 else 0
    average_female_gpa = total_female_gpa / total_female_students if total_female_students > 0 else 0

    st.write("##### Comparison of Average GPA between Male and Female Students")
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    genders = ['Male', 'Female']
    average_gpa = [average_male_gpa, average_female_gpa]
    ax4.bar(genders, average_gpa, color=['blue', 'pink'])
    ax4.set_xlabel('Gender')
    ax4.set_ylabel('Average GPA')
    ax4.set_title('Comparison of Average GPA between Male and Female Students')
    ax4.set_ylim(0, 4.0)
    plt.tight_layout()
    st.pyplot(fig4)

def gpa_class_level_statistics(data):
    st.write("## 6. GPA and Class Level Statistics")

    class_levels = ['Freshman', 'Sophomore', 'Junior', 'Senior']
    genders = ['Male', 'Female']
    summary_data = []

    for class_level in class_levels:
        male_gpa = calculate_gpa_stats(data, class_level, 'Male')
        female_gpa = calculate_gpa_stats(data, class_level, 'Female')
        total_students = data[f'{class_level} Male'].sum() + data[f'{class_level} Female'].sum()
        total_gpa = (data['GPA Midpoint'] * (data[f'{class_level} Male'] + data[f'{class_level} Female'])).sum()
        average_gpa = total_gpa / total_students if total_students > 0 else 0
        summary_data.append([male_gpa, female_gpa, average_gpa])

    total_male_students = data[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male']].sum().sum()
    total_female_students = data[['Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum().sum()
    total_students = data['Total Students'].sum()

    data['Weighted Male GPA'] = data['GPA Midpoint'] * data[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male']].sum(axis=1)
    data['Weighted Female GPA'] = data['GPA Midpoint'] * data[['Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum(axis=1)
    data['Weighted Total GPA'] = data['GPA Midpoint'] * data['Total Students']

    total_male_gpa = data['Weighted Male GPA'].sum()
    total_female_gpa = data['Weighted Female GPA'].sum()
    total_gpa = data['Weighted Total GPA'].sum()

    average_male_gpa = total_male_gpa / total_male_students if total_male_students > 0 else 0
    average_female_gpa = total_female_gpa / total_female_students if total_female_students > 0 else 0
    average_total_gpa = total_gpa / total_students if total_students > 0 else 0
    summary_data.append([average_male_gpa, average_female_gpa, average_total_gpa])

    summary_df = pd.DataFrame(summary_data, index=class_levels + ['Total'], columns=['Male', 'Female', 'Total'])

    gpa_values = []
    for index, row in data.iterrows():
        gpa = row['GPA Midpoint']
        count = row['Total Students']
        gpa_values.extend([gpa] * int(count))

    gpa_series = pd.Series(gpa_values)
    median_gpa = gpa_series.median()
    q1_gpa = gpa_series.quantile(0.25)
    q3_gpa = gpa_series.quantile(0.75)

    percent_above_b = (gpa_series >= 3.0).sum() / len(gpa_series) * 100 if len(gpa_series) > 0 else 0
    percent_above_c = (gpa_series >= 2.0).sum() / len(gpa_series) * 100 if len(gpa_series) > 0 else 0
    percent_above_d = (gpa_series >= 1.0).sum() / len(gpa_series) * 100 if len(gpa_series) > 0 else 0

    st.write("##### GPA Statistics by Class Level and Gender")
    st.dataframe(summary_df)

    st.write("##### Overall GPA Distribution Statistics")
    st.write(f"Median GPA: {median_gpa:.2f}")
    st.write(f"First Quartile (Q1): {q1_gpa:.2f}")
    st.write(f"Third Quartile (Q3): {q3_gpa:.2f}")
    st.write(f"Percentage of students with GPA above B (3.0): {percent_above_b:.2f}%")
    st.write(f"Percentage of students with GPA above C (2.0): {percent_above_c:.2f}%")
    st.write(f"Percentage of students with GPA above D (1.0): {percent_above_d:.2f}%")

def main():
    st.title("📊 College GPA Data Explorer")
    st.sidebar.header("Select College, Year, and Semester")

    file_info = load_file_info(DATA_DIR)
    years = sorted(set([info["year"] for info in file_info]))
    semesters = sorted(set([info["semester"] for info in file_info]))
    colleges = sorted(set([info["college"] for info in file_info]))

    selected_year = st.sidebar.selectbox("Choose Year:", years)
    selected_semester = st.sidebar.selectbox("Choose Semester:", semesters)
    selected_college = st.sidebar.selectbox("Choose College:", colleges)

    selected_file_info = next((info for info in file_info if info["year"] == selected_year and info["semester"] == selected_semester and info["college"] == selected_college), None)

    if selected_file_info:
        file_path = selected_file_info["file_path"]
        data = load_data(file_path)
        
        data['GPA Midpoint'] = data['GPA Group'].apply(extract_gpa_midpoint)
        
        st.write(f"### Showing Data for: **{selected_college.replace('_', ' ')} - {selected_semester.title()} {selected_year}**")
        st.dataframe(data.head(10))

        descriptive_statistics(data)
        hypothesis_testing(data)
        trend_pattern_analysis(data)
        college_visualization(data)
        gender_based_gpa_comparison(data)
        gpa_class_level_statistics(data)
    else:
        st.write("⚠️ No matching data found for the selected combination. Please choose different filters.")

if __name__ == "__main__":
    main()
    credits()
