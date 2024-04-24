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
RESULTS_DIR = 'Results'
os.makedirs(RESULTS_DIR, exist_ok=True)  # Make sure the Results directory exists

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
                save_results()  # Call to save results after fetching news
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

def save_results():
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    results_path = os.path.join(RESULTS_DIR, date_str)
    os.makedirs(results_path, exist_ok=True)  # Create a folder for today's date inside Results

    with sqlite3.connect(DATABASE_NAME) as conn:
        articles = pd.read_sql("SELECT title, link, summary FROM articles WHERE date(retrieval_date) = date('now')", conn)

    # Save to .txt file
    txt_filename = os.path.join(results_path, 'articles.txt')
    with open(txt_filename, 'w', encoding='utf-8') as file:
        for index, article in articles.iterrows():
            file.write(f"Title: {article['title']}\nLink: {article['link']}\nSummary: {article['summary']}\n\n")

    # Save to .html file
    html_filename = os.path.join(results_path, 'articles.html')
    articles.to_html(html_filename, index=False, encoding='utf-8')

def get_popular_articles(selected_date):
    # Convert selected_date from datetime.date to string in 'YYYY-MM-DD' format
    selected_date_str = selected_date.strftime('%Y-%m-%d')
    
    with sqlite3.connect(DATABASE_NAME) as conn:
        # Create a DataFrame from the SQL query
        return pd.read_sql("""
            SELECT title, link, summary, views
            FROM articles
            WHERE date(retrieval_date) = date(?)
            ORDER BY views DESC
            LIMIT 5
        """, conn, params=(selected_date_str,))


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
