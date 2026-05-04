import os
from rich import print
import requests as req
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain.tools import tool

load_dotenv()

# Loading TavilyClient
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
  """
    Perform a web search for the given query and return relevant results.

    Args:
        query (str): The search query string provided by the user.

    Returns:
        str: A string containing the summarized or most relevant search results.
    """
  query_results = tavily.search(query=query, max_results=5)
  
  final_results = [] # To store only the output content rather than whole dict
  
  for res in query_results['results']:
    final_results.append(
      f"Title: {res['title']} \nURL:{res['url']} \nSnippet: {res['content'][:300]}\n"
    )
  
  return "\n---------------------------------\n".join(final_results)

print(web_search.invoke("Tell me about the recent news about elections in West Bengal, India"))

@tool
def scrape_data(url : str) -> str:
  """
    Scrape data from the given URL and return the extracted content.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: A string containing the scraped data, such as text or relevant information
        extracted from the webpage.
    """
  pass