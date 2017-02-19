# -*- coding: utf-8 -*-

import json
import re
import requests
import time
#import ssl
import ssl
#import urllib3
#urllib3.disable_warnings()

ssl._create_default_https_context = ssl._create_unverified_context
#20170218 cookies
headers ={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch, br',
    'Accept-Language':'zh-CN,zh;q=0.8,ja;q=0.6',
    'Connection':'keep-alive',
    'Host':'xueqiu.com',
    'Upgrade-Insecure-Requests':'1',
    'Cookie':'bid=2ad30f4bf838a5258fe0c301d664938f_iv2ejxb2; webp=0; s=5k11uulhiv; aliyungf_tc=AQAAAOmhfRWslQUAVWurr+Y1MJubqPnf; xq_a_token=a51e1cb6bc43db4588407c0b4b7e3fd9d26a3ee6; xq_a_token.sig=NXXGyNgVWvbxcgBguen6oRSElQ8; xq_r_token=06f71be1104f379fc9686b95a588ffd3cc1219d4; xq_r_token.sig=jyZd9J44KLaR46XaeSbAPTFBug8; xq_is_login=1; xq_is_login.sig=J3LxgPVPUzbBg3Kee_PquUfih7Q; u=7215631864; u.sig=dhzKaq-urVaJHHxbTk9-5iufO48; snbim_minify=true; __utmt=1; Hm_lvt_1db88642e346389874251b5a1eded6e3=1485348003,1486884062,1487397181,1487416080; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1487416096; __utma=1.1560667345.1478179949.1487397208.1487416096.46; __utmb=1.2.9.1487416098394; __utmc=1; __utmz=1.1478179949.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'            
}

def timestampToDate(timeStamp):
#    timeStamp = 1381419600  
    timeArray = time.localtime(int(timeStamp)/1000)  
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)  
#    otherStyletime == "2013-10-10 23:40:00" 
    return otherStyleTime

def json_write(json_text):
    with open('json/laomao.json','a',encoding='utf-8') as f:
        f.writelines(json_text + '\n')
        
def wenda_caiji():
    url = 'https://xueqiu.com/v4/statuses/user_timeline.json?user_id=6146070786&page={0}&type=4&count=2'
    proxies = {
        'http':'http://1:1@10.88.42.18:8080',
        'https':'http://1:1@10.88.42.18:8080' 
    }
#    print(url.format('1'))
    html = requests.get(url.format('1'),proxies=proxies,headers=headers)
    print(html)
#    html = requests.get(url.format('1'),proxies=proxies,verify=True)
    json_write(html.text)
#    print(html.json)
#    json_obj = json.loads(html.json())
#    maxpage = int(json_obj.get('maxpage'))
#    print(maxpage)
#    
#    for i in range(2): #maxpage-1):
#        time.sleep(1)
#        html = requests.get(url.format(str(i+2)),proxies=proxies)
#        json_write(html.json())

def readJson (jsonpath):
    job_type_lists = []
    with open(jsonpath,'r',encoding='utf-8') as f:
#        return f.read()
#        print(f)
        for each_line in f.readlines():
            try:
                json_obj = json.loads(each_line)
                job_type_lists.append(json_obj)
                #return json_obj
            except:
                pass
    return job_type_lists

def jsonToHtml():
    xueqiu_json_list = readJson('json/test.json')   
    
    out_f = open('output/index3.html','a',encoding='utf-8')
    total_num = 0.0
    money_list = []
    for xueqiu_json in xueqiu_json_list:
#        json_obj = json.loads(xueqiu_json)
        wenda_list = xueqiu_json.get('statuses')
        print(len(wenda_list))
        
        for wenda in wenda_list:
            try:
                wen_text = wenda.get('retweeted_status').get('text')
                da_text = wenda.get('text')
                regex = re.compile('\[\¥([^\]]+)\]')
        #        m = '\[\¥([^\]]+)\]'
                wen_money= regex.findall(wen_text)
                da_money = regex.findall(da_text)
        #        wen_money = re.search(m,wen_text)
        #        da_money = re.search(m,da_text)
                money = 0.0
                if wen_money :
                    money = float(wen_money[0])
                elif da_money:
                    money = float(da_money[0])
                total_num += float(money)
                money_list.append(money)
                out_f.writelines('【问】' + timestampToDate(wenda.get('retweeted_status').get('created_at')) + '\n<br>')
                out_f.writelines('' + edit_imgsrc(wen_text) + '\n<br>')
                out_f.writelines('【答】' + timestampToDate(wenda.get('created_at')) + '\n<br>')
                out_f.writelines('' + edit_imgsrc(da_text) + '\n<br>')
                out_f.writelines('<a href="https://xueqiu.com/{0}/{1}'.format(str(wenda.get('user_id')),str(wenda.get('id'))) + '">原文地址</a><br>')
                out_f.writelines('<p>¥' + str(money) + '</p>\n')
                out_f.writelines('#' * 100 + '\n<br>')
            except:
                pass
#    print (xueqiu_json)
    out_f.writelines('<p>' + str(total_num) + '</p>')
    out_f.close() 
    print(money_list)
    print(total_num)
    
def edit_imgsrc(src):
    return src.replace('img src="//','img src="http://')    

#采集文章
def Get_user_timeline():
    """
    1760673340 HIS1963
    3491303582 闲来一坐s话投资
    """
    url = 'https://xueqiu.com/v4/statuses/user_timeline.json?user_id=3491303582&page=1&type=2&_=1487416106586' 
    result_json = requests.get(url,headers = headers)
    user_timeline_json = json.loads(result_json.text)
    statuses_list = user_timeline_json.get('statuses')
    out_f = open('output/user_timeline_3491303582.html','a',encoding='utf-8')
    for statuses in statuses_list:
        statuses_text = statuses.get('text')
        statuses_title = statuses.get('title')
        created_at = timestampToDate(statuses.get('created_at'))
        screen_name = statuses.get('user').get('screen_name')
        
        out_f.writelines('<h2>' + statuses_title + '</h2>\n<br>')
        out_f.writelines(created_at + ' @' + screen_name + '\n<br>')
        out_f.writelines(edit_imgsrc(statuses_text) + '\n<br>')
        out_f.writelines('#' * 100 + '\n<br>')
    out_f.close()    
        
if __name__ == '__main__':
#    print(timestampToDate(int('1471148483000')/1000))
#    wenda_caiji()
    Get_user_timeline()
#    jsonToHtml()
#    wen_text='[¥68.00]'
#    regex = re.compile('\[\¥([^\]]+)\]')
#    regex1 = re.compile('\[\¥11([^\]]+)\]')
#    m = '\[\¥([^\]]+)\]'
#    print (re.search(m,wen_text))
#    aa = regex.findall(wen_text)  
#    bb = regex1.findall(wen_text) 
#    if aa:
#        print(aa[0])
#    if bb:
#        print(bb)
    