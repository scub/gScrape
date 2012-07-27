gScrape
=======

Trivial Google Scraper

	Example Usage:
		from google import google
		gobj = google( 'test it', 25, '127.0.0.1:8118', 15 )
		for link in gobj.links(): print link
