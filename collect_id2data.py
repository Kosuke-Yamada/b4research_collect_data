#-*-coding:utf-8-*-

from requests_oauthlib import OAuth1Session
import json
import os, sys
import time, calendar
import random
from config import config01
from datetime import datetime

CK = config01.CK
CS = config01.CS
AT = config01.AT
AS = config01.AS
session = OAuth1Session(CK, CS, AT, AS)
url = 'https://api.twitter.com/1.1/statuses/show.json'

num = 13#numによって，データ収集するディレクトリを分ける仕様

READ_DIR = "../DATA/01.16P_ID/ID"+str(num).zfill(2)+"/"
WRITE_DIR = "../DATA/02.COLLECT_16P_DATA/"
if os.path.exists(WRITE_DIR) == False:
    os.mkdir(WRITE_DIR)
WRITE_INFO_FILE = WRITE_DIR+"info_"+str(num).zfill(2)+".txt"

#日本時間に変更
def utc2jtime(created_at):
    time_utc = time.strptime(created_at, '%a %b %d %H:%M:%S +0000 %Y')
    unix_time = calendar.timegm(time_utc)
    time_local = time.localtime(unix_time)
    jtime = time.strftime("%Y%m%d%H%M%S", time_local)
    return jtime

#resをチェックして，取得可能まで待つ
def check_res(res):
    flag_pass = 0
    try:
        if res.status_code == 200:
            json.loads(res.text)
            print(res.headers['X-Rate-Limit-Remaining'])
            if int(res.headers['X-Rate-Limit-Remaining']) < 3:
                wait_time = int(res.headers['X-Rate-Limit-Reset']) - time.mktime(datetime.now().timetuple())
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

if __name__ == '__main__':

    id_list = []
    read_file_list = os.listdir(READ_DIR)
    for read_file in read_file_list:
        with open(READ_DIR+read_file, "r") as fread:
            id_list += fread.read().split("\n")[:-1]

    ym_tweet_dict = {}
    count_pass = 0
    for tweet_id in id_list:
        res = session.get(url, params = {'id':tweet_id})
        flag_pass = check_res(res)
        if flag_pass == 1:
            count_pass += 1
            continue
        tweet_dict = json.loads(res.text)

        tweet_dict['created_at_ja'] = utc2jtime(tweet_dict['created_at'])
        tweet_dict['user']['created_at_ja'] = utc2jtime(tweet_dict['user']['created_at'])
        tweet_dict['collect_datetime'] = datetime.now().strftime("%Y%m%d%H%M%S")

        ym = tweet_dict['created_at_ja'][:6]
        if not ym in ym_tweet_dict:
            ym_tweet_dict[ym] = []
        ym_tweet_dict[ym].append(tweet_dict)

    count_total = 0
    for ym in list(ym_tweet_dict):
        count_total += len(ym_tweet_dict[ym])
        with open(WRITE_DIR+str(ym)+"_"+str(num).zfill(2)+".json","w") as fwrite:
            write_dict = {}
            write_dict[str(ym)] = ym_tweet_dict[ym]
            json.dump(write_dict, fwrite, indent = 4, ensure_ascii = False)
    
    with open(WRITE_INFO_FILE,"w") as fwrite:
        for ym in list(ym_tweet_dict):
            fwrite.write(str(ym)+"\t"+str(len(ym_tweet_dict[ym]))+"\n")
        fwrite.write("total\t"+str(count_total)+"\n")
        fwrite.write("pass\t"+str(count_pass)+"\n")
