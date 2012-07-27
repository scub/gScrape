#!/usr/bin/python
"""
	Trivial Google Scraper

"""
import urllib2, urllib, re
from cookielib import FileCookieJar as cookiejar
from BeautifulSoup import BeautifulSoup

class google:
	"""
		Simple Module To Scrape Links From Google

		 Example Use
		=============
		# Search for 'test it' and Pull 25 links through a locally bound proxy and throttle
		# search iteration 10 seconds
		>>> g = google( 'test it', 25, '127.0.0.1:8118', 10 )
		>>> for x in g.links(): print x

	"""
	def __init__( self, query, linkCount=10, proxy=None, throttle=5 ):
		"""
			Initialize Module Object - Takes up to 4 arguments

			query 	  - Query To Search For
			linkCount - Number Of Links To Pull Back (10 By Default)
			proxy 	  - Proxy Server (None Specified By Default)
			throttle  - Sleep Time Between Page Parses (5 Seconds by Default)
		"""

		self.url_next, self.url, self.userAgent, self.home, self.regex, self.query, self.c_jar, self.linkCount, self.throttle = (
			"http://www.google.com/search?num=100hl=el&site=&source=hp=&q={}&start={}",
			"http://www.google.com/search?num=100&hl=en&site=&source=hp&q={}",
			"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)",
			"http://www.google.com",
			re.compile( '^/url\?q\=(http.*)&sa=U&ei=.*' ),
			urllib.quote_plus( query ),
			cookiejar(),
			linkCount,
			throttle )

		if proxy is not None: 
			urllib2.install_opener( urllib2.build_opener( urllib2.ProxyHandler( {"http" : proxy} ) ) )

		self.getCookie()

	def newQuery( self, query, linkCount=0 ):
		"""
			Setup New Query - Takes up to 2 arguments

			query	  - New Query To Search
			linkCount - Number of links to grab, if left unspecified the previous is used
		"""
		self.query, self.linkCount = urllib.quote_plus( query ), ( linkCount, self.linkCount )[ linkCount is 0 ]

	def getCookie( self ):
		"""
			Get Initial Cookie From Google To Allow For Parsing
		"""
		req = urllib2.Request( self.home )
		req.add_header( 'User-Agent', self.userAgent )		# Spoof User-Agent
		self.c_jar.add_cookie_header( req )

		resp = urllib2.urlopen( req )
		self.c_jar.extract_cookies( resp, req )			
		resp.close()


	def getResults( self, url ):
		"""
			Retrieve Raw HTML of Search From Google - Takes one argument, Returns list of links

			url - Url to GET
		"""
		req = urllib2.Request( url.format( self.query ) )
		req.add_header( 'User-Agent', self.userAgent )
		req.add_header( 'Referer:', 'http://www.google.com' )
		self.c_jar.add_cookie_header( req )

		try:
			resp = urllib2.urlopen( req )
			self.c_jar.extract_cookies( resp, req )
			soup = BeautifulSoup( resp.read() )
			resp.close()
		except (urllib2.URLError, urllib2.HTTPError):
			return '000: FAIL'

		return self.parseLinks( soup )
		

	def parseLinks( self, soup ):
		"""
			Parse Links From Given HTML soup - Takes one argument, Returns list of links

			soup - BeautifulSoup object of returned google html
		"""
		links = []
		for url in soup.findAll( 'a' ):
			try:
				if '/url?' in url['href']:
					links.append( re.findall( self.regex, url['href']  )[0] )

				if len(links) >= self.linkCount: break
			except KeyError:
				pass

		return links


	def links( self ):
		"""
			Main Method - Takes no arguments, Returns List of links
		"""
		link_list = []
		while len(link_list) < self.linkCount:
			try:
				if len( link_list ) is not 0:
					rez = self.getResults( self.url_next.format( self.query, len(link_list) ))
				else:
					rez = self.getResults( self.url.format( self.query ) )

				if '000: FAIL' in rez: break 
				link_list.extend( rez )
				sleep( self.throttle )

			except:
				continue
		
		return link_list
