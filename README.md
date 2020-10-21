# Zillow Clustering Project
## Table of Contents
- [Goal](#goal)
- [Wrangle](#wrangle)
  - [Acquire](#acquire)
  - [Prepare](#prepare)
  - [Pre-processing](#pre-processing)
- [Exploratory Data Analysis (EDA)](#exploratory-data-analysis-eda)
  - [Visualizations](#visualizations)
  - [Clustering](#clustering)
  - [Hypothesis Testing & Feature Selection](#hypothesis-testing--feature-selection)
- [Modeling](#modeling)
- [Results & Conclusion](#results--conclusion)
  - [Next Steps](#next-steps)

# Goal
The goal of this project is to attempt to improve upon the Logerror (Zestimate) of the Zillow 2017 price prediction model utilizing a combination of techniques, with a particular focus on cluster modeling. The final product, Zesults.ipynb, contains the EDA, Modeling, and the final model used to discover which features impact Logerror. 

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

The final step in my prep phase was to detect upper bound outliers using IQR * 1.5 rule. I then choose to remove any outlier that was greater than the split difference between the max and the 3rd quantile as there were over 1000 rows of outliers and this eliminated the most extreme upper bound cases. 

## Pre-processing

After prepping the data, I split the data into train, validate, test sets. After, I determine what data is missing in the test set and impute missing with their median values of test across all data sets for:

>taxvaluedollarcnt, landtaxvaluedollarcnt, taxamount, structuretaxvaluedollarcnt calculatedfinishedsquarefeet, lotsizesquarefeet, and buildingqualitytypeid 

However, imputing missing regionidcity is a bit more complicated as using the mode across the whole data set would produce data is that is too prone to error as there are over 1,000 rows missing data. To handle this, I found the most frequent regionidcity that is associated with its associated regionidzip from the test set, and place this into a new DataFrame. I then merge the DataFrame onto each set of data, and use the most frequent regionidcity associated with each zip to fill the missing values. Any remaining rows for both regionidzip and regionidcity are dropped. 

Finally, the wrangle function returns the train, validate, test data sets for EDA and modeling.

# Exploratory Data Analysis (EDA)
From here on out, this will be summary of what appears in the final notebook. For a more detailed explanation along with visuals please see the [zesualts notebook](https://github.com/datastraine/zillow-cluster-project/blob/main/zeults.ipynb).

## Visualizations
I began my EDA by creating some basic scatter plot visualizations, en masse, using seaborn and python for loops to print the visuals.

* For Y Values I used logerror (our target)

* For our x values I used:
>'bathroomcnt', 'bedroomcnt', 'calculatedfinishedsquarefeet', 'lotsizesquarefeet','roomcnt', 'structuretaxvaluedollarcnt', 'taxvaluedollarcnt', landtaxvaluedollarcnt', 'taxamount', 'taxdollar_per_lotsqft', 'taxdollar_per_strcturesqft', 

* For Z as hue I used:
>'fips', 'buildingqualitytypeid', 'regionidcity', 'regionidcounty', 'regionidzip', 'yearbuilt', 'heatingorsystemdesc',  'more_than_two_bath'

From these visualization I honed on visualizations that I felt were useful which where 
* Logerror by Calculated Finished SQFT with coloring by Building Quality ID
* Logerror by Calculated Finished SQFT Colored by More Than Two Bath
* Logerror by Building Quality and Colored by Heating and More than 2 Baths

## Clustering
Clustering is a useful way to create new features from our data. From the visualizations noted above and using industry knowledge I used ***KMeans*** to create multiple clusters from the following features:
>'bathroomcnt', 'bedroomcnt', 'buildingqualitytypeid', 'calculatedfinishedsquarefeet', 'yearbuilt', 'heatingorsystemdesc' (floor/wall and central dummies) , 'fips', 'more_than_two_bath', 'taxvaluedollarcnt', 'regionidzip', 'fips'

Before creating clusters, I scaled the data using ***RobustScaler*** due to outliers remaining in the data.

Cluster4 was created with 'buildingqualitytypeid', 'calculatedfinishedsquarefeet', 'more_than_two_bath' using 4 clusters. It appears that cluster #2 and cluster #3 are tightly associated with logerror v taxdollarcnt while cluster #0 and #1 are not. This may be a candidate for feature engineering.

## Hypothesis Testing & Feature Selection
After performing One Sample Two Tailed T-Test, Two Sample Two Tail T-Test, Pearson's R, and Chi Squared statistical tests on a verity of features, I found that the following alternative hypothesis deserved more scrutiny/testing:

- $Ha$ The mean log error of calculatedfinishedsquarefeet that are equal or above 3000sqf is not the same as the average logeerror
- $Ha$ The mean log error of calculatedfinishedsquarefeet that are below 3ksqft is not the same as the logerror of calculatedfinishedsquarefeet that are equal or above 3ksqft
- $Ha$ The mean logerror of homes with more than two baths is not the same as the average logerror for homes with 2 or less baths
- $Ha$ There is a linear realtionship between taxvaluedollarcnt and logerror
- $Ha$ There is a linear realtionship between calculatedfinishedsquarefeet and logerror

Sadly, none of the cluster I created were shown to have a statistical relationship with logerror as created.

From our hypothesis testing we can use the following features: 
>'above_or_equal_3ksqft', 'below_3ksqft', 'calculatedfinishedsquarefeet', 'taxvaluedollarcnt', 'more_than_two_bath',  and 'taxdollar_per_strcturesqft'

# Modeling
Now that we know what features we will use in our model we can begin trying to improve upon logerror scores. We will create 4 models with the baseline model being the 

* Baseline model is the mean of the logerror or logerror
* Model1 uses Linear Regression on All Features minus the clusters
* Model2 uses Linear Regression on 'calculatedfinishedsquarefeet', 'taxvaluedollarcnt', and 'more_than_two_bath'
* Model3 uses Linear Regression on 'calculatedfinishedsquarefeet', 'taxvaluedollarcnt'
* Model4 Linear Regression Model on 'taxdollar_per_strcturesqft', 'more_than_two_bath'
  
# Results & Conclusion
* Model 1 RMSE- 2.6999149263169895
* Model 2 RMSE - 2.7068312984163585
* Model 3 RMSE - 2.7068323544888107
* Model 4 RMSE - 2.706761265128289
* Baseline RMSE - 2.70938180290154

After running our creating two models we determined that the best model was the first model we created which used Linear Regression on All Features minus the clusters. However, the goal is to find which features impact logerror and in that case, less is more, so we will actually test on the model 4. Now we need to test our model on the test set to ensure it was not overfitted to the training data and if it still beats the baseline

After running the model on test we showed that it was not overfitted to the training or validate test sets as it out performed both. From this we now know that our two engineered features ***taxdollar_per_strcturesqft & more_than_two_bath*** have a decent amount of impact on the logerror. 

## Next Steps

While we have discovered two features that impact logerror, we did not get a chance to model other features, nor did we find clusters that could prove to be useful. For example, we structures that are above or below 3000sqft may prove to be useful for modeling. Additionally, while cluster4 as created did not show to have a relationship with logerror, it had two potential candidates for feature engineering and creating other clusters may have as well.
