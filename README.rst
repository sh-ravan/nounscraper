Noun Project Scraper
====================

Originally forked from [https://github.com/yourcelf/nounscraper](https://github.com/yourcelf/nounscraper), but that didn't work at all. So, I had to rewrite it.

-----

[The Noun Project](http://thenounproject.com) is excellent, but the experience of downloading and using large numbers of icons from it is poor.  You download a zip file, which you then have to extract, and it has a random ID name rather than a meaningful noun name, and then associating the proper attribution with the icon is a pain.

This simple scraper makes this easier!  Point it at an index file on http://thenounproject.com, and it downloads the icons found on that page. It:

 * Downloads the .svg
 * Creates a JSON format file with the metadata associated with it

Downloads are cached and throttled to a maximum of one every 5 seconds to be
nice, and stay within the terms of use of the website.

Requirements
------------
Relies on [`Selenium`](https://selenium-python.readthedocs.io/), [`BeautifulSoup`](http://www.crummy.com/software/BeautifulSoup)

You need the Chrome Driver for Selenium. More on that [here](https://selenium-python.readthedocs.io/installation.html#drivers).

Python dependencies can be installed with::

    pip install -r requirements.txt

Usage
-----

    python scrape.py <nounproject index URL> [<more URLs> ...]
 
example::

    python scrape.py http://thenounproject.com/collections/modern-pictograms/

Writes SVGs and JSONs to `./icons`
