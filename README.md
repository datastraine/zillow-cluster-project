# Zillow Clustering Project

## Goal
The goal of this project is to attempt to improve upon the Logerror (Zestimate) of the Zillow price prediction model utlizings a combination of techniquies, with a particular focus on cluster modeling.

## Acquire
The data we are looking at is the zillow data provided by the CodeUp(TM) and focus in on the predictions made in 2017 and only on single unit propreties. I determined that single unit properties would be those proerties zoned as [Single-Family Residence](http://planning.lacounty.gov/luz/summary/category/residential_zones) by LA County (the largest in the data set) and eliminating any type of proprety that may share a wall, foundation, or plot of land i.e. row townhouses. This leaves the following property types:
    * Inferred Single Family Residential
    * Residential General
    * Single Family Residential
    * Rural Residence
    * Bungalows

[Bungalows](https://en.wikipedia.org/wiki/California_bungalow) were kept as they were a very popular type of single family home built in Califonia between 1910 and 1940 as seen via the wikipedia article, and not necessarily a deteacted unit. [Patio Homes](https://www.realtor.com/advice/buy/what-is-a-patio-home/) were eliminated due to sharing a wall and/or foundation with another housing unit. 

