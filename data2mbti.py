#-*-coding:utf-8-*-

import json
import os, sys
import re
from collections import defaultdict

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import re
import emoji
import mojimoji

#読み込みディレクトリ，ファイル
READ_DIR = "../DATA/02.16P_DATA/"

#書き込みディレクトリ, ファイル                                        
WRITE_DIR = "../DATA/03.16P_MBTI/"
if os.path.exists(WRITE_DIR) == False:
    os.mkdir(WRITE_DIR)
WRITE_INFO_FILE = WRITE_DIR+"info_old.txt"#バージョン管理に気をつけて
WRITE_DABURI_FILE = WRITE_DIR+"daburi_old.json"#バージョン管理に気をつけて

def mbti_unity(mbti):
    if mbti == u"建築家":
        mbti = u"INTJ"
    elif mbti == u"論理学者":
        mbti = u"INTP"
    elif mbti == u"指揮官":
        mbti = u"ENTJ"
    elif mbti == u"討論者":
        mbti = u"ENTP"
    elif mbti == u"提唱者":
        mbti = u"INFJ"
    elif mbti == u"仲介者":
        mbti = u"INFP"
    elif mbti == u"主人公":
        mbti = u"ENFJ"
    elif mbti == u"広報運動家":
        mbti = u"ENFP"
    elif mbti == u"管理者":
        mbti = u"ISTJ"
    elif mbti == u"擁護者":
        mbti = u"ISFJ"
    elif mbti == u"幹部":
        mbti = u"ESTJ"
    elif mbti == u"領事官":
        mbti = u"ESFJ"
    elif mbti == u"巨匠":
        mbti = u"ISTP"
    elif mbti == u"冒険家":
        mbti = u"ISFP"
    elif mbti == u"起業家":
        mbti = u"ESTP"
    elif mbti == u"エンターテイナー":
        mbti = u"ESFP"
    return mbti

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

    ym_tweet_dict = {}
    for year in range(2017, 2019):
        if year == 2017:
            lmonth = 12
        else:
            lmonth = 9
        for month in range(1, lmonth + 1):
            with open(READ_DIR+str(year)+str(month).zfill(2)+".json","r") as fread:
                read_json = json.load(fread)
            for ym, read_tweet_list in read_json.items():
                ym_tweet_dict[ym] = read_tweet_list

    user_daburi_dict = defaultdict(list)
    user_id_list = []
    count_daburi = 0
    count_not_ja = 0
    count_no_mbti = 0
    mbti_words = u"建築家|論理学者|指揮官|討論者|提唱者|仲介者|主人公|広報運動家|管理者|擁護者|幹部|領事官|巨匠|冒険家|起業家|エンターテイナー|INTJ|INTP|INFJ|INFP|ISTJ|ISTP|ISFJ|ISFP|ENTJ|ENTP|ENFJ|ENFP|ESTJ|ESTP|ESFJ|ESFP"
    for ym in list(ym_tweet_dict):
        for tweet_dict in ym_tweet_dict[ym][:]:

            #ユーザの言語チェック
            if tweet_dict['user']['lang'] != "ja":
                count_not_ja += 1
                ym_tweet_dict[ym].remove(tweet_dict)
                continue

            #性格取得チェック
            mbti = re.search(mbti_words,tweet_dict['text'])
            if mbti is None:
                count_no_mbti += 1
                ym_tweet_dict[ym].remove(tweet_dict)
                continue
            mbti = mbti_unity(mbti.group())
            tweet_dict['mbti'] = mbti
            tweet_dict['mbti_EI'] = [1 if mbti[0] == "E" else 0][0]
            tweet_dict['mbti_NS'] = [1 if mbti[1] == "N" else 0][0]
            tweet_dict['mbti_TF'] = [1 if mbti[2] == "T" else 0][0]
            tweet_dict['mbti_JP'] = [1 if mbti[3] == "J" else 0][0]
            
            #ダブりチェック
            user_daburi_dict[tweet_dict['user']['id_str']].append((tweet_dict['mbti'],tweet_dict['created_at_ja'][:8]))
            if tweet_dict['user']['id_str'] in user_id_list:
                count_daburi += 1
                ym_tweet_dict[ym].remove(tweet_dict)
                continue
            else:
                user_id_list.append(tweet_dict['user']['id_str'])

            #キーの追加
            tweet_dict['user']['description_filter']  = tweet_des_filter(tweet_dict)
            tweet_dict['user']['name_len'] = len(tweet_dict['user']['name'])
            tweet_dict['user']['name_number_count'] = len(re.findall('[0-9]', tweet_dict['user']['name']))
            tweet_dict['user']['name_alphabet_count'] = len(re.findall('[a-zA-Z]', tweet_dict['user']['name']))
            tweet_dict['user']['name_hiragana_count'] = len(re.findall('[ぁ-ん]', tweet_dict['user']['name']))
            tweet_dict['user']['name_katakana_count'] = len(re.findall('[ァ-ヶ]', tweet_dict['user']['name']))
            tweet_dict['user']['name_kanji_count'] = len(re.findall('[一-龥々]', tweet_dict['user']['name']))
            tweet_dict['user']['name_symbol_count'] = len(re.findall('[!-/:-@¥\[-`{-~\]+$｢｣､｡･]', mojimoji.zen_to_han(tweet_dict['user']['name'])))
            tweet_dict['user']['name_emoji_count'] = len([char for char in tweet_dict['user']['name'] if char in emoji.UNICODE_EMOJI])
            
            tweet_dict['user']['screen_name_len'] = len(tweet_dict['user']['screen_name'])
            tweet_dict['user']['screen_name_number_count'] = len(re.findall('[0-9]', tweet_dict['user']['screen_name']))
            tweet_dict['user']['screen_name_alphabet_count'] = len(re.findall('[a-zA-Z]', tweet_dict['user']['screen_name']))
            tweet_dict['user']['screen_name_under_bar_count'] = len(re.findall('_', tweet_dict['user']['screen_name']))
            
            tweet_dict['user']['location_len'] = len(tweet_dict['user']['location'])
            
            tweet_dict['user']['description_word_count'] = len(tweet_text2mecab(tweet_dict['user']['description_filter']))
            tweet_dict['user']['description_char_count'] = len(tweet_dict['user']['description'])
            tweet_dict['user']['description_entities_count'] = len(tweet_dict['user']['entities']['description']['urls'])
            tweet_dict['user']['description_number_count'] = len(re.findall('[0-9]', tweet_dict['user']['description']))
            tweet_dict['user']['description_alphabet_count'] = len(re.findall('[a-zA-Z]', tweet_dict['user']['description']))
            tweet_dict['user']['description_hiragana_count'] = len(re.findall('[ぁ-ん]', tweet_dict['user']['description']))
            tweet_dict['user']['description_katakana_count'] = len(re.findall('[ァ-ヶ]', tweet_dict['user']['description']))
            tweet_dict['user']['description_kanji_count'] = len(re.findall('[一-龥々]', tweet_dict['user']['description']))
            tweet_dict['user']['description_symbol_count'] = len(re.findall('[!-/:-@¥\[-`{-~\]+$｢｣､｡･]', mojimoji.zen_to_han(tweet_dict['user']['description'])))
            tweet_dict['user']['description_emoji_count'] = len([char for char in tweet_dict['user']['description'] if char in emoji.UNICODE_EMOJI])
            tweet_dict['user']['description_space_count'] = len(re.findall('\s', tweet_dict['user']['description']))

            tweet_dict['user']['url_flag'] = [0 if tweet_dict['user']['url'] is None else 1][0]

            ff_ratio = [float(tweet_dict['user']['friends_count'] / tweet_dict['user']['followers_count']) if tweet_dict['user']['followers_count'] != 0 else float(0)][0]
            tweet_dict['user']['friends_followers_ratio'] = float(Decimal(str(ff_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            fs_ratio = [float(tweet_dict['user']['favourites_count'] / tweet_dict['user']['statuses_count']) if tweet_dict['user']['statuses_count'] != 0 else float(0)][0]
            tweet_dict['user']['favourites_statuses_ratio'] = float(Decimal(str(fs_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            
            collect_datetime = datetime.strptime(tweet_dict['collect_datetime'],"%Y%m%d%H%M%S")
            user_created_at = datetime.strptime(tweet_dict['user']['created_at_ja'],"%Y%m%d%H%M%S")
            tweet_dict['user']['year_since_created_at'] = collect_datetime.year - user_created_at.year + 1
            tweet_dict['user']['month_since_created_at'] = (collect_datetime.year - user_created_at.year) * 12 + collect_datetime.month - user_created_at.month + 1
            tweet_dict['user']['day_since_created_at'] = (collect_datetime - user_created_at).days + 1
            
            fy_ratio = float(tweet_dict['user']['favourites_count'] / tweet_dict['user']['year_since_created_at'])
            tweet_dict['user']['favorurites_year_ratio'] = float(Decimal(str(fy_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            sy_ratio = float(tweet_dict['user']['statuses_count'] / tweet_dict['user']['year_since_created_at'])
            tweet_dict['user']['statuses_year_ratio'] = float(Decimal(str(sy_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            fm_ratio = float(tweet_dict['user']['favourites_count'] / tweet_dict['user']['month_since_created_at'])
            tweet_dict['user']['favorurites_month_ratio'] = float(Decimal(str(fm_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            sm_ratio = float(tweet_dict['user']['statuses_count'] / tweet_dict['user']['month_since_created_at'])
            tweet_dict['user']['statuses_month_ratio'] = float(Decimal(str(sm_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            fd_ratio = float(tweet_dict['user']['favourites_count'] / tweet_dict['user']['day_since_created_at'])
            tweet_dict['user']['favorurites_day_ratio'] = float(Decimal(str(fd_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            sd_ratio = float(tweet_dict['user']['statuses_count'] / tweet_dict['user']['day_since_created_at'])
            tweet_dict['user']['statuses_day_ratio'] = float(Decimal(str(sd_ratio)).quantize(Decimal('0.001'), rounding = ROUND_HALF_UP))
            
    count_total = 0
    for ym in list(ym_tweet_dict):
        count_total += len(ym_tweet_dict[ym])
        with open(WRITE_DIR+str(ym)+".json","w") as fwrite:
            write_dict = {}
            write_dict[str(ym)] = ym_tweet_dict[ym]
            json.dump(write_dict, fwrite, indent = 4, ensure_ascii = False)

    with open(WRITE_INFO_FILE,"w") as fwrite:
        for ym in list(ym_tweet_dict):
            fwrite.write(str(ym)+"\t"+str(len(ym_tweet_dict[ym]))+"\n")
        fwrite.write("total\t"+str(count_total)+"\n")
        fwrite.write("not_ja\t"+str(count_not_ja)+"\n")
        fwrite.write("no_mbti\t"+str(count_no_mbti)+"\n")
        fwrite.write("daburi\t"+str(count_daburi)+"\n")

    for user_id in list(user_daburi_dict):
        if len(user_daburi_dict[user_id]) == 1:
            user_daburi_dict.pop(user_id)

    with open(WRITE_DABURI_FILE,"w") as fdaburi:
        json.dump(user_daburi_dict, fdaburi, indent = 4, ensure_ascii = False)
