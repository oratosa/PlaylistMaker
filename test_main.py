from main import Scraping

import pytest, json
from datetime import datetime


@pytest.fixture(scope="class")
def sample_scraper():
    scraper = Scraping()
    scraper.url = (
        "https://www.nhk.jp/p/sunshine/rs/ZYKKWY88Z9/blog/bl/prGL2NxxRv/bp/pkpOW0AQlX/"
    )
    scraper.html = scraper.get_html(scraper.url)
    yield scraper


@pytest.fixture(scope="class")
def sample_page_title(sample_scraper: Scraping):
    page_title = sample_scraper.html.head.title.text.split()[0]
    yield page_title


@pytest.fixture(scope="class")
def sample_playlist(sample_scraper: Scraping, sample_page_title: str):
    playlist = sample_scraper.extract_playlist(sample_page_title)
    yield playlist


def test_get_on_air_date(sample_scraper: Scraping, sample_playlist: list):
    on_air_date = sample_scraper.get_on_air_date(sample_playlist)
    test_date = datetime.strptime("2024-4-27", "%Y-%m-%d").date()
    assert on_air_date == test_date


def test_generate_track_list(sample_scraper: Scraping, sample_playlist: list):
    track_list = sample_scraper.generate_track_list(sample_playlist)
    assert track_list[0] == [
        "01",
        "Whipping Post",
        "The Allman Brothers Band",
        "The Allman Brothers Band",
    ]
