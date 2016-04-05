import urllib.request         #这就是2.x中的urllib2库
import re

stocklist=["000300","000905"]
pre=20

output_rate=[]
output_price=[]
for code in stocklist:

    #网站抓取当前价格数据时用的代码
    if code[0]=='0':
        codeweb="0"+code
    else:
        codeweb="1"+code
    #提取当天的日期、时间、当前价格
    #下面是在Chrome中找到的动态获取收盘价的地址
    url="http://api.money.126.net/data/feed/"+codeweb+"?callback=ne28e48ef7"
    #下面的命令是读取网页内容
    wp=urllib.request.urlopen(url)
    content=wp.read()
    content=str(content,encoding='utf-8')
    
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
    
    ###########################提取20天前的价格
    #历史数据所在网址
    #url="http://app.finance.china.com.cn/stock/quote/history.php?code=sh000300&type=daily"
    url="http://quotes.money.163.com/trade/lsjysj_zhishu_"+code+".html"
    wp=urllib.request.urlopen(url)
    content=wp.read()
    content=str(content,encoding='utf-8')
    
    pattern="var STOCKNAME = '(.+?)'"
    name=re.findall(pattern, content,re.S)
    name=name[0]
    
    #pattern="<tr>.+?<a href=.+?sh000300&day=(.{10}).+?<td><.+?>(.+?)</span>.+?</tr>"
    pattern="<tr class=.+?><td>(\d{8})</td>"+"<td>.+?</td>"*3+"<td>(.+?)</td>"+"<td>.+?</td>"*4+"</tr>"
    m1=re.findall(pattern, content,re.S)  #返回一个列表，二维的
    
    #判断当前有几填的有效历史数据
    days_current_page=len(m1)
    date_tem=update_date.replace('/',"")
    if m1:
        date_tem=m1[0][0]
        if update_date==date_tem:
            days_current_page=days_current_page-1
    else:
        print("Nothing found!")
   
    #如果当前页面不够，则打开上一季的数据
    if days_current_page<pre:
        year=int(date_tem[0:4])
        month=int(date_tem[4:6])
        season=int((month-1)/3)+1
        if season==1:
            year=year-1
            season=4
        url="http://quotes.money.163.com/trade/lsjysj_zhishu_"+code+".html?year="+str(year)+"&season="+str(season)
        wp=urllib.request.urlopen(url)
        content=wp.read()
        content=str(content,encoding='utf-8')
        m2=re.findall(pattern, content,re.S)
        m1=m1+m2[0:(pre-days_current_page)]
    #过去20天增幅
    rate=float(update_price.replace(",",""))/float(m1[-1][1].replace(",",""))*100-100  #float()将字符串转化为浮点型数值
    
    rate_msg=name+"过去"+str(pre)+"日增幅="+str(rate)+"%"
    output_rate.append(rate_msg)
    
    price_msg=name+"当前价="+update_price+"；\n"+str(pre)+"交易日前收盘价="+m1[-1][1]
    output_price.append(price_msg)
    
    datepre=m1[-1][0][0:4]+"/"+m1[-1][0][4:6]+"/"+m1[-1][0][6:8]

nlen=len(stocklist)
for i in range(nlen):
    print(output_rate[i])
for i in range(nlen):
    print(output_price[i])
print("当前时间=",update_date,"  ",update_time,"; \n前"+str(pre)+"交易日=",datepre)

