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
import MeCab
from config import config01

CK = config01.CK
CS = config01.CS
AT = config01.AT
AS = config01.AS
session = OAuth1Session(CK, CS, AT, AS)
url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

YEAR = 2018
FMONTH = 12
LMONTH = 12

GET_NUM_TWEET = 3200

#読み込みディレクトリ，ファイル
READ_DIR = "../DATA/03.16P_MBTI/"

#書き込みディレクトリ, ファイル                                        
WRITE_DIR = "./201812/"#DATA/04.16P_TWEETTEXT/"
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

def tweet_text2mecab(tweet_text):
    tweet_text = str(tweet_text)
    chasen = MeCab.Tagger("-Ochasen")
    chasen_list = chasen.parse(tweet_text)
    chasen_list = chasen_list.split("\n")
    tweet_word_list = []
    for cha_list in chasen_list:
        cha_list = cha_list.split("\t")
        if len(cha_list) > 2:
            tweet_word_list.append(cha_list[2])
    return tweet_word_list

def tweet_des_filter(tweet):
    des_filter = tweet['user']['description']
    if len(tweet['user']['entities']['description']['urls']) != 0:
        for url_list in tweet['user']['entities']['description']['urls']:
            des_filter = des_filter.replace(url_list['url'],"URLURL")
    return des_filter

if __name__ == '__main__':

    year = YEAR
    read_ym_tweet_dict = {}
    for month in range(FMONTH, LMONTH + 1): 
        with open(READ_DIR+str(year)+str(month).zfill(2)+".json","r") as fread:
            read_json = json.load(fread)
        for ym, read_tweet_list in read_json.items():
            read_ym_tweet_dict[ym] = read_tweet_list

    count_pass = 0
    #count_few_num = 0
    ym_tweet_dict = {}
    count = 0
    for ym in list(read_ym_tweet_dict):
        user_tweet_dict = {}
        for read_tweet_dict in read_ym_tweet_dict[ym]:
            count += 1
            print(count)
            user_id = read_tweet_dict['user']['id']
            max_id = read_tweet_dict['id'] - 1

            user_tweet_list = []
            while(1):
                try:
                    res = session.get(url, params = {'user_id':user_id, 'max_id':max_id, 'count':200, 'include_rts':False})
                    flag_pass = check_res(res)
                    if flag_pass == 1:
                        break

                    get_tweet_list = json.loads(res.text)
                    for tweet_dict in get_tweet_list:
                        tweet_dict['created_at_ja'] = utc2jtime(tweet_dict['created_at'])
                        tweet_dict['user']['created_at_ja'] = utc2jtime(tweet_dict['user']['created_at'])
                        tweet_dict['text_filter'] = tweet_filter(tweet_dict)
                        tweet_dict['user']['description_filter']  = tweet_des_filter(tweet_dict)
                        tweet_dict['collect_datetime'] = datetime.now().strftime("%Y%m%d%H%M%S")
                        tweet_dict['text_word_count'] = len(tweet_text2mecab(tweet_dict['text_filter']))
                        tweet_dict['text_char_count'] = len(tweet_dict['text'])
                        tweet_dict['text_hashtags_count'] = len(tweet_dict['entities']['hashtags'])
                        tweet_dict['text_symbols_count'] = len(tweet_dict['entities']['symbols'])
                        tweet_dict['text_user_mentions_count'] = len(tweet_dict['entities']['user_mentions'])
                        tweet_dict['text_urls_count'] = len(tweet_dict['entities']['urls'])
                        tweet_dict['text_media_count'] = [len(tweet_dict['entities']['media']) if 'media' in tweet_dict['entities'] else 0][0]
                        tweet_dict['text_number_count'] = len(re.findall('[0-9]', tweet_dict['text']))
                        tweet_dict['text_alphabet_count'] = len(re.findall('[a-zA-Z]', tweet_dict['text']))
                        tweet_dict['text_hiragana_count'] = len(re.findall('[ぁ-ん]', tweet_dict['text']))
                        tweet_dict['text_katakana_count'] = len(re.findall('[ァ-ヶ]', tweet_dict['text']))
                        tweet_dict['text_kanji_count'] = len(re.findall('[一-龥々]', tweet_dict['text']))
                        tweet_dict['text_symbol_count'] = len(re.findall('[!-/:-@¥\[-`{-~\]+$｢｣､｡･]', mojimoji.zen_to_han(tweet_dict['text'])))
                        tweet_dict['text_emoji_count'] = len([char for char in tweet_dict['text'] if char in emoji.UNICODE_EMOJI])
                        tweet_dict['text_space_count'] = len(re.findall('\s', tweet_dict['text']))

                    user_tweet_list += get_tweet_list
                    if (len(get_tweet_list) == 0) or (len(user_tweet_list) >= GET_NUM_TWEET):
                        break
                    else:
                        tweet_dict = get_tweet_list[-1]
                        max_id = tweet_dict['id'] - 1
                except:
                    continue
                    
            #ツイートが取得できないユーザは削除
            if flag_pass == 1:
                count_pass += 1
                continue
                    
            #ツイート数の少ないユーザは削除
            #if len(user_tweet_list) < GET_NUM_TWEET:
            #    count_few_num += 1
            #    continue

            #ツイート数の統一
            if len(user_tweet_list) > GET_NUM_TWEET:
                del user_tweet_list[GET_NUM_TWEET:]

            user_tweet_dict[user_id] = user_tweet_list        
        ym_tweet_dict[ym] = user_tweet_dict
        
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
        #fwrite.write("few_num\t"+str(count_few_num)+"\n")


