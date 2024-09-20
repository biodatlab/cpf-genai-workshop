# filename: search_arxiv_gpt4.py
import requests
import xml.etree.ElementTree as ET

# Search for the latest paper about GPT-4 on arXiv
search_query = 'all:gpt-4'
url = f'http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results=1&sortBy=submittedDate&sortOrder=descending'

response = requests.get(url)
if response.status_code == 200:
    root = ET.fromstring(response.content)

    # Extract title, abstract, and publication date
    paper = root.find('{http://www.w3.org/2005/Atom}entry')
    if paper is not None:
        title = paper.find('{http://www.w3.org/2005/Atom}title').text
        abstract = paper.find('{http://www.w3.org/2005/Atom}summary').text
        published = paper.find('{http://www.w3.org/2005/Atom}published').text

        print(f"Title: {title}\n")
        print(f"Abstract:\n{abstract}\n")
        print(f"Published Date: {published}\n")
    else:
        print("No paper found.")
else:
    print(f"Error fetching data from arXiv API: {response.status_code}")