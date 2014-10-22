import numpy as np
import pandas as pd
import scipy as sp 
import csv as csv
import pyechonest 
from pyechonest import config
from pyechonest import artist
from pyechonest.util import EchoNestAPIError
import time



#first only take a subset of the total plays file
plays = pd.read_table('usersha1-artmbid-artname-plays.tsv', header = None, names = np.array(['user', 'artid', 'artname','song']))
#print plays.shape
#(17535655,4)
#select 1 million 
#plays.iloc[0:1000000]
plays_sub = plays.iloc[0:1000000]
plays_sub.to_csv('plays_sub.csv', index = False)
plays_sub = pd.read_csv('plays_sub.csv', header = 0)
# only check the first 100 listeners for exploratory analysis is enough
# and save these 100 users to a new file called 'play_user_100.csv'
plays_unique_user = plays_sub.user.value_counts()
play_user_100 = plays_unique_user.iloc[10:45] #only 35 subject due to time
play_user_100.to_csv('play_user_100.csv', header =['count'])
#note: need to add 'user' to the saved dataset
play_user_100 = pd.read_csv('play_user_100.csv', header = 0)
#only need the plays data from these 100 users, to re-sub the plays_sub
plays_res = pd.DataFrame()
for user100 in play_user_100.user:
       plays_res = plays_res.append(plays_sub.loc[plays_sub['user'] == user100])
plays_res.to_csv('plays_res.csv', index = False)
#note: need to add 'user' to the saved dataset
plays_res = pd.read_csv('plays_res.csv', header = 0)

#now access the users information from the 'usersha1-profile.tsv' file, and pull up the data into a new subset file
users = pd.read_table('usersha1-profile.tsv', header = None, names = np.array(['user', 'gender', 'age','country','time']))
users_sub = pd.DataFrame()
for user100 in play_user_100.user:
       print  (users.loc[users['user'] == user100])
       users_sub = users_sub.append(users.loc[users['user'] == user100])
users_sub.to_csv('users_sub.csv', index = False)	
# read the users_sub from the saved file
users_sub = pd.read_csv('users_sub.csv', header = 0)
#print users_sub['age']
#users_sub['age'].mean()
#pd.DataFrame.hist(users_sub)

myAPIkey = open('myAPIkey.txt').readline()
# for each user's artist, fetch the music attribute information from Echonest.
config.ECHO_NEST_API_KEY= myAPIkey

#access for the two metrics for each artist in the plays_res dataset, one for familiarity, and one for hottness---hottness removed because of limit of API access and time!!!





def echo_familiarity_hotness(art_name):
    #while True:
    try:
	    return artist.Artist(art_name).familiarity
		   #due to API limit, doNOT retieve another metric here
		   #artist.Artist(art_name).hotttnesss)
    except EchoNestAPIError,error:
	    http_status = error.http_status
	    # If the artist is not found, return empty dict
	    # EchoNestAPIError: (u'Echo Nest API Error 5: The Identifier specified does not exist [HTTP 200]',)
	    if http_status == 200:
		    print http_status
		    return None
	   # If we've exceeded the rate limit, wait 5 seconds and then try again
	   # EchoNestAPIError: (u'Echo Nest API Error 3: 3|You are limited to 120 accesses every minute. You might be eligible for a rate limit increase, go to http://developer.echonest.com/account/upgrade [HTTP 429]',)
	    elif http_status == 429:
		    print 'has to sleeeeep'
		    time.sleep(52)
	   # Any other error, raise the exception
	    else:
		    raise error

def compute_user_familarity(user_data):
	user_data_fam = sum(user_data.fam*user_data.song)/sum(user_data.song)
	return user_data_fam
			
plays_result = pd.DataFrame(columns = ['user','artid','artname','song','fam'])

for index in range(plays_res.shape[0]):
	art_name = plays_res.iloc[index]['artname']
	fam = echo_familiarity_hotness(art_name)
	print index
	print fam
	if fam == None:
		pass			
	else:
		gen_item = plays_res.iloc[index]
		gen_item['fam'] = fam
		plays_result.loc[index] = gen_item
		
plays_result.to_csv('plays_result.csv', index = False)
#read the result from local file
plays_result = pd.read_csv('plays_result.csv', header = 0)

unique_users = plays_result['user'].unique()
fam_user_data = pd.DataFrame()
for each_user in unique_users:
	#print each_user
	#each_user = '0d0fe8cea8080f0d602bd72c866a452660d60860'
	each_user_data = plays_result.loc[plays_result['user'] == each_user]
	#print  each_user_data.shape
	each_user_data_fam = compute_user_familarity(each_user_data)
	#print each_user_data_fam
	#users_sub
	fam_each_user_data = users_sub.loc[users_sub['user'] == each_user]
	fam_each_user_data['fam'] = each_user_data_fam
	fam_user_data = fam_user_data.append(fam_each_user_data)

#plt.figure()
age_effect = fam_user_data.plot(kind='scatter',x='age', y='fam', title = 'the relation between age and familarity')
age_effect.set_ylabel("familarity")

gender_effect = fam_user_data.boxplot(column=['fam'], by= ['gender'])
gender_effect.set_xlabel("gender")
gender_effect.set_ylabel("familarity")

