import pandas as pd
import numpy as np
import acquire
import warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split

def get_upper_outliers(s, k):
    '''
    Given a series and a cutoff value, k, returns the upper outliers for the
    series.

    The values returned will be either 0 (if the point is not an outlier), or a
    number that indicates how far away from the upper bound the observation is.
    '''
    q1, q3 = s.quantile([.25, .75])
    iqr = q3 - q1
    upper_bound = q3 + k * iqr
    return s.apply(lambda x: max([x - upper_bound, 0]))

def add_upper_outlier_columns(df, k):
    '''
    Add a column with the suffix _outliers for all the numeric columns
    in the given dataframe.
    '''
    # outlier_cols = {col + '_outliers': get_upper_outliers(df[col], k)
    #                 for col in df.select_dtypes('number')}
    # return df.assign(**outlier_cols)

    for col in df.select_dtypes('number'):
        df[col + '_outliers'] = get_upper_outliers(df[col], k)

    return df

def handle_missing_values(df, prop_required_column=.5, prop_required_row=.5):
    '''
    This function takes in a DataFrame (df), a minium for prop_required_column [0:1] with deafult of .5, 
    and a minimum value [0:1] for prop_required_row with a default of .5.
    
    It will first drop columns who's missing data is less than prop_required_column value.
    It will then drop the rows who's missing data is lower than the prop_required_row.
    '''
    columns_to_keep = []
    columns = df.columns
    for col in columns:   
        if df[col].notnull().sum()/df.shape[0] >= prop_required_column:
            columns_to_keep.append(col)
    df = df[columns_to_keep]
    df['row_to_keep'] = df.notnull().sum(axis=1)/df.shape[1] >= prop_required_row
    df = df.loc[df['row_to_keep'] == True]
    df.drop(columns= ['row_to_keep'], inplace = True)
    return df

def wrangle_zillow():
    '''
    Loads zillow data and then fliters it where propertylandusetypeid is 260, 261, 262, 263, 264, 265, 268, 275, 276, or 279.
    Drops unnecessary id columns and any duplicated columns.    
    Creates a has_pool column where poolcnt = 1.
    Creates a has_basement column where basementsqft > 0.
    Creates a taxdollar_per_lotsqft  feature.
    Creates taxdollar_per_strcturesqft feature.
    Creates a more_than_two_bath column
    Replaces nan values with 'none' for heatingorsystemdesc
    Replaces nan values with 0 for hashottuborspa. This was done because the only values were nan or 1
    Drops calculatedbathnbr, fullbathcnt,  columns 
    Drops columns where the percentage of missing data is over 40%
    Drop rows where the percentage of missing data is over 50%
    Eliminates outliers above the the split difference between the 3rd quartile and max value.
    Splits the data into train, validate, test sets
    Imputes missing values with median and mode values from the test set were appropriate and drops remaining null rows
    Returns train, valiate, test sets
    '''
    df = acquire.load_zillow_data()
    df = df[df.propertylandusetypeid.isin([260, 261, 262, 263, 264, 265, 268, 275, 276, 279])]
    df.drop(columns = ['buildingclasstypeid', 'typeconstructiontypeid', 'storytypeid',
                   'propertylandusetypeid', 'heatingorsystemtypeid', 'architecturalstyletypeid',
                   'airconditioningtypeid', 'id', 'parcelid' , 'unitcnt', 'propertyzoningdesc', 
                   'finishedsquarefeet12', 'calculatedbathnbr', 'finishedsquarefeet12', 'fullbathcnt'], inplace = True)
    df.drop(columns = [c for c in df.columns if c.endswith('.1')], inplace=True)
    df['has_pool'] = df['poolcnt'] == 1
    df['has_basement'] = df['basementsqft'] > 0
    df['taxdollar_per_lotsqft'] = round(df['taxvaluedollarcnt']/df['lotsizesquarefeet'], 2)
    df['taxdollar_per_strcturesqft'] = round(df['taxvaluedollarcnt']/df['calculatedfinishedsquarefeet'], 2)
    df['more_than_two_bath'] = (df.bathroomcnt > 2).astype('int')
    df.heatingorsystemdesc.fillna('None', inplace = True)
    df.hashottuborspa.fillna(0, inplace = True)
    df.replace({True:1, False:0}, inplace = True)
    df = handle_missing_values(df, .6, .5)

    # Uses the get and upper outlier function above to find the upper outliers
    add_upper_outlier_columns(df, k=1.5)
    
    # Loop through the df columns to get the list of columns that end with _outlier
    outlier_cols = [col for col in df if col.endswith('_outliers')]
    
    # create a new DF to store the description of those results
    outremove = df[outlier_cols].describe()

    # Create another df that splits the difference 
    # between the max value and 3rd quantile to use as the remove threshold
    rows_to_remove = []
    threshold = []
    for col in outlier_cols:
        value = round((outremove[col].iloc[7] - outremove[col].iloc[6])/2, 0)
        threshold.append(value)
        key = col
        rows_to_remove.append(key)
        
    when_to_remove = pd.DataFrame()
    when_to_remove['rows_to_remove'] = rows_to_remove
    when_to_remove['threshold'] = threshold

    # Remove all the rows that meet that threshold 
    df = df[df['bathroomcnt_outliers'] < 7]
    df = df[df['bedroomcnt_outliers']< 4]
    df = df[df['calculatedfinishedsquarefeet_outliers'] < 9039]
    df = df[df['lotsizesquarefeet_outliers']< 3478688]
    df = df[df['structuretaxvaluedollarcnt_outliers'] < 4358331]
    df = df[df['taxvaluedollarcnt_outliers']< 23905851]
    df = df[df['landtaxvaluedollarcnt_outliers']< 24025184]
    df = df[df['taxamount_outliers'] < 286115]
    df = df[df['taxdollar_per_lotsqft_outliers'] < 33]
    df = df[df['taxdollar_per_strcturesqft_outliers'] < 2]

    #Drops all the outlier columns
    df.drop(columns=outlier_cols, inplace=True)

    # Splits the data into train, validate, test sets    
    train_validate, test = train_test_split(df, test_size=.2, random_state=333)
    train, validate = train_test_split(train_validate, test_size=.25, random_state=333)
    
    # Finds the median value for numeric columns and imputes that value for all missing values
    med_cols = [
    "taxvaluedollarcnt",
    "landtaxvaluedollarcnt",
    "taxamount",
    "structuretaxvaluedollarcnt",
    "calculatedfinishedsquarefeet",
    "lotsizesquarefeet",
    "buildingqualitytypeid"
    ]

    for col in med_cols:
        median = train[col].median()
        train[col].fillna(median, inplace=True)
        validate[col].fillna(median, inplace=True)
        test[col].fillna(median, inplace=True)

    # Finds the mode for year and imputes that value for all missing values
    mode = int(train['yearbuilt'].mode())# I had some friction when this returned a float (and there were no decimals anyways)
    train['yearbuilt'].fillna(value=mode, inplace=True)
    validate['yearbuilt'].fillna(value=mode, inplace=True)
    test['yearbuilt'].fillna(value=mode, inplace=True)
    
    # Get a list of zip values from the train set and remove the nan value
    zips = train[['regionidcity', 'censustractandblock','regionidzip']].loc[train['regionidcity'].isnull()].regionidzip.unique()
    zips = [12447.,  24832.,  24435.,  18874.,  13693.,  22827.,
        20008.,  16764.,  34543.,  33252.,  34780.,  39308.,  27491.,
        32923.,  54311.,  47568.,  14634.,  10734.,  32380.,  46298.,
        24384.,  47019.,  24812.,  38032.,   8384.,  39306.,  37688.,
        39076.,  42967., 118217.,  18875., 118694.,  45602.,  52842.,
        40081.,  17597.,  54970.,  15554.,  40009., 396556., 113576.,
        54352.,  17882.,  17150., 118895.,  14542., 118994.,  16677.,
        56780.,  12773.,  38980.,  47762.,  42091.,  30187., 114834.,
        14906.,  47547.,  25271.,  50749.,  17686.,  12292.,  53571.,
        45457.,  32927.,  44833.,  24174.,  21778.,  30908.]

    # Finds most fequent regionidcity for each zipcode in the train data set
    findcity = train[['regionidcity', 'regionidzip']].loc[(train['regionidzip'].isin(zips))]

    # Creates a data frame of those pairs and renames the columns
    pairs = pd.DataFrame(findcity.groupby('regionidzip')['regionidcity'].agg(pd.Series.mode)).reset_index()
    pairs.columns = ['zips', 'most_regionid']
    pairs = pairs[pairs['zips'] != 96395.0]

    # merges pairs data frame across the train, validate, and test data sets
    train = train.merge(pairs, how='left', left_on='regionidzip', right_on='zips')
    validate = validate.merge(pairs, how='left', left_on='regionidzip', right_on='zips')
    test = test.merge(pairs, how='left', left_on='regionidzip', right_on='zips')


    # Fills missing regionidcity with the most_regionid_y values for each data set
    train.regionidcity.fillna(train.most_regionid, inplace=True)
    validate.regionidcity.fillna(validate.most_regionid, inplace=True)
    test.regionidcity.fillna(test.most_regionid, inplace=True)
    # Drop the extra columns
    train.drop(columns=['zips', 'most_regionid'], inplace=True)
    validate.drop(columns=['zips', 'most_regionid'], inplace=True)
    test.drop(columns=['zips', 'most_regionid'], inplace=True)
    
    #Drop remaining null values
    train.dropna(inplace=True)
    validate.dropna(inplace=True)
    test.dropna(inplace=True)

    #Reutrn the data frame
    return train, validate, test

    