
# coding: utf-8

# In[ ]:


from urllib.request import urlopen
import argparse
import requests as req
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("-name", "--target", required=True)

args = parser.parse_args()
target = args.target

def main():
    url_info = "https://www.google.co.kr/search?"
    params = {
        "q" : target, #query
        "tbm":"isch"  #to be matched : image search
    }
    html_object = req.get(url_info,params)
    if html_object.status_code == 200:
        bs_object = BeautifulSoup(html_object.text,"html.parser")
        #인스턴스 생성
        img_data = bs_object.find_all("img")
        #인스턴스의 find_all 이라는 함수에 img 태그가 있으면 img_data에 넣어줌
        for i in enumerate(img_data[1:]):
            t = urlopen(i[1].attrs['src']).read()
            filename = "byeongwoo_"+str(i[0]+1)+'.jpg'
            with open(filename,"wb") as f:
                f.write(t)
                print("Image saved as \'",f.name,'\'')

if __name__=="__main__":
    main()

