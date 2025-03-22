import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# File directory
DATA_DIR = "csv_data/gpaDistribution"

# Cache the file loading process
@st.cache_data
def load_file_info(data_dir):
    file_list = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]

    # Parse and map file names to extract college, year, and semester
    file_info = []
    for file in file_list:
        parts = file.replace(".csv", "").split("_")
        print(parts)
        year, semester, college_name = parts[0], parts[1], " ".join(parts[2:])
        file_info.append({"year": year, "semester": semester, "college": college_name, "file_path": os.path.join(DATA_DIR, file)})
    return file_info

file_info = load_file_info(DATA_DIR)

print("File Info:", file_info)  # Debugging

# Create unique lists for dropdowns
years = sorted(set([info["year"] for info in file_info]))
semesters = sorted(set([info["semester"] for info in file_info]))
colleges = sorted(set([info["college"] for info in file_info]))

# Streamlit UI
st.title("📊 College GPA Data Explorer")
st.sidebar.header("Select College, Year, and Semester")

# Dropdowns for selection
selected_year = st.sidebar.selectbox("Choose Year:", years)
selected_semester = st.sidebar.selectbox("Choose Semester:", semesters)
selected_college = st.sidebar.selectbox("Choose College:", colleges)


# Filter selected file based on user choice
selected_file_info = None
for info in file_info:
    if (info["year"] == selected_year and 
        info["semester"] == selected_semester and 
        info["college"] == selected_college):
        selected_file_info = info
        break

# Load the selected file
if selected_file_info:
    file_path = selected_file_info["file_path"]
    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        st.stop()
    except pd.errors.EmptyDataError:
        st.error(f"No data in file: {file_path}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading file: {file_path}. Error: {e}")
        st.stop()
    
    st.write(f"### Showing Data for: **{selected_college.replace('_', ' ')} - {selected_semester.title()} {selected_year}**")
    st.dataframe(data.head(10))
    
    # 1. Descriptive Statistics
    st.write("## 1. Descriptive Statistics")
    st.write("#### 1.1. Basic Statistics of GPA Groups")
    st.write(data['GPA Group'].describe())

    # Calculate total students and percentage
    data['Total Students'] = data[['Freshman Total', 'Sophomore Total', 'Junior Total', 'Senior Total']].sum(axis=1)
    overall_total_students = data['Total Students'].sum()
    data['Percentage'] = (data['Total Students'] / overall_total_students) * 100

    # GPA Midpoint Calculation
    def extract_gpa_midpoint(gpa_group):
        if gpa_group == '4.000':
            return 4.0
        else:
            lower, upper = gpa_group.split('-')
            return (float(lower) + float(upper)) / 2

    data['GPA Midpoint'] = data['GPA Group'].apply(extract_gpa_midpoint)

    st.write("#### 1.2. Aggregated Data: Gender-wise Performance")
    gender_summary = data[[col for col in data.columns if 'Male' in col or 'Female' in col]].sum()
    st.dataframe(gender_summary)

    # 2. Hypothesis Testing
    st.write("## 2. Hypothesis Testing")

    # 2.1. ANOVA or T-tests: GPA across class levels
    st.write("#### 2.1. GPA across class levels")
    # Melt the data for class level comparison
    data_melted = pd.melt(data, id_vars=['GPA Group'], value_vars=['Freshman Total', 'Sophomore Total', 'Junior Total', 'Senior Total'], var_name='Class Level', value_name='Student Count')
    
    # Box plots for GPA distribution by class level
    st.write("##### Box Plots: GPA Distributions by Class Level")
    fig_box, ax_box = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='Class Level', y='Student Count', data=data_melted, ax=ax_box)
    st.pyplot(fig_box)

    # 2.2. Chi-Square Test: Independence between GPA groups and gender
    st.write("#### 2.2. Independence between GPA groups and gender")
    # Create a contingency table
    contingency_table = data[['GPA Group', 'Freshman Male', 'Freshman Female', 'Sophomore Male', 'Sophomore Female', 'Junior Male', 'Junior Female', 'Senior Male', 'Senior Female']].set_index('GPA Group')
    st.dataframe(contingency_table)

    # 3. Trend/Pattern Analysis
    st.write("## 3. Trend/Pattern Analysis")

    # 3.1. Patterns across different GPA ranges and class years
    st.write("#### 3.1. Patterns across different GPA ranges and class years")
    # Line plot for GPA trends across class years
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

    # 4. Visualization for Each College
    st.write("## 4. Visualization for Each College")

    # 4.1. Bar Charts & Histograms: Distribution of GPA groups for male and female students
    st.write("#### 4.1. Distribution of GPA groups for male and female students")
    # Stacked bar plot for gender distribution across class levels
    st.write("##### Stacked Bar Plot: Gender Distribution across Class Levels")
    fig_stacked, ax_stacked = plt.subplots(figsize=(12, 6))
    data[['GPA Group', 'Freshman Male', 'Freshman Female']].set_index('GPA Group').plot(kind='bar', stacked=True, ax=ax_stacked)
    ax_stacked.set_xlabel('GPA Group')
    ax_stacked.set_ylabel('Number of Students')
    ax_stacked.set_title('Gender Distribution across Class Levels')
    ax_stacked.tick_params(axis='x', rotation=45)
    st.pyplot(fig_stacked)

    # 4.2. Box Plots: Compare GPA distributions by class level (already shown above)
    st.write("#### 4.2. Box Plots: Compare GPA distributions by class level (already shown above)")

    # 4.3. Stacked Bar Plots: Show gender distribution across class levels (already shown above)
    st.write("#### 4.3. Stacked Bar Plots: Show gender distribution across class levels (already shown above)")

    # 5. Gender-Based GPA Comparison
    st.write("## 5. Gender-Based GPA Comparison")

    # Calculate the weighted average GPA for males and females
    def calculate_weighted_average_gpa(row, gender):
        total = 0
        weighted_sum = 0
        for year in ['Freshman', 'Sophomore', 'Junior', 'Senior']:
            male_count = row[f'{year} Male']
            female_count = row[f'{year} Female']
            
            if gender == 'Male':
                weighted_sum += male_count
                total += male_count
            elif gender == 'Female':
                weighted_sum += female_count
                total += female_count
        
        if total > 0:
            return weighted_sum
        else:
            return 0

    # Calculate the total GPA * number of students for male and female
    data['Male GPA'] = data.apply(lambda row: calculate_weighted_average_gpa(row, 'Male'), axis=1)
    data['Female GPA'] = data.apply(lambda row: calculate_weighted_average_gpa(row, 'Female'), axis=1)

    # Calculate the average GPA for male and female
    total_male_students = data[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male']].sum().sum()
    total_female_students = data[['Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum().sum()

    total_male_gpa = (data['GPA Midpoint'] * data['Male GPA']).sum()
    total_female_gpa = (data['GPA Midpoint'] * data['Female GPA']).sum()

    average_male_gpa = total_male_gpa / total_male_students if total_male_students > 0 else 0
    average_female_gpa = total_female_gpa / total_female_students if total_female_students > 0 else 0

    # Create a bar plot to compare average GPA for males and females
    st.write("##### Comparison of Average GPA between Male and Female Students")
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    genders = ['Male', 'Female']
    average_gpa = [average_male_gpa, average_female_gpa]
    ax4.bar(genders, average_gpa, color=['blue', 'pink'])
    ax4.set_xlabel('Gender')
    ax4.set_ylabel('Average GPA')
    ax4.set_title('Comparison of Average GPA between Male and Female Students')
    ax4.set_ylim(0, 4.0)  # Set the limit of y axis to GPA scale
    plt.tight_layout()
    st.pyplot(fig4)

    # 6. GPA and Class Level Statistics
    st.write("## 6. GPA and Class Level Statistics")

    # Calculate GPA statistics for each class level and gender
    def calculate_gpa_stats(df, class_level, gender):
        total_students = df[f'{class_level} {gender}'].sum()
        total_gpa = (df['GPA Midpoint'] * df[f'{class_level} {gender}']).sum()
        average_gpa = total_gpa / total_students if total_students > 0 else 0
        return average_gpa

    class_levels = ['Freshman', 'Sophomore', 'Junior', 'Senior']
    genders = ['Male', 'Female']

    # Create a summary table
    summary_data = []
    for class_level in class_levels:
        male_gpa = calculate_gpa_stats(data, class_level, 'Male')
        female_gpa = calculate_gpa_stats(data, class_level, 'Female')
        total_students = data[f'{class_level} Male'].sum() + data[f'{class_level} Female'].sum()
        total_gpa = (data['GPA Midpoint'] * (data[f'{class_level} Male'] + data[f'{class_level} Female'])).sum()
        average_gpa = total_gpa / total_students if total_students > 0 else 0
        summary_data.append([male_gpa, female_gpa, average_gpa])

    # Calculate GPA statistics for each class level and gender
    def calculate_gpa_stats(df, class_level, gender):
        total_students = df[f'{class_level} {gender}'].sum()
        total_gpa = (df['GPA Midpoint'] * df[f'{class_level} {gender}']).sum()
        average_gpa = total_gpa / total_students if total_students > 0 else 0
        return average_gpa

    class_levels = ['Freshman', 'Sophomore', 'Junior', 'Senior']
    genders = ['Male', 'Female']

    # Create a summary table
    summary_data = []
    for class_level in class_levels:
        male_gpa = calculate_gpa_stats(data, class_level, 'Male')
        female_gpa = calculate_gpa_stats(data, class_level, 'Female')
        total_students = data[f'{class_level} Male'].sum() + data[f'{class_level} Female'].sum()
        total_gpa = (data['GPA Midpoint'] * (data[f'{class_level} Male'] + data[f'{class_level} Female'])).sum()
        average_gpa = total_gpa / total_students if total_students > 0 else 0
        summary_data.append([male_gpa, female_gpa, average_gpa])

    # Calculate total GPA statistics
    total_male_students = data[['Freshman Male', 'Sophomore Male', 'Junior Male', 'Senior Male']].sum().sum()
    total_female_students = data[['Freshman Female', 'Sophomore Female', 'Junior Female', 'Senior Female']].sum().sum()
    total_students = data['Total Students'].sum()

    # Calculate weighted GPA for male, female, and total
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

    # Calculate quartiles and median for total GPA distribution
    gpa_values = []
    for index, row in data.iterrows():
        gpa = row['GPA Midpoint']
        count = row['Total Students']
        gpa_values.extend([gpa] * int(count))

    gpa_series = pd.Series(gpa_values)
    median_gpa = gpa_series.median()
    q1_gpa = gpa_series.quantile(0.25)
    q3_gpa = gpa_series.quantile(0.75)

    # Calculate percentages above B (3.0), C (2.0), and D (1.0)
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
else:
    st.write("⚠️ No matching data found for the selected combination. Please choose different filters.")