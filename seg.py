# -*- coding: utf-8 -*-
"""
Created on Mon May 25 15:23:14 2015

@author: x
"""

import cookielib
import urllib2
import urllib
import socket
import re
import string
import os
import sys
from BeautifulSoup import BeautifulSoup
from urllib2 import URLError
import traceback
import proxyIP
import random
import user_agents
###############################################################################
###############################################################################
###############################################################################
#############   not use, but very useful!!!         ###########################
###############################################################################

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

class HeadRequest(urllib2.Request):
    def get_method(self):
        return 'HEAD'

ExploereHEADERS = {"Content-type": "application/x-www-form-urlencoded",  
           'Accept-Language':'zh-CN,zh;q=0.8',  
           'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0;Windows NT 5.0)',  
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  
           "Connection": "close",  
           "Cache-Control": "no-cache"}

def GetWeb(url,values,method ='get'):
    data = urllib.urlencode(values) #数据编码  
    if method == 'get':  
        url = url+'?'+data  
        req = urllib2.Request(url, headers = ExploereHEADERS)  
    else:  
        req = urllib2.Request(url, data,headers = ExploereHEADERS)  
    response = urllib2.urlopen(req)  
    the_page = response.read()  
    response.close() #不用了就关闭掉  
    return the_page

def GetImage(url,name):  
    im = GetWeb(url,'')  
    f = open(name,'wb')  
    f.write(im)  
    f.close()
    #return 

def trace_back():  
    try:  
        return traceback.print_exc()  
    except:  
        return ''

###############################################################################
#############   not use, but very useful!!!         ###########################
###############################################################################
###############################################################################
###############################################################################




def formatFileName(filename):   # 去掉在文件名中无法使用的不合法字符，确保能正确创建文件
    if (isinstance(filename, str)):
        tuple=('?','╲','*','/',',','"','<','>','|','“','"','，','‘','”',',','/',':')
        for char in tuple:
            if (filename.find(char)!=-1):
                filename=filename.replace(char," ")
        return filename
    else:
        return 'None'





def DownloadThesisFromSeg(searchItem,usr,psd):
    #searchItem = 'NEWTEM'
    
    #########先建一个以搜索词命名的文件夹，将所有下载的文件都存入这个文件夹中#################
    if not os.path.exists(searchItem):
        os.makedirs(searchItem)
    
    #重定向写入文件，重定向之前需要把当前输出保存到变量中，以便恢复。
    saveout = sys.stdout    
    fsock = open(os.path.join(searchItem,'out.log'),'a')
    sys.stdout = fsock
    
    ######先编译正则表达式，在匹配文献年份时用，对于多次匹配时，先编译可以提高效率#############
    p = re.compile('\d{4}')
    
    year = ''
    title = ''
    refUrl = ''
    status = False
    totalNum = 0
    #sourceList = []
    startPage = 0
    
    
    ###############################################################################
    ######### while True:                    ######################################
    #########   if condition:                ######################################
    #########       break                    ######################################
    ######### 这是python中类似于do...while语句  ######################################
    ###############################################################################
    
    while True:
        ############ seg中，单个session下载全文超过150就会封闭IP段 #####################
        ####### client IP is blocked because: More than 150 PDF or full text downloads in a session Blocked IPs: 124.016.133.042 - 124.016.133.042 ######
        initUrl = 'https://login.seg.org/'
        loginUrl = r'https://library.seg.org/action/showLogin?redirectUri=http://library.seg.org/'
        socket.setdefaulttimeout(10)
        
        proxy_ip =random.choice(proxyIP.proxy_list)
        print proxy_ip
        proxy_support = urllib2.ProxyHandler(proxy_ip)
        user_agent = random.choice(user_agents.user_agents)
        print user_agent
        ######加载cookies，使用urllib、urllib2时可以传递cookies############################
        cj = cookielib.CookieJar()
        #opener = urllib2.build_opener(proxy_support,urllib2.HTTPCookieProcessor(cj))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent',user_agent)]
        
        urllib2.install_opener(opener)
        
        #######通过访问这个网址，获得其隐藏的输入变量，在登陆的时候会传递给服务器#################
        resp = urllib2.urlopen(loginUrl).read()
        #print resp
        #######使用beautifulSoup解析获得的网页，以下是获得form标签，返回的是一个列表############
        forms = BeautifulSoup(resp)('form')
        form = forms[0]
        #######使用get方法获得该标签的一个属性##############################################
        postUrl = initUrl + form.get('action')
        
        ##########将post需要传递的表单存入temp_variable中，键值对的形式######################
        temp_variable={}
        div_inputs = BeautifulSoup(resp)('input')
        for div_input in div_inputs:
            if div_input.get('type')=='hidden':
                temp_variable[div_input.get('name')] = div_input.get('value')
                #print div_input.get('name') +" = " + temp_variable[div_input.get('name')]
        temp_variable['LoginTextBox'] = usr
        temp_variable['PasswordTextBox'] = psd
        temp_variable['SubmitButton'] = 'Go'
        data = urllib.urlencode(temp_variable)
        
        resp = opener.open(postUrl,data).read()
        #print resp
        
        
    
    
        #########全内容搜索，每次最多返回100个#############################################
        searchUrl = 'http://library.seg.org/action/doSearch?AllField=%s&publication=all&resultsTab=std&target=default&startPage=%d&pageSize=100'%(searchItem,startPage)
        resp = urllib2.urlopen(searchUrl).read()
        divs = BeautifulSoup(resp)('div')
        
        #############拆分标签，找到搜索到的文献总数，文献标题，年份，以及文献的链接###############
        for div in divs:
            ################获取文献总数######################################
            if div.get('class')=='stacked paginationStatus':
                ########需修改，这里得到的totalNum只有两位数，不符合要求###########
                totalNum = string.atoi(div.getText().split('of')[1])
                print totalNum
                sys.stdout.flush()
            ################先将文献每个分开，然后对单个进行进一步处理#############
            if div.get('class')=='notSelectedRow':
                labs_table = div('table')
                for lab_table in labs_table:
                    refUrl = 'http://library.seg.org'
                    labs_a = lab_table('a')
                    for lab_a in labs_a:
                        ################提取出题目###########################
                        labs_span = lab_a('span')
                        for lab_span in labs_span:
                            #print lab_span
                            if lab_span.get('class')=='hlFld-Title':
                                ######使用getText()直接获取标签里面的内容，很方便  #############################
                                ###### <span class="hlFld-Title">Designing a 
                                ######      <span onclick="highlight()" class="single_highlight_class">
                                ######          HTEM
                                ######      </span> 
                                ######      system for mapping glaciolacustrine overburden thickness
                                ###### </span>
                                ###### 使用getText()对上层span提取后，就可以得到Designing a HTEM system for mapping glaciolacustrine overburden thickness
                                ###### 对于标题等含有特殊标记的文字提取非常有用     ################################
                                title = lab_span.getText(separator=u" ").replace(':','')
                        #########使用prettify函数可以整理标签，自动加回车，缩进等，便于阅读#######################
                        #print lab_a.prettify()
                        
                        ##########获取年份，年份信息可能在其父标签中，调用parent获得父节点，从父节点开始进行正则匹配################
                        if lab_a.get('class')=='searchResultJournal':
                            year = "【%s】" % p.search(lab_a.parent.getText()).group(0)                 
                            title = year+title
                            #print title
                        ##########获取pdf的链接地址##############################################
                        if lab_a.get('class')=='ref nowrap pdf':
                            refUrl = refUrl + lab_a.get('href')
                    ###########以下是判断该文献是否有下载权限，若有，status=True####################    
                    labs_image = lab_table('img')
                    for lab_image in labs_image:
                        #print lab_image.prettify()
                        if lab_image.get('title')=='full access':
                            status = True
                            ############获取帧头信息############################################
                            #response = urllib2.urlopen(HeadRequest(refUrl))
                            #print response.info()
                            ###########使用urlretrieve直接下载会报错，因为在访问该网页时需要cookies，直接下载会显示cookie异常#####################
                            ###########所以先将要下载的文件流先存到一个变量中，然后写入文件，不知道这样对大文件下载是否管用？#########################                    
                            try:                    
                                f = open(os.path.join(searchItem,formatFileName(title)+'.pdf'),'wb')  
                                f.write(urllib2.urlopen(refUrl).read())
                            except Exception as err:
                                print err
                                #print trace_back()
                            f.close()
                            #urllib.urlretrieve(refUrl,os.path.join(searchItem,title+'.pdf'))
                        else:
                            status = False
                            print 'cannot download......' + title
                            sys.stdout.flush()
                    #sourceList.append((title,refUrl,status))
        startPage += 1
        if (startPage * 100) > totalNum :
            break
    
    #恢复标准输出
    sys.stdout = saveout
    fsock.close()
#os.makedirs(searchItem)
#for source in sourceList:
#    if source[2]:
#        pass
        #urllib.urlretrieve(source[1],os.path.join(searchItem,source[0]+'.pdf'))
#    else:
#        print source[0]
    #if div.get('class')=='stacked paginationStatus':
    #    print div
if __name__ == '__main__':
    DownloadThesisFromSeg(,,)
