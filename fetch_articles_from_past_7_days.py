import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def fetch_news_by_date(date):
    # Base URL for the "today" page
    base_url = "https://www.mediapool.bg/today.html"
    
    # Format the date as YYYY-MM-DD
    formatted_date = date.strftime("%Y-%m-%d")
    
    # Prepare the data to be sent in the POST request
    data = {
        "rdate": formatted_date
    }
    
    # Send the POST request
    response = requests.post(base_url, data=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print(f"Failed to fetch news for date {formatted_date}. Status code: {response.status_code}")
        return None

def extract_articles_from_soup(soup):
    # Placeholder function: Implement this based on the structure of the HTML content
    # For demonstration, let's assume we extract titles of articles
    articles = []
    for article in soup.find_all('article'):
        title = article.find('h2').text if article.find('h2') else "No title found"
        articles.append({"title": title})
    return articles

def fetch_articles_from_last_7_days():
    # Initialize an empty dictionary to store articles by date
    articles_by_date = {}
    
    # Loop over the last 7 days
    for i in range(7):
        # Calculate the date for the current iteration
        date = datetime.now() - timedelta(days=i)
        
        # Fetch news for the current date
        soup = fetch_news_by_date(date)
        
        # Check if the soup object is not None (i.e., the request was successful)
        if soup:
            # Extract articles from the soup
            articles = extract_articles_from_soup(soup)
            articles_by_date[date.strftime('%Y-%m-%d')] = articles
        else:
            print(f"No articles found for {date.strftime('%Y-%m-%d')}")
    
    # Return the dictionary of articles by date
    return articles_by_date

# Example usage
articles_by_date = fetch_articles_from_last_7_days()

# Save the articles to a JSON file
with open('fetched_last_7_days.json', 'w', encoding='utf-8') as f:
    json.dump(articles_by_date, f, ensure_ascii=False, indent=4)

print("Articles saved to fetched_last_7_days.json")