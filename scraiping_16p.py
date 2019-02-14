#-*-coding:utf-8-*-
#Twitterの"#16Personalities"の検索結果のツイートのdata-idを取得

import urllib.request
from bs4 import BeautifulSoup
import random
import time
import os

WRITE_DIR = "../Data/01.16pid/"
if os.path.exists(WRITE_DIR) == False:
    os.makedirs(WRITE_DIR)
WRITE_FILE_PREFIX = "scraiping_"

year = 2018
firstmonth = 7
lastmonth = 9
lang = "ja"

#urlからsoupの作成
def makesoup(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup

#soup(TwitterTL)からdataidのリストを出力する関数
def dataid(soup):
    dataidlist = []
    for div in soup.find_all('div'):
        if isinstance(div.get('data-id'), str) == True:
            dataidlist.append(div.get('data-id'))
    return dataidlist

#soup(TwitterTL)からurlを取得する関数
def nexturl(soup):
    for a in soup.find_all('a'):
        temp = ""
        if isinstance(a.get('href'), str) == True:
            temp = a.get('href')
            if ((temp.find("16Personalities") != -1) & (temp.find("next_cursor") != -1)):
                url = "https://mobile.twitter.com"+temp
                return url

#月の最終日を求める関数
def ym2lastday(year, month):
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        lastday = 31
    elif month == 4 or month == 6 or month == 9 or month == 11:
        lastday = 30
    elif month == 2:
        if year % 4 == 0:
            lastday = 29   
        else:
            lastday = 28
    return lastday

#main関数
def bsoup(write_file_prefix, year, first_month, last_month, lang):

    for month in range(first_month, lastmonth + 1):#月毎の繰り返し
        writefile = write_file_prefix+str(year)+str(month).zfill(2)+".txt"
        with open(writefile, "w") as fwrite:
            lastday = ym2lastday(year, month)
            for day in range(1, lastday + 1):#日付毎の繰り返し
                starthourlist = ["00", "06", "12", "18"]
                lasthourlist = ["05", "11", "17", "23"]
                for hour in range(4):#時間毎の繰り返し
                    url = "https://mobile.twitter.com/search?q=%2316Personalities%20lang%3Aja%20since%3A2017-01-01_00:00:00_JST%20until%3A2017-01-01_23:59:59_JST&src=typed_query&f=live"
                    url = url[:64]+str(lang)+url[66:77]+str(year)+url[81:82]+str(month).zfill(2)+url[84:85]+str(day).zfill(2)+url[87:88]+starthourlist[hour]+url[90:111]+str(year)+url[115:116]+str(month).zfill(2)+url[118:119]+str(day).zfill(2)+url[121:122]+lasthourlist[hour]+url[124:]
                    print(url)
                    while True:#URLの繰り返し
                        try:
                            soup = makesoup(url)
                            iddatalist = dataid(soup)
                            for iddata in iddatalist:
                                fwrite.write(str(iddata)+"\n")
                            url = nexturl(soup)
                            time.sleep(random.randint(1,5))
                        except:
                            break
                time.sleep(random.randint(10,30))
            time.sleep(random.randint(10,30))
        
if __name__ == '__main__':

    bsoup(WRITE_DIR+WRITE_FILE_PREFIX, year, firstmonth, lastmonth, lang)
