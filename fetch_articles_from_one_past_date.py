import requests
from bs4 import BeautifulSoup

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

# Example usage
from datetime import datetime, timedelta

# Select a date in the past
date = datetime.now() - timedelta(days=1) # This selects yesterday's date

# Fetch news for the selected date
soup = fetch_news_by_date(date)

# Now you can parse the soup object to extract the news articles