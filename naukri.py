#Import packages
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import re

# import scraped data
df = pd.read_csv("Naukari_data.csv")
#print(df)

#checking null value and clean the data
df.isnull().sum()
df = df.dropna(subset="Company_Name") #dropping null value
df["Review"] = df["Review"].fillna("0 reviews") #filling the missing value
df["Rating"] = df["Rating"].fillna(0)
df['Review'] = df['Review'].apply(lambda x: ''.join(filter(str.isdigit, str(x)))) #split the review column
df['Salary'] = df["Salary"].replace("","Not disclosed")


def convert_reviews(val):
    if isinstance(val, str):
        val = val.lower().replace("reviews", "").strip()
        if 'k' in val:
            return float(val.replace('k', '')) * 1000
        else:
            return float(val)
    return 0

df['Review'] = df['Review'].apply(convert_reviews)


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


# making dashboard
st.set_page_config(page_title="Naukri Job Insights", layout="wide")
st.title("📊 Naukri Job Data Dashboard")

st.sidebar.header("🔍 Filter Jobs")
min_exp = int(df['Min_Exp'].min())
max_exp = int(df['Max_Exp'].max())
exp_range = st.sidebar.slider("Experience Range (Years)", min_exp, max_exp, (min_exp, max_exp))

job_titles = st.sidebar.multiselect("Select Job Titles", options=df['Job_Role'].unique(), default=None)
filtered_df = df[(df['Min_Exp'] >= exp_range[0]) & (df['Max_Exp'] <= exp_range[1])]
if job_titles:
    filtered_df = sorted(filtered_df[filtered_df['Job_Role'].isin(job_titles)])

total_jobs = df.shape[0]
avg_min_exp =df['Min_Exp'].mean()
avg_reviews =df['Review'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("📌 Total Jobs", total_jobs)
col2.metric("📊 Avg Min Experience", f"{avg_min_exp:.1f} yrs")
col3.metric("⭐ Avg Reviews", f"{avg_reviews:.1f}")

st.subheader("💼 Top 10 Job Titles")
top_jobs = df['Job_Role'].value_counts().head(10).reset_index()
top_jobs.columns = ['Job Role', 'Count']
fig1 = px.bar(top_jobs, x='Job Role', y='Count', color='Count', text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Experience vs Reviews")
fig2 = px.scatter(df, x='Min_Exp', y='Review', size='Review', color='Job_Role', hover_name='Job_Role')
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Jobs Over Time (Matplotlib)")

# df['Date_posted'] = pd.to_datetime(df['Date_posted'], errors='coerce')

# Drop missing dates and group by date
df['Date_posted_clean'] = pd.to_datetime(df['Date_posted_clean'], errors='coerce')

job_trend = df.dropna(subset=['Date_posted_clean']).groupby(df['Date_posted_clean'].dt.date).size()

fig, ax = plt.subplots()
ax.plot(job_trend.index, job_trend.values, marker='o')
ax.set_title("Jobs Posted Over Time")
ax.set_xlabel("Date")
ax.set_ylabel("Number of Jobs")
plt.xticks(rotation=45)

st.pyplot(fig)

# Example cleaning function (assuming "Salary" column exists)
def extract_salary_range(sal):
    if pd.isna(sal):
        return pd.Series([None, None])
    # Remove currency symbols and text
    sal = sal.lower().replace("lpa", "").replace("lacs", "").replace("₹", "").replace(",", "").strip()
    match = re.findall(r'(\d+\.?\d*)', sal)
    if len(match) == 2:
        return pd.Series([float(match[0]), float(match[1])])
    elif len(match) == 1:
        return pd.Series([float(match[0]), float(match[0])])
    else:
        return pd.Series([None, None])

df[['Min_Salary', 'Max_Salary']] = df['Salary'].apply(extract_salary_range)


df['Avg_Salary'] = (df['Min_Salary'] + df['Max_Salary']) / 2
# st.subheader("📦 Salary Distribution by Job Title")

# top_titles = df['Job_Role'].value_counts().head(5).index
# subset = df[df['Job_Role'].isin(top_titles)]

# fig, ax = plt.subplots(figsize=(10, 5))
# sns.boxplot(data=subset, x='Job_Role', y='Avg_Salary', ax=ax)
# ax.set_title('Salary Distribution by Job Title')
# plt.xticks(rotation=45)

# st.pyplot(fig)

st.subheader("💰 Average Salary by Job Title")

avg_salary = df.groupby('Job_Role')['Avg_Salary'].mean().sort_values(ascending=False).head(10)

fig2, ax2 = plt.subplots(figsize=(10, 5))
avg_salary.plot(kind='bar', color='green', ax=ax2)
ax2.set_ylabel("Average Salary (LPA)")
ax2.set_title("Top 10 Job Titles by Avg Salary")
plt.xticks(rotation=45)

st.pyplot(fig2)


st.subheader('Location-wise Job Distribution')

# Drop missing locations
location_data = df.dropna(subset=['Location'])

# Get Top 10 Locations
top_locations = location_data['Location'].value_counts().head(10)

# Plot
plt.figure(figsize=(12, 6))
sns.barplot(x=top_locations.values, y=top_locations.index, palette="viridis")
plt.xlabel('Number of Jobs')
plt.ylabel('Location')
plt.title('Top 10 Locations by Job Count')
st.pyplot(plt)
