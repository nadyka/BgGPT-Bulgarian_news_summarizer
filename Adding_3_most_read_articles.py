import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os
import re  # Import regex
from random import randint

# Constants
BASE_URL = "https://www.mediapool.bg/"
DATABASE_NAME = 'articles.db'
FOLDER_NAME = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
os.makedirs(FOLDER_NAME, exist_ok=True)

# Sanitize title to create safe file names
def sanitize_title(title):
    # Remove invalid file name characters
    safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
    return safe_title[:50]  # Limit the length of file name if necessary

def setup_database():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        # Drop the existing table if it exists and recreate it
        cursor.execute("DROP TABLE IF EXISTS articles")
        cursor.execute('''
            CREATE TABLE articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                summary TEXT,
                retrieval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

        # Optionally, add the 'retrieval_date' column if it does not exist (useful if schema was initially set without it)
        cursor.execute("PRAGMA table_info(articles)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'retrieval_date' not in columns:
            cursor.execute('ALTER TABLE articles ADD COLUMN retrieval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            conn.commit()

# Fetch and Summarize Articles
def fetch_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        with sqlite3.connect(DATABASE_NAME) as conn:
            news_items = soup.find_all('article', limit=10)
            for item in news_items:
                a_tag = item.find('a')
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    link = a_tag['href']
                    summary = "Summary of article... " + title
                    # Insert without specifying retrieval_date
                    conn.execute("INSERT INTO articles (title, link, summary) VALUES (?, ?, ?)",
                                 (title, link, summary))
            conn.commit()
    except requests.RequestException as e:
        st.error(f"Failed to retrieve articles: {str(e)}")

# Retrieve recent popular articles
def get_recent_articles():
    with sqlite3.connect(DATABASE_NAME) as conn:
        recent_articles = pd.read_sql("""
            SELECT title, link, summary
            FROM articles
            WHERE retrieval_date > datetime('now', '-3 hours')
            ORDER BY retrieval_date DESC
            LIMIT 5
        """, conn)
    return recent_articles

DATABASE_NAME = 'articles.db'  # Replace with your actual database name

def retrieve_and_display_articles():
    with sqlite3.connect(DATABASE_NAME) as conn:
        articles = pd.read_sql("""
            SELECT title, link, summary
            FROM articles
            WHERE retrieval_date > datetime('now', '-3 hours')
            ORDER BY retrieval_date DESC
            LIMIT 5
        """, conn)

    if not articles.empty:  # Check if the DataFrame is empty
        for _, row in articles.iterrows():
            with st.expander(f"{row['title']}"):
                st.write(f"Summary: {row['summary']}")
                st.write(f"Read more: [link]({row['link']})")
    else:
        st.write("No recent articles found.")


# Streamlit App Layout
def main():
    st.title("Scheduled News Summary from MediaPool")
    setup_database()

   # Sidebar for popular articles
    st.sidebar.title("Most Popular Articles (Last 3 Hours)")
    popular_articles = get_recent_articles()
    if not popular_articles.empty:  # Check if the DataFrame is empty
        for index, row in popular_articles.iterrows():
            st.sidebar.header(row['Title'])
            st.sidebar.write(row['Summary'])
            st.sidebar.write(f"Прочетете повече: [link]({row['Link']})")
    else:
        st.sidebar.write("No popular articles found.")

    # Scheduling fetches
    scheduler = BackgroundScheduler()
    scheduler.add_job(retrieve_and_display_articles, 'interval', hours=12, next_run_time=datetime.datetime.now())
    scheduler.start()
    
    # Manual trigger button with a unique key
    if st.button("Fetch News Now"):
        articles = get_recent_articles()  # Or however you get your articles
        if not articles.empty:  # Check if the DataFrame is empty
            for _, row in articles.iterrows():  # Use articles instead of df
                with st.expander(f"{row['Title']}"):
                    st.write(f"Накратко: {row['Title']}")
                    st.write(f"Прочетете повече: [link]({row['Link']})")
    else:
        st.write("Няма намерени статии.")

    retrieve_and_display_articles()

if __name__ == "__main__":
    main()