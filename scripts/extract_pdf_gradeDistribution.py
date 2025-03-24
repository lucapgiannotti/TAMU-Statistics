import pypdf
import pandas as pd
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = pypdf.PdfReader(pdf_file)
            if len(reader.pages) > 0:
                for page in reader.pages:
                    text += clean_extracted_text(page.extract_text())
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text

def clean_extracted_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    for i, line in enumerate(lines):
        if i < 38:
            continue
        cleaned_line = line
        cleaned_lines.append(cleaned_line)
    return '\n'.join(cleaned_lines)

import re
import re

def extract_course_data(content):
    pattern = re.compile(
        r"""(?P<course>[A-Z]+-\d{3}-\d{3})\s+(?P<a>\d+)\n\s*\d+\.\d+%\n\s+(?P<b>\d+)\n\s*\d+\.\d+%\n\s+(?P<c>\d+)\n\s*\d+\.\d+%\n\s+(?P<d>\d+)\n\s*\d+\.\d+%\n\s+(?P<e>\d+)\n\s*\d+\.\d+%\n\s+(?P<total>\d+)\s+\d+\.\d+\s+(?P<i>\d+)\s+(?P<s>\d+)\s+(?P<u>\d+)\s+(?P<q>\d+)\s+(?P<x>\d+)\s+(?P<final_total>\d+)\s+(?P<instructor>[A-Z]+(?: [A-Z]+)*)""", re.MULTILINE
    )
    
    extracted_data = []
    
    for match in pattern.finditer(content):
        extracted_data.append(
            {
                "course": match.group("course"),
                "A": int(match.group("a")),
                "B": int(match.group("b")),
                "C": int(match.group("c")),
                "D": int(match.group("d")),
                "F": int(match.group("e")),
                "total": int(match.group("total")),
                "gpa": (float(match.group("a")) * 4 + float(match.group("b")) * 3 + float(match.group("c")) * 2 + float(match.group("d")) * 1) / int(match.group("total")),
                "I": int(match.group("i")),
                "S": int(match.group("s")),
                "U": int(match.group("u")),
                "Q": int(match.group("q")),
                "X": int(match.group("x")),
                "final_total": int(match.group("final_total")),
                "instructor": match.group("instructor").strip(),
            }
        )
    
    return extracted_data


if __name__ == '__main__':
    pdf_directory = 'pdf_downloads/gradeDistribution'
    csv_directory = 'csv_data/gradeDistribution'

    # Ensure the output directory exists
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)

    for filename in os.listdir(pdf_directory):
        if filename.endswith('.pdf'):
            pdf_file_path = os.path.join(pdf_directory, filename)
            try:
                extracted_text = extract_text_from_pdf(pdf_file_path)
                data_frame = extract_course_data(extracted_text)
                df = pd.DataFrame(data_frame)

                # Save the DataFrame to a CSV file
                csv_file_path = os.path.join(csv_directory, filename.replace('.pdf', '.csv'))
                df.to_csv(csv_file_path, index=False)
                print(f"Data extracted, cleaned, and saved to {csv_file_path}")

            except Exception as e:
                print(f"Error processing {pdf_file_path}: {e}")