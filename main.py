import multiprocessing
import datetime
import os
from database import Database
from crawler import WebCrawler
from xml import generate_xml
from newspaper import Article
from multiprocessing import Pool
from functools import partial

BASE_URL = 'http://www.cnn.com'
MAX_PAGES = 5000


def get_info(url, articles):

    try:
        a = Article(url)
        a.download()
        a.parse()
        articles.append((a.url, ', '.join(a.authors), a.publish_date,
                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         a.top_image, a.text, generate_xml(a.text)))
        print('Added information for: {}'.format(url))
    except:
        print('Cannot download {}'.format(url))


def main(base_url, max_pages):
    sql = """INSERT INTO articles (url,authors,publish_date,scraped_date,top_image,article_text,xml) 
                            VALUES (?, ?, ?, ?, ?, ?, ?);"""
    articles = []
    path = os.getcwd() + '/SQLite/articles.db'
    
    db = Database(path)
    db.create_connection()
    db.create_table("""CREATE TABLE IF NOT EXISTS articles (
                                        url text PRIMARY KEY,
                                        authors text,
                                        publish_date text,
                                        scraped_date text,
                                        top_image text,
                                        article_text text,
                                        xml text
                                        );""")
    crawler = WebCrawler(base_url, max_pages)
    crawler.run_crawler()
    func = partial(get_info, articles=articles)
    pool = Pool(10)
    pool.map(func, crawler.links)
    pool.close()
    pool.join()
    db.insert_rows(sql, articles)
    db.close_connection()


if __name__ == '__main__':
    main(BASE_URL, MAX_PAGES)
    
