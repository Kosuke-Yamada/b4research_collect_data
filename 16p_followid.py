#-*- coding:utf-8 -*-

from requests_oauthlib import OAuth1Session
import json
import os
from config import config03
import time, datetime, random

CK = config03.CK
CS = config03.CS
AT = config03.AT
AS = config03.AS
session = OAuth1Session(CK, CS, AT, AS)
#URL注意
url = 'https://api.twitter.com/1.1/followers/ids.json'
#url = 'https://api.twitter.com/1.1/friends/ids.json'

year = 2018
fmonth = 12
lmonth = 12

#読み込みディレクトリ，ファイル
READ_DIR = "../DATA/03.16P_MBTI/"
#書き込みディレクトリ, ファイル
WRITE_DIR = "../DATA/05.16P_FOLLOWER/"############
if os.path.exists(WRITE_DIR) == False:
    os.mkdir(WRITE_DIR)
WRITE_INFO_FILE = WRITE_DIR+"info_"+str(year)+str(fmonth).zfill(2)+".txt"

#レスポンスチェック
def check_res(res):
    flag_pass = 0
    try:
        if res.status_code == 200:
            json.loads(res.text)
            print(res.headers['X-Rate-Limit-Remaining'])
            if int(res.headers['X-Rate-Limit-Remaining']) < 3:
                wait_time = int(res.headers['X-Rate-Limit-Reset']) - time.mktime(datetime.datetime.now().timetuple())
                time.sleep(wait_time + random.randint(1, 5))
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
    
if __name__ == "__main__":

    read_ym_tweet_dict = {}
    for month in range(fmonth, lmonth + 1):
        with open(READ_DIR+str(year)+str(month).zfill(2)+".json","r") as fread:
            read_json = json.load(fread)
        for ym, read_tweet_list in read_json.items():
            read_ym_tweet_dict[ym] = read_tweet_list

    count_pass = 0
    ym_tweet_dict = {}
    for ym in list(read_ym_tweet_dict):
        user_follow_dict = {}
        for read_tweet_dict in read_ym_tweet_dict[ym]:
            user_id = read_tweet_dict['user']['id']
            cursor = -1
            print(user_id)
            user_follow_list = []
            while(1):
                try:
                    res = session.get(url, params = {'user_id':user_id, 'count':5000, 'cursor':cursor})
                    flag_pass = check_res(res)
                    if flag_pass == 1:
                        break
                    res_text = json.loads(res.text)
                    user_follow_list += res_text['ids']
                    cursor = res_text['next_cursor']
                    if cursor == 0:
                        break
                except:
                    time.sleep(random.randint(1,9))
                
            if flag_pass == 1:
                count_pass += 1
                continue
            print(user_id)
            user_follow_dict[user_id] = user_follow_list
        ym_tweet_dict[ym] = user_follow_dict

    count_total = 0
    for ym in list(ym_tweet_dict):
        count_total += len(list(ym_tweet_dict[ym]))
        with open(WRITE_DIR+str(ym)+".json","w") as fwrite:
            write_dict = {}
            write_dict[ym] = ym_tweet_dict[ym]
            json.dump(write_dict, fwrite, indent = 4, ensure_ascii = False)
            
    with open(WRITE_INFO_FILE,"w") as fwrite:
        for ym in list(ym_tweet_dict):
            fwrite.write(str(ym)+"\t"+str(len(list(ym_tweet_dict[ym])))+"\n")
        fwrite.write("total\t"+str(count_total)+"\n")
        fwrite.write("pass\t"+str(count_pass)+"\n")
                                                                                                                            
                                                                                                                            
