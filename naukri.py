#Import packages
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# import scraped data
df = pd.read_csv("C:\Users\alpan\Documents\naukri_file\Naukri_streamlit_app\Naukari_data.csv")
#print(df)

#checking null value and clean the data
df.isnull().sum()
df = df.dropna(subset="Company_Name") #dropping null value
df["Review"] = df["Review"].fillna("0 reviews") #filling the missing value
df["Rating"] = df["Rating"].fillna(0)
df['Review'] = df['Review'].apply(lambda x: ''.join(filter(str.isdigit, str(x)))) #split the review column
df['Salary'] = df["Salary"].replace("","Not disclosed")

# fuction to split the experience column
def split_experience(exp):
    exp = str(exp).strip().lower()
    if 'fresher' in exp:
        return 0, 0
    digits = [int(s) for s in exp.replace('yrs', '').replace('year', '').replace('years', '').split('-') if s.strip().isdigit()]
    if len(digits) == 2:
        return digits[0], digits[1]
    elif len(digits) == 1:
        return digits[0], digits[0]
    else:
        return None, None

df[['Min_Exp', 'Max_Exp']] = df['Experience'].apply(lambda x: pd.Series(split_experience(x)))

#function for change the day to date
def convert_date_posted(x):
    x = x.strip().lower()
    today = datetime.today()
    if "today" in x or "just now" in x or "few hours" in x:
        return today.date()
    elif "days ago" in x or "day ago" in x:
        days = int(x.split()[0])
        return (today - timedelta(days=days)).date()
    return np.nan

df['Date_posted_clean'] = df['Date_posted'].apply(convert_date_posted)

df = df.drop(columns=["Experience","Date_posted"]) #dropping extra columns

#print(df.head())
#print(df.shape)



