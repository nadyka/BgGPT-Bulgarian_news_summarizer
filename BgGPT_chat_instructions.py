# Import necessary libraries
import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# Set up your OpenAI API key
openai.api_key = "your_openai_api_key"

    
def fetch_webpage(url: str) -> str:
    """Fetches the content of a webpage."""
    response = requests.get(url)
    return response.text

def get_top_ten_news_articles(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='news-item') # Adjust the selector based on the website's structure\n",
        return articles[:10]
url = 'https://www.mediapool.bg/'
articles = get_top_ten_news_articles(url)
 
# def summarize_article(article_text):
# Placeholder for BgGPT API call
#    summary = "This is a placeholder summary for the article"
#    return summary
#    summaries = [summarize_article(article.text) for article in articles]

def summarize_top_ten_news_articles(content: str) -> str:
    """Summarizes the top 10 articles as ranked by the news site editors by using BgGPT."""
    prompt = f"Summarize the top ten news articles:\n\n{content}"
    response = openai.Completion.create(
        engine="bg-gpt",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def scrape_news_articles(url: str) -> list[tuple[str, str]]:
    """Scrapes the top ten news articles from the given URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Replace the following selectors with the appropriate ones for the news website you want to scrape
    headlines = soup.select(".headline-class")
    links = soup.select(".link-class")

    articles = []
    for i in range(min(len(headlines), len(links))):
        headline = headlines[i].text.strip()
        link = links[i].get("href")

        articles.append((headline, link))

    return articles

def display_news_articles():
    """Displays the top news articles."""
    url = "https://www.mediapool.bg"  # Replace with the actual news website URL
    articles = scrape_news_articles(url)

    st.set_page_title("MediaPool News Summary App")
    st.header("Top Ten News Articles")

    for i, (headline, link) in enumerate(articles):
        button = f"{i+1}. {headline}"

        with st.expander(button):
            content = fetch_webpage(link)
            summary = summarize_article(content)

            st.markdown(summary)

if __name__ == "__main__":
    display_news_articles()

#In this version, I have used more descriptive variable names, added docstrings to each function to explain their purpose, and replaced the example news website URL with a placeholder ("https://www.mediapool.bg"). You should replace this placeholder with the actual news website URL you want to scrape.