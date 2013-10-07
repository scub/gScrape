#!/usr/bin/python
#
# [ 01/27/2013 ]
#               Trivial Google Scraper
#
PY_VER=None

try:
        PY_VER=3
        from bs4 import BeautifulSoup as Soup
        from urllib.request import build_opener, ProxyHandler
        from urllib.error import URLError
except:
        PY_VER=2
        from BeautifulSoup import BeautifulSoup as Soup
        from cookielib import FileCookieJar as cookiejar
        import urllib, urllib2, re


from argparse import ArgumentParser
from random import choice
from re import compile


class gScrape:
        """
                Simple Module to Scrape Links From Google

                Example Usage
                =============
                        # Search for 'test it' and Pull 25 links through a locally bound proxy on 8118
                        g = gScrape( 'test it', proxy='127.0.0.1:8118' )
                        for link in g.links(): print( link )


        """
        def __init__( self, query, page=0, links=25, proxy=None, verbose=False ):
                """
                        Initialize Module Object -- Takes Up To 5 Arguments

                        query   - Query to search for
                        page    - Page to Start Parsing Results From (100 Per Page )
                        links   - Number Of Links To Strip
                        proxy   - Proxy Server (None Specified By Default )
                        verbose - Set Verbosity
                """
                self.config = {
                        'url'       : 'http://www.google.com/search?num=100&hl=el&site=&source=hp&q={}&start={}',
                        'proxy'     : proxy,
                        'query'     : query,
                        'verbose'   : verbose,
                        'page'      : int( page ) * 100,
                        'links'     : links,
                        're'        : compile( '\/url\?q\=(.*)\&sa\=U\&ei\=' ), 
                        'Agents'    : [
                                        'Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.1.9) Gecko/20100317 SUSE/3.5.9-0.1.1 Firefox/3.5.9',
                                        'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (.NET CLR 3.5.30729)',
                                        'Opera/5.0 (Linux 2.0.38 i386; U) [en]',
                                        'Opera/9.60 (Windows NT 5.1; U; de) Presto/2.1.1',
                                      ],
                }

                if PY_VER == 2:
                        self.config[ 'c_jar' ] = cookiejar()
                        self.getCookie()
                        if proxy is not None:
                                urllib2.install_opener( urllib2.build_opener( urllib2.ProxyHandler( { "http" : proxy } ) ) )


        def getCookie( self ):
                req = urllib2.Request( "http://www.google.com" )
                req.add_header( 'User-Agent', choice( self.config[ 'Agents' ] ) )
                self.config[ 'c_jar' ].add_cookie_header( req )

                resp = urllib2.urlopen( req )
                self.config[ 'c_jar' ].extract_cookies( resp, req )
                resp.close()


        def die( self, message ):
                """
                        Error Message And Die - Takes 1 Argument

                        message - String Containing Error Message
                """
                if self.config['verbose'] is not False: print( message )
                exit()

        def strip_links( self, soup ):
                """
                        Slow And Messy Link Parsing

                        soup - Beautiful Soup Object Containing Parsed HTML
                """
                lLinks = []
                for link_block in soup.findAll( 'h3', { 'class' : 'r' } ):
                        for link in link_block.findAll('a'):
                                try:
                                        lLinks.append( self.config['re'].match( link['href'] ).groups()[0] )
                                except:
                                        pass
                return lLinks

        def get_page( self ):
                """
                        Strip A Given Page For Links, Returning Them In A List - Takes 1 Argument

                        page_number - Page Number To Parse
                """
                if PY_VER == 3:
                        return self.get_page_3()
                else:
                        return self.get_page_2()


        def get_page_2( self ):
                """
                        Python 2 compatible get_page()
                """
                req = urllib2.Request( self.config[ 'url' ].format( self.config[ 'query' ], self.config[ 'page' ] ) )
                req.add_header( 'User-Agent', choice( self.config[ 'Agents' ] ) )
                req.add_header( 'Referer:', 'http://www.google.com' )
                self.config[ 'c_jar' ].add_cookie_header( req )

                try:
                        resp = urllib2.urlopen( req )
                        self.config[ 'c_jar' ].extract_cookies( resp, req )
                        soup = Soup( resp.read() )
                        resp.close()
                except ( urllib2.URLError, urllib2.HTTPError ) as Fail:
                        return '000: FAIL'

                return self.strip_links( soup )


        def get_page_3( self ):
                """
                        Python 3 compatible get_page()
                """
                if self.config['proxy'] is not None:
                        proxy = ProxyHandler( { 'http': self.config['proxy'] } )
                        opener = build_opener( proxy )
                else:
                        opener = build_opener()


                # Dirty User Agent Override
                opener.addheaders[0] = ( 'User-Agent', choice( self.config['Agents'] ) )

                try:
                        rep = opener.open( self.config['url'].format( self.config['query'], self.config['page'] ) )
                except URLError:
                        self.die( '\t[-] Unable To Retrieve URL' )

                html = rep.read()

                links = self.strip_links( Soup( html ) )
                return links
                
        def links( self ):
                """
                        Return Links in A List ( Programmatical )
                """
                ( linksParsed, links ) = ( 0, [] )

                while int( self.config['links'] ) >= linksParsed:
                        for link in self.get_page():
                                if ( linksParsed >= int( self.config['links'] ) ):
                                        return links

                                links.append( link )
                                linksParsed += 1

                        self.config['page'] = int( self.config['page'] ) + 100
                return links



        def raw_links( self ):
                """
                        Print Links To STDOUT And Exit ( CLI )
                """
                linksParsed = 0

                while int( self.config['links'] ) >= linksParsed:
                        for link in self.get_page():
                                if ( linksParsed >= int( self.config['links'] ) ):
                                        exit()

                                print( link )
                                linksParsed += 1
                        self.config['page'] = int( self.config['page'] ) + 1        



if __name__ == '__main__':
        parser = ArgumentParser( description="Trivial Google Scraper" )

        parser.add_argument( '-q', '--query', dest="query", help="Google Query To Scrape" )

        parser.add_argument( '-n', '--num', dest="links", default=25, \
                                help="Number Of Links To Return" )
 
        parser.add_argument( '-p', '--page', dest='page', default=0, \
                                help="Page To Parse" )

        parser.add_argument( '-P', '--Proxy', dest='proxy', default=None, \
                                help="Proxy Address To Use" )

        parser.add_argument( '-v', '--verbose',  action='store_true', dest='verbose', default=False, \
                                help="Enable Verbose Output" )


        args = parser.parse_args()

        if args.query is None:
                parser.print_help()
                exit()

        g = gScrape( args.query,args.page, args.links, args.proxy, args.verbose )
        g.raw_links()
