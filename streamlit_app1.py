import requests
from bs4 import BeautifulSoup
import streamlit as st

# Constants
URL = "https://www.mediapool.bg/"  # Assuming this is where you fetch news from

# Function to fetch top news articles
def fetch_news(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Assuming articles are in a div with class "correct-class"
        news_items = soup.find_all('div', class_='correct-class', limit=10)
        
        articles = []
        for item in news_items:
            title = item.find('a').get_text(strip=True) if item.find('a') else 'No title found'
            link = item.find('a')['href'] if item.find('a') else '#'
            articles.append((link, title))
        
        return articles
    except requests.RequestException as e:
        st.error(f"Failed to retrieve articles: {str(e)}")
        return []

def display_articles(articles):
    for link, title in articles:
        st.header(title)
        st.write(f"Read more at: {link}")

def main():
    st.title("News Summary from MediaPool")
    articles = fetch_news("https://www.mediapool.bg/")
    if articles:
        display_articles(articles)
    else:
        st.write("No articles found or unable to fetch articles.")

if __name__ == "__main__":
    main()
    
    
# Function to display articles in Streamlit
def display_articles(articles):
    for url, title in articles:
        st.header(title)
        st.write(f"Read more at: {url}")

# Streamlit App Layout
def main():
    st.title("News Summary from MediaPool")
    fetched_articles = fetch_news(URL)

    if fetched_articles:
        display_articles(fetched_articles)
    else:
        st.write("No articles found or unable to fetch articles.")

if __name__ == "__main__":
    main()

