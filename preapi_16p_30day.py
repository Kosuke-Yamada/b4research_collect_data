import json
from requests_oauthlib import OAuth1Session
from config import config03
import os
from time import sleep

WRITE_DIR = "../DATA/01.16P_ID/"
if os.path.exists(WRITE_DIR) == False:
    os.mkdir(WRITE_DIR)

CK = config03.CK
CS = config03.CS
AT = config03.AT
AS = config03.AS
session = OAuth1Session(CK, CS, AT, AS)
url = "https://api.twitter.com/1.1/tweets/search/30day/conf3.json"
word = "#16personalities lang:ja"

#日付をデータの一番最近のファイルチェックして！！！！！
fyear = 2019
fmonth = 1
fday = 16
fhour = 0
fmin = 0
lyear = 2019
lmonth = 1
lday = 18
lhour = 23
lmin = 43

def Enm2Jam(enmonth):
    monthdict = {'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':'5','Jun':'6','Jul':'7','Aug':'8','Sep':'9','Oct':'10','Nov':'11','Dec':'12'}
    return monthdict[enmonth]

if __name__ == '__main__':

    count = 0
    params = {'query':word,
              'maxResults':100,
              'fromDate':str(fyear)+str(fmonth).zfill(2)+str(fday).zfill(2)+str(fhour).zfill(2)+str(fmin).zfill(2),
              'toDate':str(lyear)+str(lmonth).zfill(2)+str(lday).zfill(2)+str(lhour).zfill(2)+str(lmin).zfill(2)}

    loop = 0
    while(loop < 100):
        res = session.get(url, params = params)
        text_list = json.loads(res.text)
        write_text = WRITE_DIR + str(lyear)+str(lmonth).zfill(2)+str(lday).zfill(2)+str(lhour).zfill(2)+str(lmin).zfill(2)+".txt"
        with open(write_text,"w") as fwrite:
            for user_dict in text_list['results']:
                fwrite.write(user_dict['id_str']+"\n")
                created_at_list = user_dict['created_at'].split()
                print(user_dict['id_str'])
                count += 1
        print(count)
        print(created_at_list)
        if count % 100 != 0:
            break
        lyear = created_at_list[5]
        lmonth = Enm2Jam(created_at_list[1])
        lday = created_at_list[2]
        lhour = int(created_at_list[3][0:2])
        lmin = int(created_at_list[3][3:5])
        if lmin == 0:
            lmin = 59
            lhour -= 1
        else:
            lmin = lmin - 1
        print(lmin)
        params = {'query':word,
                  'maxResults':100,
                  'fromDate':str(fyear)+str(fmonth).zfill(2)+str(fday).zfill(2)+str(fhour).zfill(2)+str(fmin).zfill(2),
                  'toDate':str(lyear)+str(lmonth).zfill(2)+str(lday).zfill(2)+str(lhour).zfill(2)+str(lmin).zfill(2)}
        loop += 1
        sleep(2)
