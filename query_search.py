from collections import namedtuple
import json
import pprint
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
import requests

from searchscrape import search as gsearch
from bingsearchscrape import search as bingsearch



class ExcelProcessing:
    
    
    def __init__(self, file_name:str) -> None:
        self.file_name = file_name
        self.xls = pd.ExcelFile(file_name)

    
    def combination_keywords_search(self, content:str) -> list:
        df = pd.read_excel(self.xls, 'Combination Keywords')
        combination_keywords = df['Keywords'].tolist()

        combination_words_hit = [keyword for keyword in combination_keywords if keyword in content]

        return combination_words_hit


    def mandatory_keywords_search(self, content:str) -> list:
        df = pd.read_excel(self.xls, 'Mandatory Keywords')
        mandatory_keywords = df['Required'].tolist()

        mandatory_words_hit = [word for word in mandatory_keywords if word in content]

        return mandatory_words_hit


    def url_list(self, results:list) -> list:
        df1 = pd.read_excel(self.xls, 'Media Sites')
        media_sites = df1['Name of Publication'].tolist()        
        url_list1 = [x for x in results for search in media_sites if search in x]

        return url_list1



class QueryProcessing:

    
    def __init__(self, query:str, search_engine:str, excel_file_name:str) -> None:
        self.query = query
        self.search_engine = search_engine

        self.excel_reader = ExcelProcessing(excel_file_name)
        self.search_results = {}
        
        

    
    def search(self) -> dict:

        if self.search_engine == 'www.google.com':
                self.search_results['URL'] = self.search_engine
                self.search_results['SearchText'] = self.query
                results = [result for result in gsearch(self.query,"com", num=30, stop=30, pause=2)]
                self.__search_return(results)

        elif self.search_engine == 'www.google.co.in':
                self.search_results['URL'] = self.search_engine
                self.search_results['SearchText'] = self.query
                results = [result for result in gsearch(self.query,"co.in", num=30, stop=30, pause=2)]
                self.__search_return(results)

        elif self.search_engine == 'www.bing.com':
            self.search_results['URL'] = self.search_engine
            self.search_results['SearchText'] = self.query
            results = [result for result in bingsearch(self.query, count=30)]
            self.__search_return(results)
        
        return self.search_results


    def __search_return(self, results:list) -> None:
        results = list(set(results))
        list_of_urls = self.excel_reader.url_list(results)
        temp_results = [
            {'count': index+1,
             'Title': self.__get_title(url),
             'URL': url,
             'Host': self.__get_hostnames(url),
            #  'Content': self.__get_content(url),
            #  'Mandatory_Keywords': self.excel_reader.mandatory_keywords_search(self.__get_content(url)),
            #  'Combination_Keywords': self.excel_reader.combination_keywords_search(self.__get_content(url)),
            } 
            for index, url in enumerate(list_of_urls)
        ]

        self.search_results['Records'] = len(temp_results)
        self.search_results['Results'] = temp_results
        


    def __get_content(self, link:str) -> str:
        article = Article(link)
        article.download()
        with open('article.html', 'w', encoding='utf-8') as file_handle:
            file_handle.write(article.html)
        article.parse()
        b = article.text
        
        return b


    def __get_hostnames(self, link:str):
        host = urlparse(link).netloc
        
        return host


    def __get_title(self, link:str) -> str:
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent':user_agent,} 
        request = Request(link, None, headers)
        response = urlopen(request)
        html = response.read()
        response.close()
        soup = BeautifulSoup(html, 'html.parser')
        title_1 = soup.title.get_text()
        
        return title_1



class QuerySearch:

    
    def __init__(self, query:str, excel_file_name:str) -> None:
        self.query = query
        self.excel_file_name = excel_file_name

        self.json_list = []
        SearchEngines = namedtuple('SearchEngines', ['GoogleUS','GoogleIN', 'Bing'])
        
        self.search_engines = SearchEngines('www.google.com','www.google.co.in', 'www.bing.com')
    

    def search(self):
        query_processing = QueryProcessing(self.query, self.search_engines.GoogleUS, self.excel_file_name)
        self.json_list.append(query_processing.search())

        query_processing = QueryProcessing(self.query, self.search_engines.GoogleIN, self.excel_file_name)
        self.json_list.append(query_processing.search())

        query_processing = QueryProcessing(self.query, self.search_engines.Bing, self.excel_file_name)
        self.json_list.append(query_processing.search())

        print(self.json_list)
    

    def dump_json(self):
        with open("sample.json", "w") as outfile:
            json.dump(self.json_list, outfile)



query_search = QuerySearch('Vijay Mallya', 'RiskPrediction2017.xlsx')
query_search.search()
query_search.dump_json()
