import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk

# Ensure that NLTK resources are downloaded
nltk.download('punkt')

# Custom Bulgarian stopwords list
bulgarian_stopwords = set([
    # Add your predefined stopwords here
    "и", "в", "на", "с", "за", "не"
])

def fetch_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as err:
        print(f"Error: {err}")
        return None

def extract_title_and_summary(html_content, max_length=100):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find('title').text if soup.find('title') else "No title found"
    article_text = ' '.join([p.text for p in soup.find_all('p')])
    sentences = sent_tokenize(article_text)
    summary = ''

    if sentences:
        filtered_sentence = filter_stopwords(sentences[0], bulgarian_stopwords)
        summary = ' '.join(filtered_sentence)
        if len(summary) > max_length:
            summary = summary[:max_length] + '...'

    return title, summary

def filter_stopwords(text, stopwords_set):
    words = word_tokenize(text.lower())
    return [word for word in words if word not in stopwords_set and word.isalnum()]

# Example usage
url = 'https://www.mediapool.bg/'
html_content = fetch_article(url)
if html_content:
    title, summary = extract_title_and_summary(html_content)
    print(f"Title: {title}")
    print(f"Summary: {summary}")
else:
    print("Failed to fetch the article.")
