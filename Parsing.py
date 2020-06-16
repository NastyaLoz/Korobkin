from bs4 import BeautifulSoup as bs
import requests as req
from Parser.Get_session import fetch_date
import aiohttp
import asyncio

def Parse_Site(site):
    resp = req.get(site)
    soup = bs(resp.text, 'html.parser')
    articles = soup.find_all(class_="new-article")
    lst_articles = []
    for i in articles:
        lst_articles.append({
            'title': i.h3.get_text(),
            'date': i.find(class_="mobile-date").get_text(),
            'link': i.find(class_="detail-link")['href'],
            'count_comments': i.find(class_="comment-icon").get_text()
        })

    return articles

async def download_news(queue):
    site = "https://v102.ru"
    url_form = "https://v102.ru/center_line_dorabotka_ajax.php?page={num}&category={category}"
    category = 0
    async with aiohttp.ClientSession() as session:
        for i in range(1, 2):
            url = str.format(url_form, num=i, category=category)
            html = await fetch_date(url, session)
            news = Parse_Site(html)
            articles = await asyncio.gather(
                *[fetch_date(link, session) for link in map(lambda article: site + article['link'], news)]
            )
            text_articles = map(parse_article, articles)
            for new, new_text in zip(news, text_articles):
                new['text'] = new_text
                new['link'] = site + new['link']
            await queue.put(news)

def parse_article(html_article):
    html = bs(html_article, 'html.parser')
    return html.find(class_='n-text').get_text()

