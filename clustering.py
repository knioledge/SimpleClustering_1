# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 01:42:36 2022

@author: Yogesh
"""

#Load relevant packages
import datetime
from pandas_datareader import data as web
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

#Get data using the Yahoo datareader
def get_data(indexname, start_year):
    companies = pd.read_csv("tickers_"+indexname+".csv")
    companies["Ticker"] = companies["Tickers"]
    companies = companies.set_index("Tickers")
    start_date, end_date = datetime.datetime(start_year, 1, 1), datetime.datetime(2022, 1, 1)
    
    #get Adj Close prices (typically used for correlations) and clean
    data = web.DataReader(companies["Ticker"], 'yahoo', start_date, end_date)["Adj Close"];
    isnull = data.isnull().sum()
    for ticker in companies["Ticker"]:     #if too many null entries for given stock, exclude from analysis
        if isnull[ticker] > 50:
            data.drop(ticker, axis=1, inplace=True)
    return data, companies

def process_data(df, window_size, smooth, diff): 
    df = (df - df.median())/df.std()      #Scale Data
    dfscaled = df.copy()
    
    if smooth == 1:                       #Smooth Data
        df = df.rolling(window=window_size).mean()
        df = df[(window_size-1):]
        
    if diff == 1:                         #Get Derivative of data
        df = df.diff(axis=0)
        df = df[1:]
    return df, dfscaled

index = "S&PIT"     #options are DJIA, S&PEnergy, S&PIT, etc.
start_year = 2017   #get data from start_year (Jan 1st) 
window = 22         #rolling window for taking the mean Adj Close price. 22 trading day month assumed

data, companies = get_data(index, start_year)
data, data_scaled = process_data(data, window, 1, 1)
data.head()

#find correlation matrix, i.e. the "distances" between each stock
corr = data.corr()
size = 22
fig, ax = plt.subplots(figsize=(size, size))
ax.matshow(corr,cmap=cm.get_cmap('coolwarm'), vmin=0,vmax=1)
plt.xticks(range(len(corr.columns)), corr.columns, rotation='vertical', fontsize=8);
plt.yticks(range(len(corr.columns)), corr.columns, fontsize=8);

from scipy.cluster.hierarchy import dendrogram, linkage
Z = linkage(corr, 'average')
Z[0]



from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
import pylab
c, coph_dists = cophenet(Z, pdist(corr))
c

plt.figure(figsize=(25, 10))
labelsize=20
ticksize=15
plt.title('Hierarchical Clustering Dendrogram for '+index, fontsize=labelsize)
plt.xlabel('stock', fontsize=labelsize)
plt.ylabel('distance', fontsize=labelsize)
dendrogram(
    Z,
    leaf_rotation=90.,  # rotates the x axis labels
    leaf_font_size=8.,  # font size for the x axis labels
    labels = corr.columns
)
pylab.yticks(fontsize=ticksize)
pylab.xticks(rotation=-90, fontsize=ticksize)
plt.savefig('dendogram_'+index+'.png')
plt.show()
