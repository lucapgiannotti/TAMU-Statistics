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
            data = data.set_index(pd.Index(data["GPA Group"]))
            data.drop(columns=["GPA Group"], inplace=True)
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
    weighted_sum = 0
    total_students = 0
    for class_level in ['Freshman', 'Sophomore', 'Junior', 'Senior']:
        student_count = row[f'{class_level} {gender}']
        weighted_sum += row['GPA Midpoint'] * student_count
        total_students += student_count
    return weighted_sum / total_students if total_students > 0 else 0

def descriptive_statistics(data):
    st.write("## 1. Descriptive Statistics")

    data['Total Students'] = data[['Freshman Total', 'Sophomore Total', 'Junior Total', 'Senior Total']].sum(axis=1)
    overall_total_students = data['Total Students'].sum()
    data['Percentage'] = (data['Total Students'] / overall_total_students) * 100

    st.write("#### 1.1. Total Students and Percentage by GPA Group")
    st.write(f"**Total Students:** {overall_total_students:,}")
    st.dataframe(data[['Total Students', 'Percentage']])

    st.write("#### 1.2. Aggregated Data: Student Count by Gender")
    gender_summary = data[[col for col in data.columns if 'Male' in col or 'Female' in col]].sum()
    gender_summary_df = pd.DataFrame(gender_summary, columns=['Student Count'])

    total_men = gender_summary_df.loc[gender_summary_df.index.str.contains('Male'), 'Student Count'].sum()
    total_women = gender_summary_df.loc[gender_summary_df.index.str.contains('Female'), 'Student Count'].sum()

    st.dataframe(gender_summary_df)

    st.write(f"**Total Men:** {total_men:,}")
    st.write(f"**Total Women:** {total_women:,}")

    if total_women > 0:
        ratio = total_men / total_women
        st.write(f"**Ratio (Men:Women):** {ratio:.2f}")
    else:
        st.write("**Ratio (Men:Women):** Undefined (no women in data)")
    
def hypothesis_testing(data):
    st.write("## 2. Hypothesis Testing")
    st.write("#### 2.1. GPA Across Class Levels")

    # Expand the data so that each student is represented by a single row
    student_rows = []
    for idx, row in data.iterrows():
        gpa_val = row['GPA Midpoint']
        for level in ['Freshman', 'Sophomore', 'Junior', 'Senior']:
            count_val = row[f'{level} Total']
            for _ in range(int(count_val)):
                student_rows.append({'Class Level': level, 'GPA': gpa_val})


    expanded_df = pd.DataFrame(student_rows)

    st.write("##### Box Plot: GPA Distribution by Class Level")
    fig_box, ax_box = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='Class Level', y='GPA', data=expanded_df, ax=ax_box)
    ax_box.set_title("GPA Distribution by Class Level")
    st.pyplot(fig_box)

def trend_pattern_analysis(data):
    st.write("## 3. Trend/Pattern Analysis")
    st.write("#### 3.1. Patterns across different GPA ranges and class years")
    st.write("##### Line Plot: GPA Trends across Class Years")
    fig_line, ax_line = plt.subplots(figsize=(12, 6))
    for class_level in ['Freshman Total', 'Sophomore Total', 'Junior Total', 'Senior Total']:
        ax_line.plot(data['GPA Midpoint'], data[class_level], marker='o', label=class_level)
    ax_line.set_xlabel('GPA Midpoint')
    ax_line.set_ylabel('Number of Students')
    ax_line.set_title('GPA Trends across Class Years')
    ax_line.legend()
    st.pyplot(fig_line)
    
def gender_based_analysis(data):
    st.write("## 4. Gender-Based GPA Analysis")

    # Stacked Bar Plot: Gender Distribution across GPA Groups
    st.write("#### 4.1. Distribution of GPA groups for male and female students")
    fig_stacked, ax_stacked = plt.subplots(figsize=(12, 6))
    
    # Ensure that the columns exist before plotting
    male_cols = [col for col in data.columns if 'Male' in col and col != 'Total']
    female_cols = [col for col in data.columns if 'Female' in col and col != 'Total']
    
    # Combine male and female columns for plotting
    if male_cols and female_cols:
        male_data = data[male_cols].sum(axis=1)
        female_data = data[female_cols].sum(axis=1)
        
        # Create a DataFrame for plotting
        gender_data = pd.DataFrame({'Male': male_data, 'Female': female_data})
        gender_data.plot(kind='bar', stacked=True, ax=ax_stacked)
        
        ax_stacked.set_xlabel('GPA Group')
        ax_stacked.set_ylabel('Number of Students')
        ax_stacked.set_title('Gender Distribution across GPA Groups')
        ax_stacked.tick_params(axis='x', rotation=45)
        st.pyplot(fig_stacked)
    else:
        st.warning("Required 'Male' or 'Female' columns not found for stacked bar plot.")

    # Line Plot: Average GPA by Gender and Class Level
    st.write("#### 4.2. Comparison of average GPA between genders across class levels")
    class_levels = ['Freshman', 'Sophomore', 'Junior', 'Senior']
    
    # Calculate GPA values for overall GPA distribution statistics
    gpa_values = []
    for index, row in data.iterrows():
        gpa = row['GPA Midpoint']
        total_students_in_range = row[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male',
                                        'Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum()
        gpa_values.extend([gpa] * int(total_students_in_range))

    gpa_series = pd.Series(gpa_values)

    summary_data = []

    for class_level in class_levels:
        total_male_students = data[f'{class_level} Male'].sum()
        total_female_students = data[f'{class_level} Female'].sum()
        total_students = total_male_students + total_female_students
        
        # Calculate weighted GPA for male and female students
        male_weighted_gpa = (data['GPA Midpoint'] * data[f'{class_level} Male']).sum()
        female_weighted_gpa = (data['GPA Midpoint'] * data[f'{class_level} Female']).sum()
        
        # Calculate average GPA for male and female students
        average_male_gpa = male_weighted_gpa / total_male_students if total_male_students > 0 else 0
        average_female_gpa = female_weighted_gpa / total_female_students if total_female_students > 0 else 0
        average_total_gpa = (male_weighted_gpa + female_weighted_gpa) / total_students if total_students > 0 else 0
        
        summary_data.append([average_male_gpa, average_female_gpa, average_total_gpa])

    # Calculate totals across all class levels
    total_male_students = data[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male']].sum().sum()
    total_female_students = data[['Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum().sum()
    total_students = total_male_students + total_female_students

    # Calculate weighted GPA for all students
    total_male_gpa = (data['GPA Midpoint'] * data[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male']].sum(axis=1)).sum()
    total_female_gpa = (data['GPA Midpoint'] * data[['Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum(axis=1)).sum()
    total_gpa = total_male_gpa + total_female_gpa

    # Calculate average GPA for all students
    average_male_gpa = total_male_gpa / total_male_students if total_male_students > 0 else 0
    average_female_gpa = total_female_gpa / total_female_students if total_female_students > 0 else 0
    average_total_gpa = total_gpa / total_students if total_students > 0 else 0
    summary_data.append([average_male_gpa, average_female_gpa, average_total_gpa])

    # Create DataFrame for summary data
    summary_df = pd.DataFrame(summary_data, index=class_levels + ['Total'], columns=['Male', 'Female', 'Total'])
    
    st.dataframe(summary_df)

    class_levels = ['Freshman', 'Sophomore', 'Junior', 'Senior']
    male_gpa_by_class = summary_df.loc[class_levels, 'Male'].to_dict()
    female_gpa_by_class = summary_df.loc[class_levels, 'Female'].to_dict()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(class_levels, male_gpa_by_class.values(), marker='o', label='Male', color='blue')
    ax.plot(class_levels, female_gpa_by_class.values(), marker='o', label='Female', color='pink')
    ax.set_xlabel('Class Level')
    ax.set_ylabel('Average GPA')
    ax.set_title('Average GPA by Gender and Class Level')
    ax.set_ylim(0, 4.0)
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)


def gpa_class_level_statistics(data):
    st.write("## 6. Overall GPA Distribution Statistics")

    # Collect GPA values for overall GPA distribution statistics
    gpa_values = []
    for index, row in data.iterrows():
        gpa = row['GPA Midpoint']
        total_students_in_range = row[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male',
                                        'Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum()
        gpa_values.extend([gpa] * int(total_students_in_range))

    gpa_series = pd.Series(gpa_values)

    # Calculate GPA distribution statistics
    median_gpa = gpa_series.median()
    q1_gpa = gpa_series.quantile(0.25)
    q3_gpa = gpa_series.quantile(0.75)

    percent_above_b = (gpa_series >= 3.0).sum() / len(gpa_series) * 100 if len(gpa_series) > 0 else 0
    percent_above_c = (gpa_series >= 2.0).sum() / len(gpa_series) * 100 if len(gpa_series) > 0 else 0
    percent_above_d = (gpa_series >= 1.0).sum() / len(gpa_series) * 100 if len(gpa_series) > 0 else 0


    st.write(f"**Median GPA:** {median_gpa:.2f}")
    st.write(f"**First Quartile (Q1):** {q1_gpa:.2f}")
    st.write(f"**Third Quartile (Q3):** {q3_gpa:.2f}")
    st.write(f"**Percentage of students with GPA above B (3.0):** {percent_above_b:.2f}%")
    st.write(f"**Percentage of students with GPA above C (2.0):** {percent_above_c:.2f}%")
    st.write(f"**Percentage of students with GPA above D (1.0):** {percent_above_d:.2f}%")

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
        
        data['GPA Midpoint'] = data.index.to_series().apply(extract_gpa_midpoint)
        
        st.write(f"### Showing Data for: **{selected_college.replace('_', ' ')} - {selected_semester.title()} {selected_year}**")
        st.dataframe(data.drop(columns=['GPA Midpoint']).style.hide(axis="index"), width=2000, height=500)


        descriptive_statistics(data)
        descriptive_statistics(data)
        hypothesis_testing(data)
        trend_pattern_analysis(data)
        gender_based_analysis(data)
        gpa_class_level_statistics(data)
    else:
        st.write("⚠️ No matching data found for the selected combination. Please choose different filters.")
if __name__ == "__main__":
    main()
    credits()
