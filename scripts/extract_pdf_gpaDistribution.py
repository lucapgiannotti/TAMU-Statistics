import pypdf
import pandas as pd
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = pypdf.PdfReader(pdf_file)
            if len(reader.pages) > 0:
                page = reader.pages[0]  # Get the first page
                text = page.extract_text()
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def clean_extracted_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    for i, line in enumerate(lines):
        if i < 13 or i > 29:
            continue
        elements = line.split()
        if len(elements) > 12:
            cleaned_line = ' '.join(elements[:12])
        else:
            cleaned_line = line
        cleaned_lines.append(cleaned_line)
    return '\n'.join(cleaned_lines)

def create_data_tables(text):
    lines = text.splitlines()
    data = []
    for i, line in enumerate(lines):
        elements = line.split()
        if len(elements) == 12:  # Ensure there are enough elements for all categories
            try:
                data.append({
                    "GPA Group": f"{4.0 - i * 0.25:.3f}" if i == 0 else f"{4.0 - i * 0.25:.3f}-{4.0 - (i - 1) * 0.25 - 0.001:.3f}",
                    "Freshman Male": int(elements[0]),
                    "Freshman Female": int(elements[1]),
                    "Freshman Total": int(elements[2]),
                    "Sophomore Male": int(elements[3]),
                    "Sophomore Female": int(elements[4]),
                    "Sophomore Total": int(elements[5]),
                    "Junior Male": int(elements[6]),
                    "Junior Female": int(elements[7]),
                    "Junior Total": int(elements[8]),
                    "Senior Male": int(elements[9]),
                    "Senior Female": int(elements[10]),
                    "Senior Total": int(elements[11])
                })
            except ValueError as e:
                print(f"ValueError processing line: {line}. Error: {e}")
                continue
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    pdf_directory = 'pdf_downloads/gpaDistribution'
    csv_directory = 'csv_data/gpaDistribution'

    # Ensure the output directory exists
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)

    for filename in os.listdir(pdf_directory):
        if filename.endswith('.pdf'):
            pdf_file_path = os.path.join(pdf_directory, filename)
            try:
                extracted_text = extract_text_from_pdf(pdf_file_path)
                cleaned_text = clean_extracted_text(extracted_text)
                data_frame = create_data_tables(cleaned_text)

                # Save the DataFrame to a CSV file
                csv_file_path = os.path.join(csv_directory, filename.replace('.pdf', '.csv'))
                data_frame.to_csv(csv_file_path, index=False)
                print(f"Data extracted, cleaned, and saved to {csv_file_path}")

            except Exception as e:
                print(f"Error processing {pdf_file_path}: {e}")