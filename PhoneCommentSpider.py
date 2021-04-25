import os
import re
import time
import json
import random
import codecs
import requests
from bs4 import BeautifulSoup

class Spider:
    def __init__(self, comment_url, product_list=None,finish_list=None ,download_path="download/", proxy_file=None):

        self.comment_url = comment_url

        self.proxy_pool = None if not proxy_file else \
            [line.strip() for line in open(proxy_file,'r').readlines()]

        self.REQUEST_HEADER = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Cookie': 'Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1614413456,1614422866,1614437125,1614475980; reviewJump=nojump; usersurvey=1; v=A-yuTw5voIQ0YbS4gREgEuQXvcEdpZBOkkmkE0Yt-Bc6UYL3brVg3-JZdKeV'
        }

        # 加载商品id
        if not product_list:
            self.crawl_product_list()
        else:
            self.products = json.load(open(product_list,'r',encoding='utf-8'))

        # 加载已完成的列表
        self.finish_list = set()
        if finish_list:
            self.finish_list = set([line.strip() for line in open(finish_list,'r').readlines()])

        # 评论保存路径
        if not os.path.exists(download_path):
            os.mkdir(download_path)
        self.download_path = download_path

    # 先爬取对应品牌的产品的id号，然后直接通过id号请求对应的接口拿到评论数据
    # 为了偷懒，这里没有处理同一个品牌的产品翻页的问题，只选择了同一个品牌第一页的产品来提取评论信息。
    def crawl_product_list(self):
        product_dict = {}
        print(" crawl product list ...")
        product_list_url = "https://list.jd.com/list.html?cat=9987%2C653%2C655&cid3=655&cid2=653"
        web_source = requests.get(product_list_url,headers=self.REQUEST_HEADER)
        if web_source.status_code != 200:
            print("[ERROR] Status Code ERROR ...")
        else:
            soup = BeautifulSoup(web_source.content.decode("utf8"), 'lxml')
            # 拿到所有手机品牌的链接
            _temp = soup.find_all(name="ul",attrs={"class":"J_valueList v-fixed"})
            all_brands = _temp[0].find_all(name="a")
            for i,url_object in enumerate(all_brands):
                print("[INFO {}/{}] get product id for brand [{}]".format(i,len(all_brands),url_object.attrs['title']))
                brand_url = "https://list.jd.com" + url_object.attrs['href']
                # 请求品牌对应的产品列表
                brand_products_source = requests.get(brand_url,headers=self.REQUEST_HEADER)
                if brand_products_source.status_code != 200:
                    print("[ERROR] Status Code ERROR ...")
                else:
                    products_soup = BeautifulSoup(brand_products_source.content.decode("utf8"), 'lxml')
                    # 处理第一页的30条数据，拿到id号和title名称
                    products = products_soup.find_all(name="li",attrs={"class":"gl-item"})
                    for product in products:
                        name = product.find_all(name="em")[-1].text
                        code = product.attrs['data-sku']
                        product_dict[code] = name
                # 休眠 防止被检测到
                time.sleep(random.randint(8,20))
            with codecs.open("products.json",'w',encoding='utf-8') as f:
                json.dump(product_dict,f,ensure_ascii=False)
            print("[INFO] crawl product list ...")

    def crawl_once(self,code,name,idx,cnt):
        tgt_url = self.comment_url.format(code)
        web_source = requests.get(tgt_url, headers=self.REQUEST_HEADER)

        print("[{}/{} | STATUS CODE:[{}]]start crawl {}".format(idx,cnt,web_source.status_code,name))
        if web_source.status_code != 200:

            print("[ERROR] Status Code ERROR, start chrome for cookies ...")

        else:
            soup = BeautifulSoup(web_source.content.decode("gbk"), 'lxml')
            if soup.find(name="p"):
                self.save_data(soup.find(name="p").text,name)
            else:
                print("[warn] cannot find json comments ...")

            time.sleep(random.randint(8,20))

    def save_data(self,json_text,name):
        saved_path = os.path.join(self.download_path,name)
        save_file = os.path.join(saved_path,"{}.txt".format(int(time.time())))
        res = []
        if not os.path.exists(saved_path):
            os.mkdir(saved_path)
        try:
            json_comments = re.findall(r"[(](.*)[)]",json_text)[0]
            comments_dict = json.loads(json_comments)
            for comment in comments_dict['comments']:
                res.append(comment['content'])
            with open(save_file,"w",encoding="utf-8") as f:
                f.write("\n\n".join(res))
        except:
            print("[error ]re cannot match json comments ..")

    def run(self):
        product_count = len(self.products.keys()) - len(self.finish_list)
        idx = 1
        for key,name in self.products.items():
            if key in self.finish_list:continue

            name = re.sub(r"[-()\"\n\t\\#/@;:<>{}`+=~|.!?,]", "", name)
            self.crawl_once(key,name,idx,product_count)
            idx += 1

            with open("finish.txt","a+") as f:
                f.write(key+"\n")

        print("spider run over ... ")

if __name__ == '__main__':
    # page为评论页数
    product_comment_url = "https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&" \
                          "productId={}&score=0&sortType=5&page=2&pageSize=10&isShadowSku=0&rid=0&fold=1"

    # 未获取product id
    spider = Spider(product_comment_url)

    # 已经拿到product id文件后
    # spider = Spider(product_comment_url,"products.json","finish.txt")

    spider.run()