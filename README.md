# Zillow Clustering Project
## Table of Contents
- Goal
- Wrangle
  - Acquire
  - Prepare
  - Pre-processing
- Exploratory Data Analysis (EDA)
  - Visualizations
  - Clustering
  - Additional Feature Energizing (if need be)
- Modeling 
- Results & Conclusion

# Goal
The goal of this project is to attempt to improve upon the Logerror (Zestimate) of the Zillow price prediction model utilizing a combination of techniques, with a particular focus on cluster modeling. The final product, Zesults.ipynb, contains the EDA, Modeling, and the final model used. 

# Wrangle
The following processes are contained in the zillow_wrangle.py module which is used to acquire the data, prepare the data for processing, deal with missing data, and create basic features. The whole kit and caboodle is executed using the wrangle_zillow function within the Zesults notebook.

## Acquire
The data we are looking at is the Zillow data provided by the CodeUp(TM) and focus in on the predictions made in 2017 and only on single unit properties. 

The SQL used to pull the data can be found via the [acquire.py](https://github.com/datastraine/zillow-cluster-project/blob/main/acquire.py) function located in this repo. In addition to pulling the basic data from the DB, it also can do some pre-prep work utilizing some built functions including a summarize function, a function to count the number of missing rows per column, and count the number of missing columns per row.

## Prepare
After pulling the data using the acquire.py function I determined that single unit properties would be those properties zoned referred as Single-Family within the [Investors And Housing Affordability Report](https://www.aeaweb.org/conference/2020/preliminary/paper/ndkr58Tk) (downloads a PDF) which was built using Zillow data to analyze affordable housing. For convivence, the list is below
 
>Single-family: single family residential; townhouse; row house; mobile home; cluster home; seasonal, cabin, vacation residence; bungalow; zero lot line; patio home manufactured, modular, prefabricated homes; garden home; planned unit development; rural >residence; residential general; inferred single family residential.

In addition to eliminating properties that do not meet the above definition of a single family home, I created some additional features from the data to include
- More Than Two Baths 
- Tax amount per square foot of lotsize
- Tax amount per square foot of structure size
- Has a pool
- Has a basement

A data dictionary with all features that are used within the final product can be found [here]()

The final step in my prep phase was to detect upper bound outliers using IQR * 1.5 rule. I then choose to remove any outlier that was greater than the split difference between the max and the 3rd quantile as there were over 1000 rows of outliers. 

## Pre-processing

After prepping the data, I split the data into train, validate, test sets. After, I determine what data is missing in the test set and impute missing values for taxvaluedollarcnt, landtaxvaluedollarcnt, taxamount, structuretaxvaluedollarcnt calculatedfinishedsquarefeet, lotsizesquarefeet, and buildingqualitytypeid with median value for train test set across all sets. However, imputing missing regionidcity is a bit more complicated as using the mode across the whole data set would produce data is that is too prone to error as there are over 1,000 rows missing data. To handle this, I found the most frequent regionidcity that is associated with its associated regionidzip from the test set, and place this into a new DataFrame. I then merge the DataFrame onto each set of data, and use the most frequent regionidcity associated with each zip to fill the missing values. Any remaining rows for both regionidzip and regionidcity are dropped. Finally, the wrangle function returns the train, validate, test data sets for EDA and modeling.