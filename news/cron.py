import requests
from bs4 import BeautifulSoup

from django.core.cache import cache
from news.models import NewsArticle


def news_crawling_job():
    url = "https://news.naver.com/breakingnews/section/102/251"
    response = requests.get(url)
    dom = BeautifulSoup(response.text, "html.parser")

    news_data = []
    news_url = []

    news_items = dom.find_all("div", class_="sa_item_inner")

    for item in news_items:
        title_head = item.find("div", class_="sa_text")
        title_tag = title_head.find("a", class_="sa_text_title")
        title = title_tag.find("strong", class_="sa_text_strong").text if title_tag else ""

        summary_head = item.find("div", class_="sa_text")
        summary_tag = summary_head.find("div", class_="sa_text_lede")
        summary_with_date = summary_tag.text if summary_tag else ""

        summary = " ".join(summary_with_date.split()[:-1])

        news_link = title_tag['href'] if title_tag and 'href' in title_tag.attrs else ""

        image_tag = item.find("a", class_="sa_thumb_link")
        image_link = ""
        if image_tag:
            image_img = image_tag.find("img", class_="_LAZY_LOADING _LAZY_LOADING_INIT_HIDE")
            image_link = image_img['data-src'] if image_img and 'data-src' in image_img.attrs else ""

        if title and summary and not NewsArticle.objects.filter(title=title, news_link=news_link).exists():
            news_data.append({"title": title, "summary": summary, "news_link": news_link, "image_link": image_link})
            news_url.append(news_link)

    for i in range(len(news_url)):
        response = requests.get(news_url[i])
        dom = BeautifulSoup(response.text, "html.parser")

        news_items = dom.find_all("div", class_="newsct_body")
        first_article = news_items[0].find("article", class_="go_trans _article_content")

        img_desc = first_article.find("em", class_="img_desc")
        if img_desc:
            img_desc.decompose()

        news_agency_tag = dom.find('img',
                                   class_='media_end_head_top_logo_img light_type _LAZY_LOADING _LAZY_LOADING_INIT_HIDE')
        news_agency = news_agency_tag.get('alt') if news_agency_tag else 'Unknown'

        timestamp_tag = dom.find('span', class_='media_end_head_info_datestamp_time _ARTICLE_DATE_TIME')
        timestamp = timestamp_tag.text.strip() if timestamp_tag else 'Unknown'

        news_content = first_article.get_text(separator="\n", strip=True)

        news_data[i]['news_agency'] = news_agency
        news_data[i]['timestamp'] = timestamp
        news_data[i]['news_content'] = news_content

        # db에 저장
        if NewsArticle.objects.filter(news_link=news_data[i]['news_link']).exists():
            continue
        else:
            NewsArticle.objects.create(
                title=news_data[i]['title'],
                summary=news_data[i]['summary'],
                news_link=news_data[i]['news_link'],
                image_link=news_data[i]['image_link'],
                news_agency=news_data[i]['news'],
                timestamp=news_data[i]['timestamp'],
                news_content=news_data[i]['news_content']
            )

    # cache 저장
    recent_news_data = NewsArticle.objects.order_by('-id').values('id', 'title', 'image_link', 'news_agency', 'summary', 'timestamp')[:20]
    cache.set('news_articles', recent_news_data, timeout=60 * 60)
    print("Cron job executed, data stored in DB and Redis")
