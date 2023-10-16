# Tax_agency_web_scraper

Web scrapper of companies' financial statements through the web site of the Tax Agency of Russia - pb.nalog.ru. 
Code starts with "Nologi_comp_info.py" script. This script initiates the whole scraping process, opens 
a source data xlsx file containing company names and composes final xlsx file with all of the results
found.

"Nologi_search.py" finds the information about a specific company on pb.nalog.ru and transmits it to the 
"Nologi_comp_info.py". "Nologi_GZ_sbis.py" searches for public procurements of a company on the independent
web site. 

The whole scrapper uses proxy rotation. It searches for current available free proxies and stores them into
an SQL database, it is proceeded by "proxy_.py" script. The tax agency's web site is very strict to proxy 
connections, it makes the scraping process to take quite a few time, however the system is stable and eventually
gets its job done. 

This repository also contains two excel files: "sites Белгород.xlsx" with the company names of a town of Belgorod
and "test_comp_info.xlsx" containing a sample of data that was scraped from the previous company list. There are
a lot of "none" cells, it is an issue of companies that were already closed at the time of scraping.
