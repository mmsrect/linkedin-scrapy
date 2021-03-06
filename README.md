# linkedin-scrapy
All scrapers related to LinkedIn in Scrapy

## Chrome extension to copy cookies
Please install this Chrome extension to easily copy cookies in one click
https://chrome.google.com/webstore/detail/copy-cookies/jcbpglbplpblnagieibnemmkiamekcdg/

## Note:
1. This Scrapy script contains two spiders.
    1. To scrape company urls from the search results (Sales Navigator only)
    2. To scrape company data using company urls obtained using the first spider (Free LinkedIn user)
2. Scrapy will automatically choose the right spider based on the urls you enter inside the `input-urls.txt` file

## Installation on local PC
1. Download entire code as zip
2. Extract it on your PC
3. Install Python 3+
4. Open CMD and run `pip install scrapy`

## Usage:
1. Enter urls to scrape in input > input-urls.txt
2. Enter cookies in input > cookies.txt
    1. Here is a video on how to copy cookies using the Chrome extension - https://watch.screencastify.com/v/MtDq2ho6SQzZru5812cw
3. ***On Windows***: double click - `run.py` file to start the scraper.
4. ***On Mac***: Open Terminal > Type `python run.py` and hit enter
5. Output will be saved in the `Output` folder



   

