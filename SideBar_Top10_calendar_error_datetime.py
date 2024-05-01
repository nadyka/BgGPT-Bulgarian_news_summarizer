import streamlit as st
import pandas as pd
import sqlite3
import datetime
from datetime import datetime, date
import os

# Constants
DATABASE_NAME = 'articles.db'
RESULTS_DIR = 'Results_news'

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

def get_popular_articles(specific_date):
    with sqlite3.connect(DATABASE_NAME) as conn:
        date_str = specific_date.strftime('%Y-%m-%d')  # Format specific_date as a string
        query = """
            SELECT id, title, link, summary, views
            FROM articles
            WHERE date(retrieval_date) = date(?)
            ORDER BY views DESC
            LIMIT 10
        """
        return pd.read_sql(query, conn, params=(date_str,))
        
def display_previous_news(selected_date):
    previous_news = get_popular_articles(selected_date)
    if not previous_news.empty:
        st.subheader(f"Previous News for {selected_date}")
        for index, row in previous_news.iterrows():
            st.markdown(f"**{row['title']}**")
            st.write(f"Summary: {row['summary']}")
            st.markdown(f"[Read more]({row['link']})", unsafe_allow_html=True)
    else:
        st.write("No previous news found for this date.")

from datetime import datetime, date

def display_articles():
    st.title("News Articles Dashboard")
    
    # Sidebar for selecting a date and displaying previous news
    st.sidebar.title("Explore Previous News")
    selected_date = st.sidebar.date_input("Select a date", date.today())
    if st.sidebar.button("Show Previous News"):
        display_previous_news(selected_date)

    # Main area for displaying top news summary
    specific_date = datetime.now()  # Set to today's date or any specific date
    st.header(f"TOP 10 News Summary from MediaPool {specific_date}")
    popular_articles = get_popular_articles(specific_date)
    if not popular_articles.empty:
        for index, row in popular_articles.iterrows():
            st.subheader(row['title'])
            st.write(f"Summary: {row['summary']}")
            st.markdown(f"[Read more]({row['link']})", unsafe_allow_html=True)
    else:
        st.write("No articles found for this date.")

if __name__ == "__main__":
    display_articles()
