import os
import time
import json
import random
import requests


REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Cookie': 'Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1614413456,1614422866,1614437125,1614475980; reviewJump=nojump; usersurvey=1; v=A-yuTw5voIQ0YbS4gREgEuQXvcEdpZBOkkmkE0Yt-Bc6UYL3brVg3-JZdKeV'
}

tgt_url = "https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=100017744916&score=0&sortType=5&page=1&pageSize=10&isShadowSku=0&rid=0&fold=1"
web_source = requests.get(tgt_url, headers=REQUEST_HEADER)

# soup = BeautifulSoup(web_source.content.decode("gbk"), 'lxml')
w = web_source.content.decode("gbk")

print(w)

