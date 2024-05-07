"""
This module fetches news articles from mediapool.bg for the last 7 days and saves them to a JSON file.
It includes functions to fetch news by date, extract articles from the HTML content,
and save the articles to a JSON file.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def fetch_news_by_date(date):
    """
    Fetches news articles for a specific date from mediapool.bg.
    
    Parameters:
    date (datetime.date): The date for which to fetch news articles.
    
    Returns:
    BeautifulSoup: The parsed HTML content of the page for the specified date.
    """
    base_url = "https://www.mediapool.bg/today.html"
    formatted_date = date.strftime("%Y-%m-%d")
    data = {"rdate": formatted_date}
    response = requests.post(base_url, data=data)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print(f"Failed to fetch news for date {formatted_date}. Status code: {response.status_code}")
        return None

def extract_articles_from_soup(soup):
    """
    Extracts articles from the parsed HTML content.
    
    Parameters:
    soup (BeautifulSoup): The parsed HTML content.
    
    Returns:
    list: A list of dictionaries, each representing an article with its details.
    """
    articles = []
    for article in soup.find_all('article'): # Adjust the selector based on the actual HTML structure
        title = article.find('h2').text if article.find('h2') else "No title found"
        url = article.find('a')['href'] if article.find('a') else "No URL found"
        # Assuming the full article text is within a <p> tag within the article
        full_article_text = ' '.join([p.text for p in article.find_all('p')])
        # Placeholder for publication_datetime, views, and retrieval_datetime
        # These values need to be extracted based on the actual HTML structure
        publication_datetime = "No publication datetime found"
        views = "No views found"
        retrieval_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        articles.append({
            "publication_datetime": publication_datetime,
            "title": title,
            "url": url,
            "full_article_text": full_article_text,
            "views": views,
            "retrieval_datetime": retrieval_datetime
        })
    return articles

def fetch_articles_from_last_7_days():
    """
    Fetches articles from the last 7 days and returns them in a dictionary.
    
    Returns:
    dict: A dictionary with dates as keys and lists of articles as values.
    """
    articles_by_date = {}
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        soup = fetch_news_by_date(date)
        if soup:
            articles = extract_articles_from_soup(soup)
            articles_by_date[date.strftime('%Y-%m-%d')] = articles
        else:
            print(f"No articles found for {date.strftime('%Y-%m-%d')}")
    return articles_by_date

def save_articles_to_json(articles_by_date):
    """
    Saves the fetched articles to a JSON file.
    
    Parameters:
    articles_by_date (dict): The articles to save, organized by date.
    """
    with open('fetched_last_7_days.json', 'w', encoding='utf-8') as f:
        json.dump(articles_by_date, f, ensure_ascii=False, indent=4)
    print("Articles saved to fetched_last_7_days.json")

# Example usage
articles_by_date = fetch_articles_from_last_7_days()
save_articles_to_json(articles_by_date)