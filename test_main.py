from main import Scraping

import pytest
from datetime import datetime


@pytest.fixture(scope="class")
def sample_scraper():
    scraper = Scraping()
    scraper.url = (
        "https://www.nhk.jp/p/sunshine/rs/ZYKKWY88Z9/blog/bl/prGL2NxxRv/bp/pvq3pX7g6O/"
    )
    scraper.html = scraper.get_html(scraper.url)
    yield scraper


def test_get_html(sample_scraper: Scraping):
    site_name = sample_scraper.html.find_all("meta", property="og:site_name")
    assert site_name[0].get("content") == "ウィークエンドサンシャイン - NHK"


def test_get_on_air_date(sample_scraper: Scraping):
    html = sample_scraper.html.find("div", class_="article-text").find("strong")
    on_air_date = sample_scraper.get_on_air_date(html)
    test_date = datetime.strptime("2023-4-22", "%Y-%m-%d").date()
    assert on_air_date == test_date
