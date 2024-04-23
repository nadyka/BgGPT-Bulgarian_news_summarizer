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

#Define the user agents
user_agents = {
        'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.902.78 Safari/537.36 Edg/92.0.902.78',
        'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'opera': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36 OPR/64.0.3417.83'
    }

def fetch_news(articles_folderpath, browser):
    headers = {'User-Agent': user_agents.get(browser, 'Mozilla/5.0')}
    articles_folderpath = os.getcwd() + '\\' + articles_folderpath
    #base_news_folder = r'C:\Users\Nadia Stoyanova\Documents\GitHub\BgGPT-Bulgarian_news_summarizer\articles'
    file2save = 'response.html'
    article_filepath = articles_folderpath + '\\' + file2save
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            print (f"response.status_code: {response.status_code}")
            # Save the response content as HTML            
            save_html(response, article_filepath)
            #with open(article_filepath, 'w', encoding='utf-8') as f:
    except Exception as e:
        print(f"Error fetching news: {e}")        
    response = fetch_news(articles_folderpath)
    if response is not None:
        soup = parse_and_save_soup(response, soup_filepath)
        if soup is not None:
            save_articles(soup)
    return response        
        #f.write(response.text)
        #print (f"#response.html successfully written out")
        #response.html successfully written out            
def save_html(response, filepath):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
            print (f"#response.html successfully written out")
    except Exception as e:
        print(f"Error writing HTML file: {e}")

    #TODO print return value is successful - fetch and save news response was successful


def parse_and_save_soup(response, soup_filepath):
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        with open(soup_filepath, 'w', encoding='utf-8') as f:
            f.write(soup.get_text())
            print (f"soup content written out from soup.get_text(): {soup.get_text()}")
        return soup
    except Exception as e:
        print(f"Error writing soup file: {e}")
        return None

def save_articles(soup):
    try:
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
        st.error(f"Exception during raw data news_fetch_and_save article_file: {e}")

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
            tokens = word_tokenize(article_text)  # Tokenize the article text
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
        articles_folderpath = 'articles'
        soup_filepath = 'response_soup.txt'
        response = fetch_news(articles_folderpath)
        if response is not None:
            soup = parse_and_save_soup(response, soup_filepath)
            if soup is not None:
                save_articles(soup)

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
                st.write(f"Накратко: {row['summary']}")
                st.write(f"Прочетете цялата статия: [link]({row['link']})")
    else:
        st.write("Не са намерени статии.")

if __name__ == "__main__":
    display_articles()
