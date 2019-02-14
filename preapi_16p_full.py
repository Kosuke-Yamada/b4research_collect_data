import json
from requests_oauthlib import OAuth1Session
from config import config06
from time import sleep

WRITE_DIR = "../DATA/01.16P_ID/"

CK = config06.CK
CS = config06.CS
AT = config06.AT
AS = config06.AS
session = OAuth1Session(CK, CS, AT, AS)
url = "https://api.twitter.com/1.1/tweets/search/fullarchive/conf6.json"
word = "#16personalities lang:ja"

#日付をデータの一番最近のファイルチェックして！！！！！
year = 2015
lmonth = 6
lday = 13
lhour = 1
lmin = 26

def Enm2Jam(en_month):
    month_dict = {'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':'5','Jun':'6','Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}
    return month_dict[en_month]

if __name__ == '__main__':

    count = 0
    params = {'query':word,
              'maxResults':100,
              'toDate':str(year)+str(lmonth).zfill(2)+str(lday).zfill(2)+str(lhour).zfill(2)+str(lmin).zfill(2)}

    loop = 0
    while(loop < 100):
        res = session.get(url, params = params)
        text_list = json.loads(res.text)
        write_text = WRITE_DIR + str(year)+str(lmonth).zfill(2)+str(lday).zfill(2)+str(lhour).zfill(2)+str(lmin).zfill(2)+".txt"
        with open(write_text,"w") as fwrite:
            for user_dict in text_list['results']:
                fwrite.write(user_dict['id_str']+"\n")
                created_at_list = user_dict['created_at'].split()
                print(user_dict['id_str'])
                count += 1
        year = created_at_list[5]
        lmonth = Enm2Jam(created_at_list[1])
        lday = created_at_list[2]
        lhour = created_at_list[3][0:2]
        lmin = int(created_at_list[3][3:5])
        if lmin == 0:
            lmin = 59
        else:
            lmin = lmin - 1
        params = {'query':word,
                  'maxResults':100,
                  'toDate':str(year)+str(lmonth).zfill(2)+str(lday).zfill(2)+str(lhour).zfill(2)+str(lmin).zfill(2)}
        print(count)
        print(created_at_list)
        
        loop += 1
        sleep(1)
