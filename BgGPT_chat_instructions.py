import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os
import sqlite3

# Set up your OpenAI API key
openai.api_key = "your_openai_api_key"

def fetch_webpage(url: str) -> str:
    """Fetches the content of a webpage."""
    response = requests.get(url)
    return response.text

def summarize_article(content: str) -> str:
    """Summarizes the given article using BgGPT."""
    prompt = f"Summarize the following article:\n\n{content}"
    response = openai.Completion.create(
        engine="bg-gpt",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def scrape_news_articles(url: str) -> list[dict]:
    """Scrapes news articles from the given URL and returns their summaries."""
    articles = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = soup.select(".entry-title > a")
    links = soup.select(".entry-link")

    for i in range(min(len(headlines), len(links))):
        headline = headlines[i].text.strip()
        link = links[i].get("href")

        articles.append({"headline": headline, "link": link})

    return articles

def store_summaries_in_files(articles: list[dict], output_dir: str):
    """Stores the summaries and their hyperlinks in text and HTML files in the specified directory."""
    for article in articles:
        with open(f"{output_dir}/{article['headline']}.txt", "w") as f:
            f.write(article["summary"])

        with open(f"{output_dir}/{article['headline']}.html", "w") as f:
            f.write(article["summary"])
            f.write(f"<a href='{article['link']}' target='_blank'>Read full article</a>")

def store_summaries_in_db(articles: list[dict], conn: sqlite3.Connection):
    """Stores the summaries and their hyperlinks in an SQLite database."""
    cursor = conn.cursor()

    # Create a new table with the desired structure
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL UNIQUE,
            summary TEXT NOT NULL,
            link TEXT NOT NULL
        );
    """)

    # Copy the data from the old table to the new table
    cursor.execute("""
        INSERT INTO new_articles (summary, link)
        SELECT summary, link FROM articles;
    """)

    # Delete the old table
    cursor.execute("""
        DROP TABLE articles;
    """)

    # Rename the new table to the old table's name
    cursor.execute("""
        ALTER TABLE new_articles RENAME TO articles;
    """)

    # Insert the new data into the articles table
    cursor.executemany("""
        INSERT INTO articles (headline, summary, link) VALUES (?, ?, ?);
    """, [(article["headline"], article["summary"], article["link"]) for article in articles])

    conn.commit()

def display_and_store_news_articles():
    """Displays the top news articles and stores them in text and HTML files, as well as an SQLite database."""
    url = "https://mediapool.bg"  # Replace with the actual news website URL
    articles = scrape_news_articles(url)

    output_dir = "articles"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, article in enumerate(articles[:10], start=1):
        # Ensure that the article has a 'headline' key and the value of the 'headline' key is not None
        if "headline" in article and article["headline"] is not None:
            button = f"{i}. {article['headline']}"

            with st.expander(button):
                summary = article["summary"]
                # The rest of your code goes here

# Call the display_and_store_news_articles function
display_and_store_news_articles()

        
store_summaries_in_files(articles, output_dir)

conn = sqlite3.connect("articles.db", timeout=10)
store_summaries_in_db(articles, conn)
conn.close()

st.set_page_title("MediaPool.bg Top News Summaries")
st.header("Top News Summaries")

if __name__ == "__main__":
    display_and_store_news_articles()