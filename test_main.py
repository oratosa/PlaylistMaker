from main import Scraping

from datetime import datetime


def test_get_html():
    scraper = Scraping()
    scraper.url = (
        "https://www.nhk.jp/p/sunshine/rs/ZYKKWY88Z9/blog/bl/prGL2NxxRv/bp/pvq3pX7g6O/"
    )
    scraper.html = scraper.get_html(scraper.url)
    site_name = scraper.html.find_all("meta", property="og:site_name")
    assert site_name[0].get("content") == "ウィークエンドサンシャイン - NHK"


def test_get_on_air_date():
    scraper = Scraping()
    scraper.url = (
        "https://www.nhk.jp/p/sunshine/rs/ZYKKWY88Z9/blog/bl/prGL2NxxRv/bp/pvq3pX7g6O/"
    )
    html = scraper.get_html(scraper.url)
    scraper.html = html.find("div", class_="article-text").find("strong")

    on_air_date = scraper.get_on_air_date(scraper.html)
    test_date = datetime.strptime("2023-4-22", "%Y-%m-%d").date()
    assert on_air_date == test_date
