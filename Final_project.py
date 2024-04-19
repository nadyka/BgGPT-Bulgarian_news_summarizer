import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
import re  # Import regex
from random import randint
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk

# Download necessary NLTK resources
nltk.download('punkt')

# Custom Bulgarian stopwords list
bulgarian_stopwords = set([
    "и", "в", "на", "с", "за", "не"
])

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

def fetch_news():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('article', limit=10)
            with sqlite3.connect(DATABASE_NAME) as conn:
                conn.execute("DELETE FROM articles WHERE date(retrieval_date) = date('now')")
                for item in news_items:
                    a_tag = item.find('a')
                    if a_tag and a_tag['href']:
                        title, summary = extract_title_and_summary(a_tag['href'])
                        views = randint(1, 100)
                        conn.execute("INSERT INTO articles (title, link, summary, views, retrieval_date) VALUES (?, ?, ?, ?, ?)",
                                     (title, a_tag['href'], summary, views, datetime.datetime.now()))
                conn.commit()
    except requests.RequestException as e:
        st.error(f"Exception during news fetch: {e}")

def extract_title_and_summary(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').text if soup.find('title') else "No title found"
            article_text = ' '.join([p.text for p in soup.find_all('p')])
            sentences = sent_tokenize(article_text)
            summary = sentences[0][:100] if sentences else "No summary available"
            return title, summary
    except Exception as e:
        return "Failed to extract", str(e)

def get_popular_articles(selected_date):
    with sqlite3.connect(DATABASE_NAME) as conn:
        return pd.read_sql("""
            SELECT title, link, summary
            FROM articles
            WHERE date(retrieval_date) = date(?)
            ORDER BY views DESC
            LIMIT 5
        """, conn, params=(selected_date,))

def display_articles():
    st.title("TOP 10 News Summary from MediaPool")
    setup_database()

    selected_date = st.sidebar.date_input("Select a date", datetime.date.today())
    if st.sidebar.button("Fetch News Now"):
        fetch_news()

    popular_articles = get_popular_articles(selected_date)
    if not popular_articles.empty:
        st.sidebar.write(f"Most Popular Articles for {selected_date}:")
        for index, row in popular_articles.iterrows():
            st.sidebar.write(f"{row['title']} - {row['link']}")

    # Display today's articles
    with sqlite3.connect(DATABASE_NAME) as conn:
        todays_articles = pd.read_sql("SELECT title, link, summary FROM articles WHERE date(retrieval_date) = date('now')", conn)
    if not todays_articles.empty:
        todays_articles.index = range(1, len(todays_articles) + 1)
        for _, row in todays_articles.iterrows():
            with st.expander(f"{row['title']}"):
                st.write(f"Summary: {row['summary']}")
                st.write(f"Read more at: [link]({row['link']})")
    else:
        st.write("No articles found.")

if __name__ == "__main__":
    display_articles()
