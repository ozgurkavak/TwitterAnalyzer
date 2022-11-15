from os import access
import tweepy
import time
from datetime import datetime, timezone
import numpy as np 
import pandas as pd
import gspread
import csv
from auth import spreadsheet_service
from oauth2client.service_account import ServiceAccountCredentials
import os
import sys


from oauth2client.service_account import ServiceAccountCredentials
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
open(dir_path + '/' + 'service_account.json')

#Twitter API
consumerKey = "YOUR CONSUMER KEY"
consumerSecret = "YOUR CONSUMER SECRET"
accessToken = "YOUR ACCESS TOKEN"
accessTokenSecret = "YOUR ACCESS TOKEN SECRET"
auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth)

#Welcoming Screen
print("---Welcome to Twitter Analyzer---\n" + "Please Wait for Data to be Imported! \n")
time.sleep(3)

#Google Spreadsheets - workspace build
sa = gspread.service_account(filename = 'service_account.json')
sh = sa.open("YOUR GOOGLE SHEET")
wksInf = sh.worksheet("WORKSHEET")

#rowCount = wks.row_count #print('Rows: ', wks.row_count)
#colCount = wks.col_count #print('Cols: ', wks.col_count)

#Getting Twitter Accounts on Google Sheet
accountID = []
accountID = wksInf.col_values(4) #(accountID - Screen Names)

#TODO remove first item of accountID that is Screen Names
#print("Screen Names: \n", *accountID, sep= "\n")
accountID.remove("Screen Name")

for accounts in range(len(accountID)):
    print(accounts, ". account is: ", accountID[accounts])
    time.sleep(0.1)
print(len(accountID))

#arrays
tweetData = []

#input amount of tweets to analyse
numberOfTweets = 30

for i in range(len(accountID)):
    timeline = api.user_timeline(screen_name = accountID[i], 
                                count = numberOfTweets, 
                                tweet_mode = "extended", 
                                exclude_replies = True)
    
    for tweet in timeline:
        print("------\n",
            "\nScreen Name: ", accountID[i],
            "Tweet: ", tweet.full_text,
            "\n Date:", tweet.created_at, 
            "\n Tweet id: ", tweet.id )
        tweetData.append(accountID[i])
        tweetData.append(tweet.full_text)
        parentTweetID = tweet.id
        #twt = api.get_status(id = twtID)
        #parentTweetID = twt.in_reply_to_status_id
        parentTweet = api.get_status(id = parentTweetID)
        replies = []
        requestCount = 1      
        for mention in tweepy.Cursor(api.search_tweets, 
                                    q ="@{}".format(parentTweet.user.screen_name), 
                                    since_id = parentTweetID, 
                                    tweet_mode = 'extended', 
                                    result_type = 'recent').items(500):
            requestCount = requestCount + 1
            time.sleep(1)
            if requestCount < 400:
                if mention.in_reply_to_status_id == parentTweetID:
                    range = mention.display_text_range
                    replyFullText = mention.full_text
                    onlyText = replyFullText[range[0]:range[1]]
                    twitterName = mention.user.screen_name
                    reply = parentTweet.user.screen_name + " | replied " + onlyText + " | " + "by {}".format(twitterName)
                    replies.append(reply)
                    print('sibling extracted')
                    print("Current Time = ", current_time)
                    time.sleep(1)
                else:
                    print('no replys in mentions found')
                    print("Current Time = ", current_time)
                    time.sleep(1)
            else:
                print('request limit reached')
                print("Current Time = ", current_time)
                time.sleep(1000)
                req_count = 0
        print('recieved {} replies'.format(len(replies)))
        print("Replies: \n", *replies, sep="\n")
        time.sleep(1)
    print("Tweet Data of ", accountID[i], *tweetData, sep= "\n")
    print("---End of An Account---\n")
    print("Current Time = ", current_time)
print("---End Of Searching---")
print("Current Time = ", current_time)

with open('replies_clean.csv', 'w') as f:
    csv_writer = csv.DictWriter(f, fieldnames=('user', 'text'))
    csv_writer.writeheader()
    for tweet in replies:
        row = {'user': tweet.user.screen_name, 'text': tweet.text.replace('\n', ' ')}
        csv_writer.writerow(row)

#Analyse Time
print("Process Time: ", time.process_time)
print("Current Time = ", current_time)
