# Import packages
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

job_details = {
    'Company_Name':[],
    'Job_Role':[],
    'Experience':[],
    'Location':[],
    'Salary':[],
    'Date_posted':[],
    'Review':[],
    'Rating':[]
}

def scroll_page():
    last_height = driver.execute_script("return document.body.ScrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Scrap web data
for i in range(1,200):
    driver.get(f"https://www.naukri.com/jobs-in-india-{i}")
    time.sleep(5)
    scroll_page()
    # time.sleep(5)
    

    # job_elements = driver.find_elements(By.CLASS_NAME, "cust-job-tuple")
    job_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'cust-job-tuple')]")


    for job in job_elements:
        try:
            job_details["Company_Name"].append(job.find_element(By.XPATH, './/a[contains(@class, "comp-name")]').text)
        except:
            job_details['Company_Name'].append(None)
            
        try:
            job_details["Job_Role"].append(job.find_element(By.XPATH, './/a[contains(@class, "title")]').text)
        except:
            job_details['Job_Role'].append(None)
            
        try:
            job_details["Experience"].append(job.find_element(By.XPATH, './/span[contains(@class, "exp-wrap")]/span/span').text.strip())
        except:
            job_details['Experience'].append(None)
            
        try:
            job_details["Location"].append(job.find_element(By.XPATH, ".//span[contains(@class, 'locWdth')]").text)
        except:
            job_details['Location'].append(None)
            
        try:
            job_details["Salary"].append(job.find_element(By.XPATH, ".//span[contains(@class, 'sal-wrap')]/span/span").text.strip())
        except:
            job_details['Salary'].append(None)
        try:
            date_post_element = job.find_element(By.XPATH, ".//span[contains(@class, 'job-post-day')]").text
            job_details["Date_posted"].append(date_post_element.strip() if date_post_element else None)
        except:
             job_details['Date_posted'].append(None)
             
        try:
            job_details['Review'].append(job.find_element(By.XPATH, './/a[contains(@class, "review")]').text)
        except:
            job_details['Review'].append(None)
            
        try:
            job_details["Rating"].append(job.find_element(By.XPATH, './/a[contains(@class, "rating")]').text)
        except: 
            job_details["Rating"].append(None)
driver.quit()

df=pd.DataFrame(job_details)
print(df.head())

df
        