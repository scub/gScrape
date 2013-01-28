gScrape
=======

Trivial Google Scraper [ Python 3 ]


        Dependencies Outside Of Standard Library
                - Beautiful Soup 4
                        $> easy_install-3.2 BeautifulSoup4


	Example Programmatical Usage:
		from gScrape import gScrape as google
		gobj = google( 'test it', 0, 25, '127.0.0.1:8118', False )
                for link in gobj.links(): print( link )

                gobj = google( 'test it' )
                for link in gobj.links(): print( link )


        Example CLI Usage:
                $> ./gScrape.py -q 'Test'
                $> ./gScrape.py -v -q 'Test' -n 25 -p 0 -P '127.0.0.1:8118' 
