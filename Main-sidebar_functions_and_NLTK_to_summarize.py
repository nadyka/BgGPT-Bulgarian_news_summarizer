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
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
nltk.download('punkt')  # Download the Punkt sentence tokenizer
nltk.download('stopwords')  # Download the stopwords

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

def fetch_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as err:
        print(f"Error: {err}")
        return None

def extract_title_and_summary(html_content, max_length=100):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find('title').text if soup.find('title') else "No title found"
    article_text = ' '.join([p.text for p in soup.find_all('p')])
    sentences = sent_tokenize(article_text)
    summary = ''

    if sentences:
        filtered_sentence = filter_stopwords(sentences[0], bulgarian_stopwords)
        summary = ' '.join(filtered_sentence)
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'

    return title, summary

def filter_stopwords(text, stopwords_set):
    words = word_tokenize(text.lower())
    return [word for word in words if word not in stopwords_set and word.isalnum()]

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
                        # Fetch the article text and summarize it
                        article_response = fetch_article(link)
                        if article_response:
                            title, summary = extract_title_and_summary(article_response)
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
                st.write(f"Накратко: {row['summary']}")
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