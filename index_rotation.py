import urllib.request         #这就是2.x中的urllib2库
import re

stocklist=["000016","000300","000905","399006"]
pre=20

class CurrentInfo(object):
    def __init__(self, date, time,price):
        self.date = date
        self.time = time
        self.price = price
class PreInfo(object):
    def __init__(self, name, date,price):
        self.name = name
        self.date = date
        self.price = price
        
def getUrlContent(url):
    #下面的命令是读取网页内容
    wp=urllib.request.urlopen(url)
    content=wp.read()
    content=str(content,encoding='utf-8')
    return content
    
def getCurrentData(code):
    #网站抓取当前价格数据时用的代码
    if code[0]=='0':
        codeweb="0"+code
    else:
        codeweb="1"+code
    #提取当天的日期、时间、当前价格
    #下面是在Chrome中找到的动态获取收盘价的地址
    url="http://api.money.126.net/data/feed/"+codeweb+"?callback=ne28e48ef7"
    #下面的命令是读取网页内容
    content=getUrlContent(url)
    #下面的命令是用正则表达式进行模式匹配，查找需要的内容
    pattern='"update": "(.+?)\s+?(.+?)",'   #这里是抓取当天的更新时间
    #\s表示空白字符；+表示匹配前一个字符1次或无限次；?表示匹配前一个字符0次或1次；(?P<name>...)表示分组，除了原有的编号外再制定一个额外的别名；
    #.匹配任意除换行符"\n"外的字符；
    #http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html
    m=re.search(pattern, content)
    update_date=m.group(1)
    update_time=m.group(2)
    #抓取当天的价格
    pattern='"price": (.+?), "open"'
    m=re.search(pattern, content)
    update_price=m.group(1)
    index_info=CurrentInfo(update_date,update_time,update_price.replace(",",""))
    return index_info

def getPreData(code,pre):
    ###########################提取20天前的价格
    #历史数据所在网址
    #url="http://app.finance.china.com.cn/stock/quote/history.php?code=sh000300&type=daily"
    url="http://quotes.money.163.com/trade/lsjysj_zhishu_"+code+".html"
    content=getUrlContent(url)
    
    pattern="var STOCKNAME = '(.+?)'"
    name=re.findall(pattern, content,re.S)
    name=name[0]
    
    #pattern="<tr>.+?<a href=.+?sh000300&day=(.{10}).+?<td><.+?>(.+?)</span>.+?</tr>"
    pattern="<tr class=.+?><td>(\d{8})</td>"+"<td>.+?</td>"*3+"<td>(.+?)</td>"+"<td>.+?</td>"*4+"</tr>"
    m1=re.findall(pattern, content,re.S)  #返回一个列表，二维的
    
    #判断当前有几填的有效历史数据
    current_info=getCurrentData(code)
    days_current_page=len(m1)
    date_c=current_info.date.replace('/',"")
    if m1:
        date_tem=m1[0][0]
        if date_c==date_tem:
            m1=m1[1: days_current_page ]
            days_current_page=days_current_page-1
    else:
        date_tem=date_c
   
    #如果当前页面不够，则打开上一季的数据
    if days_current_page<pre:
        year=int(date_tem[0:4])
        month=int(date_tem[4:6])
        season=int((month-1)/3)+1
        if season==1:
            year=year-1
            season=4
        else:
            season=season-1
        url="http://quotes.money.163.com/trade/lsjysj_zhishu_"+code+".html?year="+str(year)+"&season="+str(season)
        content=getUrlContent(url)
        m2=re.findall(pattern, content,re.S)
        m1=m1+m2[0:(pre-days_current_page)]
    m1=m1[0:pre]
    datepre=m1[-1][0][0:4]+"/"+m1[-1][0][4:6]+"/"+m1[-1][0][6:8]
    
    pre_info=PreInfo(name,datepre,m1[-1][1].replace(",",""))
    return current_info,pre_info

def rateCompute(code,pre):
    current_data,pre_data=getPreData(code,pre)
    #过去20天增幅
    rate=float(current_data.price)/float(pre_data.price)*100-100  #float()将字符串转化为浮点型数值
    
    rate_msg=pre_data.name+"过去"+str(pre)+"日增幅="+str(rate)+"%"
    price_msg=pre_data.name+"当前价="+current_data.price+"；\n前"+str(pre)+"日前收盘价="+pre_data.price
    datepre=pre_data.date
    date_msg="当前时间="+current_data.date+" "+current_data.time+"; \n前"+str(pre)+"交易日="+pre_data.date
    return rate_msg,price_msg,date_msg

if __name__=="__main__":
    output_rate=[]
    output_price=[]
    stocklist=["000016","000300","000905","399006"]
    pre=20

    for code in stocklist:
        result=rateCompute(code,pre)     
        output_rate.append(result[0])
        output_price.append(result[1])
    for item in output_rate:
        print(item)
    for item in output_price:
        print(item)
    print(result[2])
    