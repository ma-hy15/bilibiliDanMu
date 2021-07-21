# -*- coding: UTF-8 -*-
# @Project ：bilibiliDanMu 
# @File    ：getNovel.py
# @Author  ：Ma Haoyu
# @Date    ：2021/7/15 15:17 

from bs4 import BeautifulSoup
import requests


class DownLoader(object):
    def __init__(self):
        self.url = 'https://www.xbiquge.la'
        # 这里是你要下载的小说目录页
        self.target = 'https://www.xbiquge.la/49/49527'
        # 存储小说的章节
        self.names = []
        # 存储小说相应章节的url地址
        self.urls = []
        # 存储下载的章节数
        self.nums = []

    # 获取下载链接
    def get_download_url(self):
        html = requests.get(url=self.target).content.decode('utf-8')
        soup = BeautifulSoup(html, 'html5lib')
        dl = soup.find_all('div', id='list')
        a_bf = BeautifulSoup(str(dl), 'html5lib')
        charp_url = a_bf.find_all('a')
        charp_url = charp_url[0:100]
        self.nums = len(charp_url)
        for each in charp_url:
            self.urls.append(self.url + each.get('href'))
            self.names.append(each.text)
        return

    # 获取章节内容
    def get_contents(self, target):
        req = requests.get(url=target).content.decode('utf-8')
        dv_Area = BeautifulSoup(req, 'html5lib')
        dv_Area_text = dv_Area.find_all('div', id='content')
        if len(dv_Area_text) != 0:
            split_string = '亲,点击进去,给个好评呗'
            text = dv_Area_text[0].text.split(split_string)[0]
            return text
        else:
            print('被拦截了')
            return

    # 把内容写入文本  name章节名，path当前路径下,小说保存名称 text章节内容
    def writer(self, name, path, text):
        if name != None and path != None and text != None:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(name + '\n')
                f.writelines(text)
                f.write('\n\n')
                f.flush()


if __name__ == "__main__":
    dl = DownLoader()
    dl.get_download_url()
    print('开始下载')
    for i in range(dl.nums):
        dl.writer(dl.names[i], '绍宋.txt', dl.get_contents(str(dl.urls[i])))
    print('下载完成')
