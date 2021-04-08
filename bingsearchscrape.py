import requests
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import bs4
import re
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse,parse_qs

url_search = "https://www.bing.com/search?q=%(query)s&count=%(count)s"
def search(query, count=10):
    # tittle = {}
    query = quote_plus(query)

    html=get_page(url_search % vars())
    soup = BeautifulSoup(html,'html.parser')
    anchors = soup.find(id='b_results').findAll('a', href=True)
    links = [filter_result(a[ 'href']) for a in anchors if filter_result(a[ 'href'])]
    return links
    # for x in links:
    #     print(get_title(x))
    #     print(x)

# def get_title(link):
#     # soup = BeautifulSoup(urlopen(link, 'lxml'))
#     html = get_page(link)
#     soup = BeautifulSoup(html, 'html.parser')
#     title_1 = soup.title.get_text()
#     return title_1

def get_page(url):
    request = Request(url)
    #request.add_header('User-Agent', USER_AGENT)
    response = urlopen(request)
    html = response.read()
    response.close()
    return html

def filter_result(link):
    # try:
        if link.startswith('/search?'):
            o = urlparse(link, 'http')
            link = parse_qs(o.query)['q'][0]
        o = urlparse(link, 'http')
        if o.netloc and 'bing' not in o.netloc:
            return link
    # except Exception:
        # pass

query = "harshad mehta"
search(query, count=10)
