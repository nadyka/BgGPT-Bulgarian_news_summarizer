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
nltk.download('stopwords')  # Do

# Constants
URL = "https://www.mediapool.bg/"
DATABASE_NAME = 'articles.db'
FOLDER_NAME = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
os.makedirs(FOLDER_NAME, exist_ok=True)

# Sanitize title to create safe file names
def sanitize_title(title):
    # Remove invalid file name characters
    safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
    return safe_title[:50]  # Limit the length of file name if necessary

# Setup Database
def setup_database():
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                summary TEXT,
                views INTEGER,
                retrieval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

# Fetch and Summarize Articles
def fetch_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    articles = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('article', limit=10)  # Limit to the first 10 articles

        for item in news_items:
            a_tag = item.find('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                summary = "Накратко... " + title  # Placeholder for actual summarization
                sanitized_title = sanitize_title(title)
                articles.append({"title": title, "link": link, "summary": summary})
                
                # Save to SQLite DB
                with sqlite3.connect(DATABASE_NAME) as conn:
                    for item in news_items:
                        a_tag = item.find('a')
                    if a_tag:
                        title = a_tag.text.strip()
                        link = a_tag.get('href')
                        summary = "Summary placeholder"
                        views = randint(1, 100)
                        print(f"Views for {title}: {views}")
                    conn.execute("INSERT INTO articles (title, link, summary) VALUES (?, ?, ?)",
                                 (title, link, summary))
                
                # Save to files
                with open(f"{FOLDER_NAME}/{sanitized_title}.txt", 'w', encoding='utf-8') as file:
                    file.write(f"Title: {title}\nLink: {link}\nSummary: {summary}\n")
        
    except requests.RequestException as e:
        st.error(f"Failed to retrieve articles: {str(e)}")

    return articles

#Summarize with NLTK function as an alternative to Gensim which rendered an issue with SciPy
def summarize(text):
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text)

    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1

    sentences = sent_tokenize(text)
    sentenceValue = dict()

    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]

    average = int(sumValues / len(sentenceValue))

    summary = ''
    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence
    return summary


# Display Articles Function
def display_articles(articles):
    if not articles:  # Check if the list is empty
        st.write("Не са намерени статии.")
    else:
        # Convert articles to a DataFrame
        articles = pd.DataFrame(articles)
        if articles.empty:  # Check if the DataFrame is empty
            st.write("The DataFrame is empty.")
        else:
            articles.index = range(1, len(articles) + 1)  # Start index from 1
            print(articles)  # Print the DataFrame
            for _, row in articles.iterrows():
                with st.expander(f"{row['title']}"):
                    # Generate a summary of the article
                    summary = summarize(row['summary'])
                    st.write(f"Накратко: {summary}")
                    st.write(f"Прочетете повече: [link]({row['link']})")
                    
# Retrieve and Display Function for APScheduler
# Retrieve and Display Function for APScheduler
def retrieve_and_display_articles():
    articles = fetch_news(URL)
    if articles:  # Check if the list is not empty
        display_articles(articles)

# Streamlit App Layout
def main():
    st.title("Scheduled News Summary from MediaPool")
    setup_database()

    # Scheduling fetches
    scheduler = BackgroundScheduler()
    scheduler.add_job(retrieve_and_display_articles, 'interval', hours=12, next_run_time=datetime.datetime.now())
    scheduler.start()

    if st.button("Fetch News Now"):
        retrieve_and_display_articles()

if __name__ == "__main__":
    main()
