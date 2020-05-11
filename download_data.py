# https://pushshift.io/api-parameters/
# https://www.reddit.com/r/pushshift/comments/8h31ei/documentation_pushshift_api_v40_partial/

import datetime as dt
import time
import pandas as pd
from psaw import PushshiftAPI
import requests
import os
import praw
#importing our error
from prawcore.exceptions import Forbidden


my_client_id = '74CBTlXRo31zAg'
my_client_secret = 'qvpDreHLSY2-QicrieFmc_R-NfM'
my_user_agent = 'newVisualization'
reddit = praw.Reddit(client_id = my_client_id,
                     client_secret = my_client_secret,
                     user_agent = my_user_agent)

api = PushshiftAPI(reddit)


matching_praw_submissions = []

# Default time values if none are defined (credit to u/bboe's PRAW `submissions()` for this section)
utc_offset = 0
 
#discussion_communities = ['askreddit', 'ama', 'askscience']
entertainment_communities = ['movies', 'television', 'sports']
humor_communities = ['memes', 'funny', 'humor']
news_communities = ['worldnews', 'news', 'politics']
other_communities = ['science', 'technology', 'economics']
#country_communities = ['spain', 'denmark', 'italy']


subreddit = 'gaming'
limit = 400

 # Creating folder paths
year = '2020'
parent_folder = ('/home/jpre/Documents/DTU/SocialDataViz/Project/{0}//subreddits/').format(year)
subreddit_folder = parent_folder + subreddit + '/'
week_folder = subreddit_folder + 'weeks' + '/'
day_folder = subreddit_folder + 'days' + '/'

if not os.path.exists(subreddit_folder):
    os.makedirs(subreddit_folder)

if not os.path.exists(week_folder):
    os.makedirs(week_folder)
    
if not os.path.exists(day_folder):
    os.makedirs(day_folder)

 # Defining query (1/2)
first_day = ('{0}-01-01 00:00:00').format(year)
last_day = ('{0}-04-19 00:00:00').format(year)
first_monday = ('{0}-01-06 00:00:00').format(year)
last_monday = ('{0}-04-13 00:00:00').format(year)

days = pd.date_range(start=first_day, end=last_day, freq='D')
days = [d.timestamp() for d in days]
mondays = pd.date_range(start=first_monday, end=last_monday, freq='W-MON')
mondays = [d.timestamp() for d in mondays]

    
#week_folder
week_offset = 6*60*60*24 + 60*60*23 + 59*60
day_offset = 60*60*23 + 59*60

the_folder = day_folder
period = days
delta_period = day_offset

last_day = 54
#for j in range(len(period)):
for j in [last_day+x for x in range(106-last_day)]:    
    

    ini_period = int(period[j]) 
    end_period = int(ini_period + delta_period)
    
    # Defining query (2/2)
    # Format our search link properly.
    url_0 = 'https://api.pushshift.io/reddit/search/submission/?'
    filters = '&filter=id,score,title,subreddit,c120reated,created_utc,num_comments'
    sorting = '&sort_type=score&sort=desc'
    search_link = url_0 + 'before=' + str(end_period) +'&after='+ str(ini_period) + '&size=' + str(limit) + sorting + filters
    if subreddit != 'all':
        search_link = search_link + '&subreddit='+ subreddit
        
    # Get the data from Pushshift as JSON.
    retrieved_data = requests.get(search_link)
    returned_submissions = retrieved_data.json()['data']
    
    file_folder = the_folder + str(j) + '/'

    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    # Iterate over the returned submissions to convert them to PRAW submission objects.
    #file_scores = open(file_folder + 'scores.txt', 'w')
    #file_dates = open(file_folder + 'dates.txt', 'w')
    #file_subreddits = open(file_folder + 'subreddits.txt', 'w')
    
    file_df = open(file_folder + 'df.txt', 'w')
    file_titles = open(file_folder + 'titles.txt', 'w')
    
    for submission in returned_submissions:
        
        # Take the ID, fetch the PRAW submission object, and append to our list
        praw_submission = reddit.submission(id=submission['id'])
        matching_praw_submissions.append(praw_submission)
        
        #trying to comment (we may be banned)
        try:
            post_title = praw_submission.title
            post_score = str(praw_submission.score)
            post_created_utc = str(praw_submission.created_utc)
            post_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(praw_submission.created_utc)))
            post_created = str(praw_submission.created)
            post_local_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(praw_submission.created)))
            post_subreddit = str(praw_submission.subreddit)
            post_num_comments = str(praw_submission.num_comments)
            post_id = str(praw_submission.id)
            
            #file_scores.write(post_score + '\n')
            #file_dates.write(post_created_utc + '\n')
            #file_subreddits.write(post_subreddit + '\n')
            
            file_titles.write(post_title + '\n')
            file_df.write(post_time + '\t' + post_created_utc + '\t' + post_local_time + '\t' + post_created + '\t' + post_id + '\t' + post_score  + '\t' + post_subreddit + '\t' + post_num_comments + '\n')
            
        #doing something if we can't comment
        except Forbidden:
           print(f"We\'ve been banned from somewhere!")
        
        
    #file_scores.close()
    #file_dates.close()
    #file_subreddits.close()
    file_df.close()
    file_titles.close()