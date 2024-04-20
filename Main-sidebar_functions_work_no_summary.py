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

def sanitize_title(title):
    return re.sub(r'[\\/*?:"<>|]', '', title)[:50]

def setup_database():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                summary TEXT,
                views INTEGER DEFAULT 0,
                retrieval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def fetch_news(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    articles = []
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('article', limit=10)
            with sqlite3.connect(DATABASE_NAME) as conn:
                conn.execute("DELETE FROM articles WHERE date(retrieval_date) = date('now')")  # Clear today's existing entries to prevent duplicates
                for item in news_items:
                    a_tag = item.find('a')
                    if a_tag:
                        title = a_tag.text.strip()
                        link = a_tag.get('href')
                        summary = "Summary of article... " + title
                        views = randint(1, 100)
                        conn.execute("INSERT INTO articles (title, link, summary, views, retrieval_date) VALUES (?, ?, ?, ?, ?)",
                                     (title, link, summary, views, datetime.datetime.now()))
                conn.commit()
    except requests.RequestException as e:
        st.error("Exception during news fetch: " + str(e))

def get_popular_articles(selected_date):
    with sqlite3.connect(DATABASE_NAME) as conn:
        return pd.read_sql("""
            SELECT title, link, summary
            FROM articles
            WHERE date(retrieval_date) = date(?)
            ORDER BY views DESC
            LIMIT 5
        """, conn, params=(selected_date,))

def display_articles(articles):
    if not articles.empty:
        articles.index = range(1, len(articles) + 1)  # Start index from 1
        for _, row in articles.iterrows():
            with st.expander(f"{row['title']}"):
                st.write(f"Накратко: {row['title']}")
                st.write(f"Прочетете повече: [link]({row['link']})")
    else:
        st.write("Не са намерени статии.")

def main():
    st.title("TOP 10 News Summary from MediaPool")
    setup_database()
    
    selected_date = st.sidebar.date_input("Select a date", datetime.date.today())
    if st.sidebar.button("Fetch News Now"):
        fetch_news(BASE_URL + "bulgaria-cat2.html")  # Assume today's news is always on page 1

    # Display today's articles
    todays_articles = pd.read_sql("SELECT title, link, summary FROM articles WHERE date(retrieval_date) = date('now')", sqlite3.connect(DATABASE_NAME))
    display_articles(todays_articles)

    # Display popular articles in the sidebar
    popular_articles = get_popular_articles(selected_date)
    if not popular_articles.empty:
        st.sidebar.write(f"Most Popular Articles for {selected_date}:")
        for index, row in popular_articles.iterrows():
            st.sidebar.write(f"{row['title']} - {row['link']}")
    else:
        st.sidebar.write("No popular articles found.")

if __name__ == "__main__":
    main()
