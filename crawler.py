import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse


class WebCrawler:
    def __init__(self, base_url, max_links):
        self.base_url = base_url
        self.max_links = max_links
        self.root_url = '{}://{}'.format(urlparse(self.base_url).scheme, urlparse(self.base_url).netloc)
        self.pool = ThreadPoolExecutor(max_workers=10)
        self.links = set()
        self.to_crawl = Queue()
        self.to_crawl.put(self.base_url)

    def crawl_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.links:
                    self.to_crawl.put(url)

    def callback(self, response):
        result = response.result()
        if result and result.status_code == 200:
            self.crawl_links(result.text)

    def crawl_page(self, url):
        try:
            res = requests.get(url, timeout=(3, 30))
            return res
        except requests.RequestException:
            return

    def run_crawler(self):
        while len(self.links) < self.max_links:
            try:
                url = self.to_crawl.get(timeout=60)
                if url not in self.links:
                    print('Scraping: {}'.format(url))
                    self.links.add(url)
                    job = self.pool.submit(self.crawl_page, url)
                    job.add_done_callback(self.callback)
            except Exception as e:
                print(e)
                continue
        return
