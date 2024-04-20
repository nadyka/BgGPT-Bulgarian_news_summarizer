#To create the steps and code for the BgGPT News Summarizer Project, we'll break down the requirements into manageable tasks.
# This project involves web scraping, text summarization, and data presentation using Streamlit. 
# We'll also explore options for storing the articles, including SQLite and file storage
### Step 1: Retrieve the top 10 News Articles sorted by the website's editors

import requests
from bs4 import BeautifulSoup
    
def get_most_recent_articles(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='news-item') # Adjust the selector based on the website's structure\n",
        return articles[:10]
    
url = 'https://www.mediapool.bg/'
articles = get_most_recent_articles(url)
### Step 2: Summarize Articles with BgGPT\n
#"Assuming BgGPT is accessible via an API, we'll iterate over the articles and summarize them."

def summarize_article(article_text):
# Placeholder for BgGPT API call
   summary = "This is a placeholder summary for the article"
   return summary
   summaries = [summarize_article(article.text) for article in articles]
   ### Step 3: Present Articles in Streamlit GUI
#"We'll use Streamlit to create a simple GUI

import streamlit as st
import requests
from bs4 import BeautifulSoup

# Define URL and number of articles to scrape
url = "https://www.mediapool.bg/"
get_top_ten_articles = 10

# Send request and get response
response = requests.get(url)

# Check for successful response
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all article elements
    articles = soup.find_all('div', class_='article')[:get_top_ten_articles]

    # Extract headlines and article URLs
    headlines = []
    article_urls = []
    for article in articles:
        headline = article.find('h2').text.strip()
        headlines.append(headline)
        article_url = article.find('a')['href']
        article_urls.append(article_url)

    # Summarize each article
    summaries = []
    for article_url in article_urls:
        article_response = requests.get(article_url)
        if article_response.status_code == 200:
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            article_text = article_soup.find('div', class_='article-text').text.strip()

def get_top_ten_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='news-item') # Adjust the selector based on the website's structure
    return articles[:10]

def summarize_article(article_text):
    # Placeholder for BgGPT API call
    summary = "This is a placeholder summary for the article"
    return summary

def get_summaries(articles):
    summaries = [summarize_article(article.text) for article in articles]
    return summaries

def display_articles(articles, summaries):
    for i, (article, summary) in enumerate(zip(articles, summaries)):
        st.header(f"Article {i+1}")
        st.write(f"Title: {article.title}")
        st.write(f"Link: {article.link}")
        st.write("Summary:")
        st.write(summary)

url = 'https://www.mediapool.bg/'
articles = get_top_ten_articles(url)
article_summaries = get_summaries(articles)
display_articles(articles, article_summaries)
#### Step 4: Retrieve articles periodically
#We'll use APScheduler to schedule the data retrieval at specific times.and display process at regular intervals.

# Olena: Streamlit and APScheduler are both designed to run continuously. 
# Streamlit listens for changes and updates its interface accordingly, 
# while APScheduler is blocking in nature, meaning it stops further code execution until it is stopped or
# terminated. This can lead to problems where the Streamlit server does not start or work properly
# because APScheduler is blocking the stream.
# Instead of using the BlockingScheduler, we can use a non-blocking version - BackgroundScheduler. SEE streamlit_app1.py


import requests
from bs4 import BeautifulSoup
import streamlit as st
from apscheduler.schedulers.background import BackgroundScheduler

def get_most_recent_articles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    return articles[:10]

def summarize_article(article_text):
    return article_text[:100]

def display_articles(articles, summaries):
    for i, (article, summary) in enumerate(zip(articles, summaries)):
        st.header(f"Article {i+1}")
        title = article.find('h1').text if article.find('h1') else 'No title found'
        link = article.find('a')['href'] if article.find('a') else 'No link found'
        st.write(f"Title: {title}")
        st.write(f"Link: {link}")
        st.write("Summary:")
        st.write(summary)

url = 'https://www.mediapool.bg/'

def retrieve_and_display_articles():
    articles = get_most_recent_articles(url)
    summaries = [summarize_article(article.get_text()) for article in articles]
    display_articles(articles, summaries)

if __name__ == '__main__':
    st.title("Bulgarian news Article Summaries")
    scheduler = BackgroundScheduler()
    scheduler.add_job(retrieve_and_display_articles, 'interval', hours=12, start_date='2023-04-01 07:00:00')
    scheduler.start()
    st.button("Click to Refresh Articles")  # Add a button to manually trigger an update

    # Use an empty container to display articles initially and update it when button is clicked.
    article_container = st.empty()
    with article_container:
        retrieve_and_display_articles()

# Example article data (usually fetched from a web source or other API)
articles = [
    {'title': 'Article 1', 'link': 'http://example.com/article1'},
    {'title': 'Article 2', 'link': 'http://example.com/article2'}
]

# Corresponding summaries for the articles
summaries = [
    "Summary of Article 1.",
    "Summary of Article 2."
]
### Step 5: Store Articles. 
#For simplicity, we'll store articles in files.

import os
"""
    Store the articles and their summaries to text files.

    Each article and its summary is stored in a separate text file. 
    The text files are grouped into a folder. The name of the folder indicates the number of
    articles in the batch.

    Parameters:
    articles (list): The articles to be stored.
    summaries (list): The summaries of the articles.
    """
def store_articles_to_files(articles, summaries):
    batch_size = len(articles)
    folder_name = f"articles_batch_{batch_size}"
    os.makedirs(folder_name, exist_ok=True)  # Ensures that the directory exists

    for i, (article, summary) in enumerate(zip(articles, summaries)):
        file_name = f"{folder_name}/article_{i+1}.txt"
        with open(file_name, "w") as file:
            file.write(f"Title: {article['title']}\n")  # Access title from dictionary
            file.write(f"Link: {article['link']}\n")    # Access link from dictionary
            file.write("Summary:\n")
            file.write(summary)

# Now call the function with the defined articles and summaries
store_articles_to_files(articles, summaries)

### Step 6: SQLite Database\n",
#"For a more robust solution, consider using SQLite to store articles and summaries.

import sqlite3
import os

def create_articles_db():
    """ Create a SQLite database and a table for storing articles. """
    with sqlite3.connect('articles.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS articles
            (id INTEGER PRIMARY KEY, title TEXT, link TEXT, summary TEXT)
        ''')

def insert_article_to_db(title, link, summary):
    """ Insert an article into the articles table in the SQLite database. """
    with sqlite3.connect('articles.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO articles (title, link, summary) VALUES (?, ?, ?)", 
                  (title, link, summary))
        conn.commit()

def save_articles_to_files(articles, summaries, time_of_summarization, source):
    """ Save the articles and their summaries to text files. """
    folder_name = f"articles_{time_of_summarization}_{source}"
    os.makedirs(folder_name, exist_ok=True)

    for i, (article, summary) in enumerate(zip(articles, summaries)):
        article_file_path = os.path.join(folder_name, f"article_{i+1}.txt")
        summary_file_path = os.path.join(folder_name, f"summary_{i+1}.txt")
        
        with open(article_file_path, "w") as article_file:
            # Correctly accessing 'text' or any relevant content from the dictionary
            article_text = article.get('text', 'No content available')  # Safely access the 'text' key with a default
            article_file.write(f"Title: {article['title']}\n")  # Accessing title from dictionary
            article_file.write(f"Link: {article['link']}\n")    # Accessing link from dictionary
            article_file.write("Article Content:\n")
            article_file.write(article_text)
        
        with open(summary_file_path, "w") as summary_file:
            summary_file.write(summary)

# Example usage
if __name__ == '__main__':
    create_articles_db()
    # Example articles and summaries
    articles = [{'title': 'Example Title', 'link': 'http://example.com', 'text': 'Example Article Text'}]
    summaries = ['Example Summary']
    for article, summary in zip(articles, summaries):
        insert_article_to_db(article['title'], article['link'], summary)
    save_articles_to_files(articles, summaries, "2023-04-01", "mediapool")

