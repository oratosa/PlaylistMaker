from main import Scraping

import pytest
from datetime import datetime


@pytest.fixture(scope="class")
def sample_scraper():
    scraper = Scraping()
    scraper.url = (
        "https://www.nhk.jp/p/sunshine/rs/ZYKKWY88Z9/blog/bl/prGL2NxxRv/bp/pkd9r03agZ/"
    )
    scraper.html = scraper.get_html(scraper.url)
    yield scraper


def test_get_html(sample_scraper: Scraping):
    site_name = sample_scraper.html.find_all("meta", property="og:site_name")
    assert site_name[0].get("content") == "ウィークエンドサンシャイン - NHK"


def test_get_on_air_date(sample_scraper: Scraping):
    html = sample_scraper.html.find("div", class_="article-text").find("p")
    on_air_date = sample_scraper.get_on_air_date(html)
    test_date = datetime.strptime("2023-5-13", "%Y-%m-%d").date()
    assert on_air_date == test_date


def test_generate_track_list(sample_scraper: Scraping):
    html = sample_scraper.html.find("div", class_="article-text").find("ol")
    track_list = sample_scraper.generate_track_list(html)
    assert track_list[0] == ["01", "Looking For Clues", "Robert Palmer", "Clues"]
    assert track_list[14] == [
        "15",
        "I Still Haven’t Found What I’m Looking For",
        "U2",
        "Songs Of Surrender",
    ]
