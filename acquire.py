import pandas as pd
import numpy as np
import env
import os

def get_connection(db, user=env.user, host=env.host, password=env.password):
    '''
    Returns a formatted url with login credentials to access data on a SQL database.
    '''
    return f'mysql+pymysql://{user}:{password}@{host}/{db}'

def load_zillow_data():
    '''
    This function acquires the zillow dataset from a SQL Database.
    It returns the zillow dataset as a Pandas DataFrame.
    
    A local copy will be created as a csv file in the current directory for future use.
    '''
    db = 'zillow'
    sql_query = '''
select * from properties_2017
	join (select parcelid, max(transactiondate) as transactiondate from predictions_2017
	group by parcelid) recent
	using(parcelid)
	join (select parcelid, logerror, transactiondate from predictions_2017) est
	on est.parcelid = recent.parcelid
	and est.transactiondate = recent.transactiondate
	left outer join zillow.airconditioningtype
	using(airconditioningtypeid)
	left outer join zillow.architecturalstyletype
	using (architecturalstyletypeid)
	left outer join zillow.heatingorsystemtype
	using(heatingorsystemtypeid)
	left outer join zillow.propertylandusetype
	using (propertylandusetypeid)
	left outer join zillow.storytype
	using(storytypeid)
	left outer join zillow.typeconstructiontype
	using(typeconstructiontypeid)
	left outer join zillow.buildingclasstype
	using(buildingclasstypeid)
	where latitude is not null 
	and longitude is not null;
	'''
    file = 'zillow_full.csv'
    
    if os.path.isfile(file):
        return pd.read_csv('zillow_full.csv')
    else:
        df = pd.read_sql(sql_query, get_connection(db))
        df.to_csv('zillow_full.csv', index=False)
        return df

def summarize(df):
	'''
	Prints the basic summary statistics of a data frame
	'''
	print("INFO \n")
	print(df.info)
	print("DESCRIPTION\n")
	print(df.describe())
	print("SHAPE \n")

def row_data(df):
	'''
	Takes in a data frame and returns the range of columns with missing data, 
	what precentage of missing columns that represents,
	and how many rows have that number of missing columns
	'''
	row_data = pd.DataFrame(df.isnull().sum(axis=1).value_counts().sort_values())
	row_data.reset_index(inplace = True)
	row_data.columns = ['num_cols_missing', 'num_rows']
	row_data['pct_cols_missing'] = column_data['num_cols_missing']/df.shape[1]
	row_data = column_data.sort_values('num_cols_missing').reset_index(drop= True)
	return row_data

def columns_data(df):
	'''
	Takes in a data frame and returns the number of rows and percentage of rows missing per column
	'''
	columns_data = pd.concat([pd.Series(df.isnull().sum()), pd.Series(df.isnull().sum()/df.shape[0])], axis=1)
	columns_data.reset_index(inplace = True)
	columns_data.columns=(['columns', 'num_rows_missing', 'pct_rows_missing'])
	return columns_data

