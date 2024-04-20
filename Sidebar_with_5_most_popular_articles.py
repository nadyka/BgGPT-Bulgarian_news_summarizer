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
    return re.sub(r'[\\/*?:"<>|]', '', title)[:50]  # Limit to 50 characters

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
            
def store_articles_in_db(articles, conn):
    cursor = conn.cursor()

    for article in articles:
        # Convert the retrieval date to a string in the format 'YYYY-MM-DD'
        retrieval_date = article["retrieval_date"].strftime('%Y-%m-%d')

        cursor.execute("""
            INSERT INTO articles (title, link, summary, retrieval_date)
            VALUES (?, ?, ?, ?)
        """, (article["title"], article["link"], article["summary"], retrieval_date))

    conn.commit()

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

def create_articles_db():
    """
    Create a SQLite database and a table for storing articles.
    """
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY, title TEXT, link TEXT, summary TEXT, retrieval_date TEXT, views INTEGER)''')
    conn.close()

# Create the articles table with a views column
conn = sqlite3.connect('articles.db')
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS articles')  # Drop the old table
c.execute('''
    CREATE TABLE articles
    (id INTEGER PRIMARY KEY, title TEXT, link TEXT, summary TEXT, retrieval_date TEXT, views INTEGER)
''')  # Create the new table
conn.close()

def get_popular_articles(selected_date):
    # Convert selected_date to a string in the format 'YYYY-MM-DD'
    selected_date = selected_date.strftime('%Y-%m-%d')
    with sqlite3.connect(DATABASE_NAME) as conn:
        return pd.read_sql("""
            SELECT title, link, summary
            FROM articles
            WHERE date(retrieval_date) = date(?)
            ORDER BY views DESC
            LIMIT 5
        """, conn, params=(selected_date,))

def generate_summary(text):
    # Split the text into words, take the first 150 words, and join them back together
    return " ".join(text.split()[:150])

def display_articles(articles):
    if not articles.empty:
        articles.index = range(1, len(articles) + 1)  # Start index from 1
        for _, row in articles.iterrows():
            with st.expander(f"{row['title']}"):
                  # Split the summary into words, take the first 150 words, and join them back together
                summary = " ".join(row['title'].split()[:150])
                st.write(f"Накратко: {summary}")
                st.write(f"Прочетете повече: [link]({row['link']})")
    else:
        st.write("Няма намерени статии.")

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
