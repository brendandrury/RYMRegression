# RYM Custom Charts

This project is still in its early stages and can only be run from the command line:

* Main.py will parse all of the pages within the files_to_scan folder and produce a JSON database. 
* Regression.py will regress based on several factors (release type, recency, obscurity), adjust all scores, and create a chart text file. 
* Just_chart.py will use a pre-existing regression (also stored in JSON) to generate a chart directly from the JSON database. 

Two forms of adjustments are utilized. For category-based adjustments, a simple multiplicative factor is used. For regressions, a quadratic fit is first determined; an album's adjustment is found by identifying its predicted score according to the fit relative to the fit's maximum. 

## Scraper

RYM has a strict policy against robots scraping pages, so a scraping tool has not been included here. The database used was scraped at a very low rate of pages per day in accordance with the policy. 

A small sample of pages is included to demonstrate the functionality of the scripts, as the full database is several gigabytes. The provided database.json file uses the entire data set. The tool scrapes from RYM's public HTML chart pages as the site does not yet have an API; the number of releases accessible from RateYourMusic's charts (and thus available to this tool) is very small compared to the website's full database.