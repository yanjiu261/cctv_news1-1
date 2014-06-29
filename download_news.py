#coding=utf-8

import urllib2
import urllib
import re
import time
import threading
import socket
import os
import json



socket.setdefaulttimeout(120)



list_pattern=re.compile(r'{\'title\':\'.*?\'<!--VIDEOSTR-->\'}', re.S)
content_search=re.compile(r'<div class="body" id="content_body">(.*?)</div>', re.S).search
file_name_search=re.compile(r'\d{4}/\d{2}/\d{2}').search

class Conn(object):  
    def __init__(self):  
            self.headers = {  
                                        'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'  
                                    }       
    def request(self, url, data={},times=0):  
           try:
                   postdata = urllib.urlencode(data)        
                   req = urllib2.Request(
                                                       url=url,
                                                       data=postdata,
                                                       headers=self.headers  
                                                       )  
                   link = urllib2.urlopen(req)  
                   result = link.read()  
                   link.close()  
                   return  result  
           except  Exception, e:         #处理超时、url不正确异常
                 if times <20:
                          print "conn error:%s"%e
                          print r'重新连接'
                          self.request(url, data,times+1)
                 else:
                          print r'重试超过20次,退出'
                          error_file_list.append(url)

def get_list(url,count):
  c=Conn()
  result=[]
  list_page=c.request(url)
  l=re.findall(list_pattern,list_page)
  for i in l:
    result.append(eval(i))
  return result[:count]

def createContent(list):
  articles=[]
  for item in list:
      c=Conn()
      page=c.request(item['link_add'])
      content=content_search(page).group(1)
      article="<h2>%s</h2><div>%s</div>"%(item["title"].decode('gbk','ignore').encode('utf-8'),content)
      print item["title"].decode('gbk','ignore').encode('utf-8')
      articles.append(article)
  b=file_name_search(list[0]["link_add"]).group(0).replace('/','')
  e=file_name_search(list[-1]["link_add"]).group(0).replace('/','')
  book_content="<!doctype html><html><head><meta charset=\"UTF-8\"><title> 新闻1+1_%s-%s </title></head><body> %s </body></html>"%(b,e,''.join(articles))
  f=open("%s-%s.html"%(b,e),'w')
  f.write(book_content)
  f.close()
if __name__ == '__main__':
  #文章总数
  count=60
  #每本书中文章数
  articlesOfBook=60

  start=time.time()
  lists=get_list('http://cctv.cntv.cn/lm/xinwenyijiayi/video/index.shtml',count)
  books_nums= count/articlesOfBook
  if count%articlesOfBook != 0:
      books_nums+=1
  threads=[]
  for i in range(0,books_nums):
      threads.append(threading.Thread(target=createContent,args=(lists[i*articlesOfBook:i*articlesOfBook+articlesOfBook],)))
  for i in threads:
      i.start()
  while reduce(lambda x,y:x or y,[ i.isAlive() for i in threads]):
      time.sleep(1)
      # print time.time()
  end=time.time()
  print end,start,end-start
  print r'全部下载完毕,共用时%s'%(end-start)
  print len(lists),books_nums