#-*-coding:utf-8-*-
#tweetidからtweet全体のデータに変換するプログラム

from requests_oauthlib import OAuth1Session
import json
import os, sys
import time, calendar
import random
from datetime import datetime
import re
import emoji
import mojimoji
from config import config05

CK = config05.CK
CS = config05.CS
AT = config05.AT
AS = config05.AS
session = OAuth1Session(CK, CS, AT, AS)
url = 'https://api.twitter.com/1.1/favorites/list.json'

YEAR = 2018
FMONTH = 12
LMONTH = 12

#読み込みディレクトリ，ファイル
READ_DIR = "../DATA/03.16P_MBTI/"

GET_NUM_TWEET = 3200

#書き込みディレクトリ, ファイル                                        
WRITE_DIR = "../DATA/15.16P_FAVTEXT_ALL/"
if os.path.exists(WRITE_DIR) == False:
    os.mkdir(WRITE_DIR)
WRITE_INFO_FILE = WRITE_DIR+"info_"+str(YEAR)+str(FMONTH).zfill(2)+".txt"

#UTCから日本時間へ
def utc2jtime(created_at):
    time_utc = time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    jtime = time.strftime("%Y%m%d%H%M%S", time_local)
    return jtime

#レスポンスチェック
def check_res(res):
    flag_pass = 0
    try:
        if res.status_code == 200:
            json.loads(res.text)
            if int(res.headers['X-Rate-Limit-Remaining']) < 3:
                wait_time = int(res.headers['X-Rate-Limit-Reset']) - time.mktime(datetime.now().timetuple())
                time.sleep(wait_time + random.randint(1, 60))
        else:
            if res.status_code == 401:
                flag_pass = 1
            elif res.status_code == 403:
                flag_pass = 1
            elif res.status_code == 404:
                flag_pass = 1
    except:
        flag_pass = 1
    return flag_pass

#ツイートフィルター
def tweet_filter(tweet):
    text_filter = tweet['text']
    if len(tweet['entities']['urls']) != 0:#URL
        for url_list in tweet['entities']['urls']:
            text_filter = text_filter.replace(url_list['url'],"URLURL")
    if 'media' in tweet['entities']:#メディア
        for media_url_list in tweet['entities']['media']:
            text_filter = text_filter.replace(media_url_list['url'],"MEIDAURLMEDIAURL")
    if len(tweet['entities']['user_mentions']) != 0:#メンション
        for mention_list in tweet['entities']['user_mentions']:
            text_filter = text_filter.replace("@"+mention_list['screen_name'],"@@")
    if len(tweet['entities']['hashtags']) != 0:#ハッシュタグ
        for hash_list in tweet['entities']['hashtags']:
            text_filter = text_filter.replace("#"+hash_list['text'],"##"+hash_list['text'])
    if len(tweet['entities']['symbols']) != 0:#シンボル
        for symbol_list in tweet['entities']['symbols']:
            text_filter = text_filter.replace("$"+symbol_list['text'],"$$"+symbol_list['text'])
    return text_filter

def tweet_des_filter(tweet):
    des_filter = tweet['user']['description']
    if len(tweet['user']['entities']['description']['urls']) != 0:
        for url_list in tweet['user']['entities']['description']['urls']:
            des_filter = des_filter.replace(url_list['url'],"URLURL")
    return des_filter

if __name__ == '__main__':

    year = YEAR
    count = 0
    count_pass = 0
    count_dict = {}
    for month in range(FMONTH, LMONTH + 1): 
        with open(READ_DIR+str(year)+str(month).zfill(2)+".json","r") as fread:
            read_json = json.load(fread)
        for ym, read_tweet_list in read_json.items():
            user_tweet_dict = {}
            for read_tweet_dict in read_tweet_list:
                count += 1
                print(count)
                user_id = read_tweet_dict['user']['id']
                params = {'user_id':user_id, 'count':200}

                user_tweet_list = []
                while(1):
                    try:
                        res = session.get(url, params = params)
                        flag_pass = check_res(res)
                        if flag_pass == 1:
                            break
                        get_tweet_list = json.loads(res.text)
                        if (len(get_tweet_list) == 0) or (len(user_tweet_list) >= GET_NUM_TWEET):
                            break
                        else:
                            for tweet_dict in get_tweet_list:
                                t_dict = {}
                                t_dict['id'] = tweet_dict['id']
                                t_dict['text'] = tweet_dict['text']
                                t_dict['user_mentions'] = tweet_dict['entities']['user_mentions']
                                t_dict['user_id'] = tweet_dict['user']['id_str']
                                t_dict['retweet_count'] = tweet_dict['retweet_count']
                                t_dict['favorite_count'] = tweet_dict['favorite_count']
                                t_dict['created_at_ja'] = utc2jtime(tweet_dict['created_at'])
                                t_dict['text_filter'] = tweet_filter(tweet_dict)
                                t_dict['collect_datetime'] = datetime.now().strftime("%Y%m%d%H%M%S")
                                if 'retweeted_status' in tweet_dict:
                                    rt_dict ={}
                                    rt_dict['id'] = tweet_dict['retweeted_status']['id']
                                    rt_dict['text'] = tweet_dict['retweeted_status']['text']
                                    rt_dict['user_mentions'] = tweet_dict['retweeted_status']['entities']['user_mentions']
                                    rt_dict['user_id'] = tweet_dict['retweeted_status']['user']['id_str']
                                    rt_dict['retweet_count'] = tweet_dict['retweeted_status']['retweet_count']
                                    rt_dict['favorite_count'] = tweet_dict['retweeted_status']['favorite_count']
                                    rt_dict['created_at_ja'] = utc2jtime(tweet_dict['retweeted_status']['created_at'])
                                    rt_dict['text_filter'] = tweet_filter(tweet_dict['retweeted_status'])
                                    t_dict['retweeted_status'] = rt_dict
                                user_tweet_list.append(t_dict)
                            tweet_dict = user_tweet_list[-1]
                            params['max_id'] = tweet_dict['id'] - 1

                    except Exception as e:
                        flag_pass = 1
                    
                #ツイートが取得できないユーザは削除
                if flag_pass == 1:
                    count_pass += 1
                    continue
                    
                #ツイート数の統一
                if len(user_tweet_list) > GET_NUM_TWEET:
                    del user_tweet_list[GET_NUM_TWEET:]
                print(len(user_tweet_list))
                user_tweet_dict[user_id] = user_tweet_list        
            count_dict[ym] = len(list(user_tweet_dict))

            with open(WRITE_DIR+str(ym)+".json","w") as fwrite:
                write_dict = {}
                write_dict[ym] = user_tweet_dict
                json.dump(write_dict, fwrite, indent = 4, ensure_ascii = False)
            
        with open(WRITE_INFO_FILE,"w") as fwrite:
            count_total = 0
            for ym in list(count_dict):
                fwrite.write(str(ym)+"\t"+str(count_dict[ym])+"\n")
                count_total += count_dict[ym]
            fwrite.write("total\t"+str(count_total)+"\n")
            fwrite.write("pass\t"+str(count_pass)+"\n")
