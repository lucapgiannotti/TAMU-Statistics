import os, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By 
import urllib.request

# GLOBALS
year_IDs = ["ctl00_plcMain_lstGradYear", "ctl00_plcMain_lstGPRYear", "ctl00_plcMain_lstCGPRYear"]
semester_IDs = ["ctl00_plcMain_lstGradTerm", "ctl00_plcMain_lstGPRTerm", "ctl00_plcMain_lstCGPRTerm"]
college_IDS = ["ctl00_plcMain_lstGradCollege", "ctl00_plcMain_lstGPRCollege", "ctl00_plcMain_lstCGPRCollege"]
download_button_IDS = ["ctl00_plcMain_btnGrade", "ctl00_plcMain_btnGPR", "ctl00_plcMain_btnCGPR"]
download_paths = ["pdf_downloads/gradeDistribution", "pdf_downloads/gpaDistribution", "pdf_downloads/cumuativeGPA"]

def initalize_driver():
    current_os = os.name    
    url = 'https://web-as.tamu.edu/gradereports/'
    
    chrome_options = Options()
    if current_os == "nt":
        driver_path = ChromeDriverManager().install()
        if driver_path:
            driver_name = os.path.basename(driver_path)
            if driver_name != "chromedriver.exe":
                driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    else:
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("window-size=1920x1080")
        driver_path = ChromeDriverManager().install()
            
    driver = webdriver.Chrome(service=ChromeService(driver_path), options=chrome_options)
    driver.get(url)

    return driver

def scrape_years_and_colleges(driver, year_ID, college_ID):
    #   Globals
    years = []
    semesters = ["SPRING", "SUMMER", "FALL"]
    colleges = []
    
    #   YEARS
    try:
        select_element = driver.find_element(By.ID, year_ID)
    
        select = Select(select_element)
    
        for option in select.options:
            year = option.text 
            years.append(year)
            print(f"Processing year: {year}")
                    
    except Exception as e:
        print(f"Error while looping through select options: {e}")

    #  COLLEGES
    try:
        select_element = driver.find_element(By.ID, college_ID)
    
        select = Select(select_element)
    
        for option in select.options:
            college = option.text 
            colleges.append(college)
            print(f"Processing college: {college}")
            
        
    except Exception as e:
        print(f"Error while looping through select options: {e}")
        
    return years, colleges, semesters


def scrape_and_download(driver):
    # GLOBALS
    year_IDs = ["ctl00_plcMain_lstGradYear", "ctl00_plcMain_lstGPRYear", "ctl00_plcMain_lstCGPRYear"]
    semester_IDs = ["ctl00_plcMain_lstGradTerm", "ctl00_plcMain_lstGPRTerm", "ctl00_plcMain_lstCGPRTerm"]
    college_IDS = ["ctl00_plcMain_lstGradCollege", "ctl00_plcMain_lstGPRCollege", "ctl00_plcMain_lstCGPRCollege"]
    download_button_IDS = ["ctl00_plcMain_btnGrade", "ctl00_plcMain_btnGPR", "ctl00_plcMain_btnCGPR"]
    download_paths = ["pdf_downloads/gradeDistribution", "pdf_downloads/gpaDistribution", "pdf_downloads/cumulativeGPA"]
    
    try:
        for year_ID, semester_ID, college_ID, download_button_ID, download_path in zip(year_IDs, semester_IDs, college_IDS, download_button_IDS, download_paths):
            # Get the years, semesters, and colleges for the current data
            years, colleges, semesters = scrape_years_and_colleges(driver, year_ID, college_ID)
            for year in years:
                print(f"Processing year: {year}")
                
                # Select the year
                year_select = Select(driver.find_element(By.ID, year_ID))
                year_select.select_by_visible_text(year)
                
                for semester in semesters:
                    print(f"  Processing semester: {semester}")
                    
                    # Select the semester
                    semester_select = Select(driver.find_element(By.ID, semester_ID))
                    semester_select.select_by_visible_text(semester)
                    for college in colleges:
                        print(f"    Processing college: {college}")
                        
                        # Select the college
                        college_select = Select(driver.find_element(By.ID, college_ID))
                        college_select.select_by_visible_text(college)
                        
                        # Download the .pdf file
                        download_button = driver.find_element(By.ID, download_button_ID)
                        driver.execute_script("arguments[0].click();", download_button)
                        if not os.path.exists(download_path):
                            os.makedirs(download_path)
                        # Check if it's a PDF
                        if driver.current_url.endswith(".pdf"):
                            pdf_url = driver.current_url
                            pdf_name = f"{year}_{semester}_{college}.pdf".replace(" ", "_")
                            pdf_path = os.path.join(download_path, pdf_name)
                            
                            # Download the PDF
                            response = urllib.request.urlopen(pdf_url)    
                            file = open("FILENAME.pdf", 'wb')
                            with open(pdf_path, 'wb') as file:
                                file.write(response.read())
                            file.close()
                            print(f"Downloaded: {pdf_name}")
                        else:
                            print("The page is not a PDF.")
                        # Navigate back to the original page
                        driver.get("https://web-as.tamu.edu/gradereports/")
                        # Reselect the year
                        year_select = Select(driver.find_element(By.ID, year_ID))
                        year_select.select_by_visible_text(year)
                        # Reselect the semester
                        semester_select = Select(driver.find_element(By.ID, semester_ID))
                        semester_select.select_by_visible_text(semester)
                        
                    
    except Exception as e:
        print(f"Error during scraping and downloading: {e}")



#   MAIN FUNCTION
def __main__():
    driver = initalize_driver()
    scrape_and_download(driver)
    
    driver.quit()
    
__main__()