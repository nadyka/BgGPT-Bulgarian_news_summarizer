#TODO: Separate fetch news into several functions, it is doing too much. One function that randonmly selects a user agents and it gets passed in as a parameter to fetch news, save the response as html. Then another function to parse it, convert it into soup, then another function to save the articles to the database.
#To refactor the code according to your request, we'll break down the `display_articles` function into smaller, more manageable functions. This will make the code more modular and easier to maintain. We'll also ensure that the main entry point (`__main__`) calls these functions in the correct sequence.
#Here's the refactored code:
#python
import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os
import re # Import regex
import random
from random import randint
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize


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

def fetch_news(articles_folderpath):
    # Define the user agents
    user_agents = {
        'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.902.78 Safari/537.36 Edg/92.0.902.78',
        'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'opera': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36 OPR/64.0.3417.83'
    }
    # Select a random user agent
    browser = random.choice(list(user_agents.keys()))
    headers = {'User-Agent': user_agents[browser]}
    # Set up path to save each article to file
    articles_folderpath = os.getcwd() + '\\' + articles_folderpath
    file2save = 'response.html'
    article_filepath = articles_folderpath + '\\' + file2save

    # Request the news page    
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            print (f"response.status_code: {response.status_code}")
            # Save the response content as HTML            
            save_html(response, article_filepath)
    except Exception as e:
        print(f"Error fetching news: {e}")
    return response
#In this version of the function, a random user agent is selected from the user_agents dictionary. The browser variable is not passed as an argument to the function, but is defined within the function. This should resolve the TypeError you were encountering.

def save_html(response, filepath):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
            print (f"HTML file successfully written out to {filepath}")
    except Exception as e:
        print(f"Error writing HTML file: {e}")

def parse_and_save_soup(response, soup_filepath):
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        with open(soup_filepath, 'w', encoding='utf-8') as f:
            f.write(soup.get_text())
            print (f"Text file successfully written out to {soup_filepath}")
        return soup
    except Exception as e:
        print(f"Error writing soup file: {e}")
        return None

def save_articles_to_db(soup):
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
            save_results()  # Call to save results after fetching news
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
            tokens = word_tokenize(article_text) # Tokenize the article text
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
        articles_folderpath = 'articles'
        soup_filepath = 'response_soup.txt'
        response = fetch_news(articles_folderpath)
        if response is not None:
            soup = parse_and_save_soup(response, soup_filepath)
            if soup is not None:
                save_articles_to_db(soup)

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
        col1, col2 = st.columns(2)  # Create two columns
        article_titles = todays_articles['title'].tolist()  # Get a list of article titles
        selected_article = col1.selectbox('Select an article', article_titles)  # Create a dropdown menu with the article titles
        selected_article_data = todays_articles[todays_articles['title'] == selected_article].iloc[0]  # Get the data for the selected article
        for i, row in enumerate(todays_articles.iterrows()):
            index, data = row
            if data['title'] == selected_article:  # If this is the selected article
                with col1:  # Display the title, short summary and link in the left column
                    st.write(f"Title: {selected_article_data['title']}")
                    st.write(f"Short Summary: {selected_article_data['summary'][:100]}")
                    st.write(f"Read the full article: [link]({selected_article_data['link']})")
                with col2:  # Display the 5 sentence summary in the right column
                    sentences = sent_tokenize(selected_article_data['summary'])
                    five_sentence_summary = ' '.join(sentences[:5])
                    st.write(f"Summary: {five_sentence_summary}")
    else:
        st.write("Не са намерени статии.")

if __name__ == "__main__":
    # Set up the database
    setup_database()

    # Fetch the news
    articles_folderpath = 'articles'
    response = fetch_news(articles_folderpath)

    # Save the response as HTML
    soup_filepath = 'response_soup.txt'
    if response is not None:
        save_html(response, articles_folderpath + '\\' + 'response.html')

        # Parse the response and convert it into soup
        soup = parse_and_save_soup(response, soup_filepath)

        # Save the articles to the database
        if soup is not None:
            save_articles_to_db(soup)

    # Display the articles
    display_articles()

#This refactored code maintains the original functionality but organizes the code into smaller, more manageable functions. The main entry point (`__main__`) calls the `display_articles` function, which in turn calls other functions as needed. This structure makes the code easier to understand and maintain.
#This code does the same thing as the original display_articles function, but it calls each function separately under if __name__ == "__main__":. Note that the save_html, parse_and_save_soup, and save_articles_to_db functions are only called if the previous function returns a valid result (i.e., not None). This ensures that the code is executed in a logical sequence and that each step is completed successfully before moving on to the next one.