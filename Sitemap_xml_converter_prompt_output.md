To execute the prompt in the file `sitemap_xml_to_dataframe_converter.prompt.txt`, we'll follow the instructions step by step. The prompt outlines two main tasks:

1. Extract all URL records from a sitemap file in XML format and return a JSON object of URL records.
2. Convert the JSON object to a Python dictionary and then to a pandas DataFrame named `article_url_records`.

Let's start with the first task:

### Task 1: Extract URL Records from XML Sitemap

We'll use Python's `xml.etree.ElementTree` to parse the XML sitemap and extract the URL records.

```python
import xml.etree.ElementTree as ET
import json

def extract_url_records(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    namespaces = {'news': 'http://www.google.com/schemas/sitemap-news/0.9'}
    url_records = []

    for url in root.findall('url'):
        loc = url.find('loc').text
        news_info = url.find('news:news', namespaces)
        if news_info is not None:
            title = news_info.find('news:title', namespaces).text
            publication_date = news_info.find('news:publication_date', namespaces).text
            publication = news_info.find('news:publication', namespaces)
            source_name = publication.find('news:name', namespaces).text
            source_language = publication.find('news:language', namespaces).text

            url_records.append({
                'news_article_url': loc,
                'news_article_title': title,
                'news_publication_date': publication_date,
                'news_source_name': source_name,
                'news_source_language': source_language
            })

    return json.dumps(url_records)

# Example usage
json_url_records = extract_url_records('sitemap-today.xml')
print(json_url_records)
```

### Task 2: Convert JSON to DataFrame

Next, we'll convert the JSON object to a pandas DataFrame.

```python
import pandas as pd
import json

def json_to_dataframe(json_data):
    data = json.loads(json_data)
    df = pd.DataFrame(data)
    return df

# Example usage
df = json_to_dataframe(json_url_records)
print(df)
```

### Additional Task: Count the Length of Each URL

Finally, we'll add a function to count the length of each URL and add it to the DataFrame.

```python
def add_url_length(df):
    df['url_length'] = df['news_article_url'].apply(len)
    return df

# Example usage
df_with_length = add_url_length(df)
print(df_with_length)
```

This code completes the tasks outlined in the prompt. It extracts URL records from an XML sitemap, converts the records to a JSON object, then to a pandas DataFrame, and finally adds a column for the length of each URL.