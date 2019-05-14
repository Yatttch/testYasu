
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
gDf = pd.DataFrame(index=[],columns=["title","headline"]) #空のデータフレーム作成
#↓ここで，１行だけ追加，あとはこの１行を使い回し，１行づつ書き出す
gDf = gDf.append(pd.DataFrame(index=[0],columns=["title","headline"]))

#NewsNo = 1
#df = df.append(pd.DataFrame([["aaa","bbb"]],index=[NewsNo],columns=["title","headline"]))
#print(df)

def headLine_urlopen_lxml(address,nest_no):
    global gDf
    #html = urllib.request.urlopen(address)
    response = requests.get(address)
 
    # get first all html source
    #soup = BeautifulSoup(html, "html.parser") #bs4
 
    # extract main body which tag is div
    #main_body = soup.find("div", {"id": "main"}) #bs4
    content = lxml.html.fromstring(response.content)
    main_div1 = content.body.cssselect("div#main")
    main_div2 = content.body.cssselect("#main") #上と同じ
 
    # extract list items in main_body which class name equals to "topics"
    #hbody = content.xpath("//div[@class=\"headlineTxt\"]/p[@class=\"hbody\"]")

    hbody = content.body.cssselect("div.headlineTxt > p.hbody")
    out_str = ""
    href_str=""
 
    # join each list item's string
    if type(None) != type(hbody[0].text):
        out_str += (hbody[0].text + "\n")
        print(out_str) #■■■ ヘッドライン書き出し
        gDf.iat[0,1] = out_str #２列目に出力
        #print(df)
        #↓★★★書き出しはここだけ
        gDf.to_csv("aaa.csv",mode="a",encoding="cp932",index=False,header=False)
        gDf.iat[0,0]=gDf.iat[0,1]="" #クリア


def yahooTop_urlopen_lxml(address,nest_no):

    gNewsNo = 0
    response = requests.get("https://www.yahoo.co.jp/") #これは行ける
    response = requests.get(address)

    # extract main body which tag is div
    #main_body = soup.find("div", {"id": "main"}) #bs4
    content = lxml.html.fromstring(response.content)

    # extract list items in main_body which class name equals to "topics"
    #topics = main_body.find("ul", {"class": "topics"}) #bs4 #<ul class="topics">
    #topics = content.xpath("//ul[@class=\"topics\"]") #xpath
    topics = content.body.cssselect("ul.topics")

    a1 = topics[0].cssselect("li a")
    a2 = content.cssselect("li a")
    a3 = topics[0].xpath("//li//a") #←topicの下を探してくれない！

    out_str = ""
    href_str=""
    #contents_num = len(topics.contents)
#    contents_num = len(topics[0].cssselect("a"))

    #for a in topics[0].xpath("//li//a"): #liの子孫
    #↑■xpathだと、topicsの下だけを検索してくれない
    newsNo = 0
    for p in topics[0].cssselect("li p"): #liの子孫
        a = p.cssselect("a") #cssselectは、必ずlistオブジェクトを返す
        if type(None) != type(a[0].text):
            out_str = a[0].text
            #if out_str != "もっと見る":
            if p.get("class") != "more":
                out_str = str(newsNo) + "■"+out_str+"\n"
                print(out_str) #■■■ タイトル書き出し
                 #データフレームを１行追加
                gDf.iat[0,0] = out_str #１列目に出力
                #print(df)
                adrs = a[0].get("href") #OK
                nest_no += 1
                newsNo +=1
                headLine_urlopen_lxml(adrs,nest_no) #←この中で書き出し
                out_str = ""
            else:
                adress = topics[0].cssselect("li.topicsFt a")
                a = adress[0].get("href")
                r = requests.get(adress[0].get("href"))
                out_str = ""
                break
    #print(r.text)
    #「もっと見る」以下を最後のページまでクローリング
    pageNo = 1
    while(True):
        print("■■■ Page."+str(pageNo)+" ■■■\n")
        cont = lxml.html.fromstring(r.content)
        cont.make_links_absolute(r.url)#すべて絶対パスに変換
        lists = cont.body.cssselect("div.mainBox  ul.list")
        #for dt in lists[0].cssselect("dl.title > dt"):
        for listBox in lists[0].cssselect("li.ListBoxwrap"):
            dt = listBox.cssselect("dt")
            date = listBox.cssselect("time.date")
            if type(None) != type(dt[0].text):
                out_str = str(newsNo) +" - "+ date[0].text +"■"+dt[0].text +"\n"
                newsNo+=1
                try:
                    print(out_str)
                except UnicodeEncodeError:
                    print("catch UnicodeEncodeError - continued")
                    continue
                gDf.iat[0,0] = out_str #１列目に出力
                a = listBox.cssselect("a")
                if(len(a) >0):
                    headLine_urlopen_lxml(a[0].get("href"),nest_no) #←この中で書き出し
                else: #ヘッドラインがない場合は，ここで書き出し
                    gDf.to_csv("aaa.csv",mode="a",encoding="cp932",index=False,header=False)
                    gDf.iat[0,0]=gDf.iat[0,1]="" #クリア
        next = cont.body.cssselect("div.ftPager li.next > a")
        if(len(next)>0):
            nextPage = next[0].get("href")
            if(pageNo==0): #「0」 なら、page2から
                nextPage = "https://news.yahoo.co.jp/list/?p=10706"
                #headLine_urlopen_lxml("https://rdsig.yahoo.co.jp/list/?p=10708",0)
            if(nextPage != ""):
                r = requests.get(nextPage)
            pageNo+=1
        else:
            break


"""
        if "li" == topics:
            # join each list item's string
            for topic in topics.contents[i].a.contents:
                out_str += topic.string
            # remove if string contains "new"
            out_str = re.sub(r'new', '', out_str) #正規表現
            out_str = re.sub(r'写真', '', out_str) #正規表現
            if out_str != "もっと見る":
                out_str += "\n"
                print(out_str)
                adrs = topics.contents[i].a.attrs["href"] #OK
                nest_no += 1
                headLine_urlopen(adrs,nest_no)
                out_str = ""
"""

"""
#
#HTMLファイルを読み込んでBeautifulSoupオブジェクトを得る
#
f = urllib.request.urlopen("http://news.yahoo.co.jp/")
#with open("http://news.yahoo.co.jp/") as f:
soup = BeautifulSoup(f, "html.parser")
#find_all()メソッドでa要素のリストを取得して、個々のa要素に対して処理を行う
for p in soup.find_all("a"):
    print(p.get("href"),p.text)
"""


#
# crawring & scraiping sample
#
#import urllib2  # ← ■python2の書き方
import requests
import lxml.html
nest_no = 0

#crawling from Yahoo Top

yahooTop_urlopen_lxml("http://news.yahoo.co.jp/",nest_no)

