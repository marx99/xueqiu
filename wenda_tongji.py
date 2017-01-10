# -*- coding: utf-8 -*-

import json
import re

def readJson (jsonpath):
    job_type_lists = []
    with open(jsonpath,'r',encoding='utf-8') as f:
        return f.read()
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
    xueqiu_json = readJson('wenda.json')   
    json_obj = json.loads(xueqiu_json)
    wenda_list = json_obj.get('statuses')
    
    out_f = open('output/index3.html','a',encoding='utf-8')
    
    for wenda in wenda_list:
        wen_text = wenda.get('retweeted_status').get('text')
        da_text = wenda.get('text')
        regex = re.compile('\[\¥([^\]]+)\]')
        m = '\[\¥([^\]]+)\]'
#        wen_money= regex.findall(wen_text)
#        da_money = regex.findall(da_text)
        wen_money = re.search(m,wen_text)
        da_money = re.search(m,da_text)
        money = ''
        if wen_money and wen_money.group(0):
            money = wen_money.group(0)
        elif da_money:
            money = da_money.group(0)
        out_f.writelines('【问】' + edit_imgsrc(wen_text) + '<br>')
        out_f.writelines('【答】' + edit_imgsrc(da_text) + '<br>')
        out_f.writelines('<a href="https://xueqiu.com/{0}/{1}'.format(str(wenda.get('user_id')),str(wenda.get('id'))) + '">原文地址</a><br>')
        out_f.writelines('<p>' + money + '</p>')
        out_f.writelines('#' * 100 + '<br>')
#    print (xueqiu_json)
    out_f.close() 
    
def edit_imgsrc(src):
    return src.replace('img src="//','img src="http://')    
            
if __name__ == '__main__':
#    jsonToHtml()
    wen_text='[¥68.00]'
    regex = re.compile('\[\¥([^\]]+)\]')
    regex1 = re.compile('\[\¥11([^\]]+)\]')
    m = '\[\¥([^\]]+)\]'
    print (re.search(m,wen_text))
    aa = regex.findall(wen_text)  
    bb = regex1.findall(wen_text) 
    if aa:
        print(aa[0])
    if bb:
        print(bb)
    