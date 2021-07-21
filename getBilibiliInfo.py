# -*- coding: UTF-8 -*-
# @Project ：bilibiliDanMu 
# @File    ：getBilibiliComment.py
# @Author  ：Ma Haoyu
# @Date    ：2021/7/20 16:27 
import json
from datetime import datetime
import requests
import chardet
import re
import time
from bs4 import BeautifulSoup
from pprint import pprint


class BilibiliInfo(object):
    def __init__(self, bv='', av=0, index=0, header={'User-Agent': 'Mozilla/5.0'}):
        self.dic_header = header
        self.table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
        self.tr = {}
        for i in range(58):
            self.tr[self.table[i]] = i
        self.s = [11, 10, 3, 8, 4, 6]
        self.xor = 177451812
        self.add = 8728348608
        if bv != '':
            self.bvid = bv
            self.aid = self._dec(bv)
            self.cid = self._getcid(self.bvid, index)
            self.state = True
        elif av != 0:
            self.bvid = self._enc(av)
            self.aid = av
            self.cid = self._getcid(self.bvid, index)
            self.state = True
        else:
            self.bvid = 0
            self.aid = 0
            self.cid = 0
            self.state = False

    def updateid(self, bv='', av=0, index=0):
        if bv != '':
            self.bvid = bv
            self.aid = self._dec(bv)
            self.cid = self._getcid(self.bvid, index)
            self.state = True
        elif av != 0:
            self.bvid = self._enc(av)
            self.aid = av
            self.cid = self._getcid(self.bvid, index)
            self.state = True
        else:
            self.bvid = 0
            self.aid = 0
            self.cid = 0
            self.state = False

    def getstate(self):
        return self.state

    def getbvid(self):
        return self.bvid

    def getaid(self):
        return self.aid

    def getcid(self):
        return self.cid

    def getbullet(self):
        bullet_list = []
        if type(self.cid) == list:
            for mycid in self.cid:
                bullet_list.extend(self._getbullet_single(mycid))
        else:
            bullet_list.extend(self._getbullet_single(self.cid))
        return bullet_list

    def _getbullet_single(self, cid):
        bullet_url = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + str(cid)
        bullet_res = requests.get(bullet_url)
        bullet_res.encoding = chardet.detect(bullet_res.content)['encoding']
        bullet_res = bullet_res.text
        pattern = re.compile('<d.*?>(.*?)</d>')
        data = pattern.findall(bullet_res)
        # pprint(data)
        return data

    def getcomments(self):
        comment_page = 1
        comment_data_lst = []
        while True:
            try:
                comment_url = 'https://api.bilibili.com/x/v2/reply/main?next={}&type={}&oid={}'.format(
                    comment_page, 1, self.aid)
                html = requests.get(url=comment_url, headers=self.dic_header)
                # start = html.text.index('{')
                # end = html.text.index('}]') + 1
                comment_data = json.loads(html.text)['data']['replies']
                # print(comment_data) #成功的转换为json数据
                print(f'当前正在爬取第{comment_page}页评论数据...\n')
                for data in comment_data:
                    dic_coment = {}
                    dic_coment['member'] = data['member']['uname']
                    dic_coment['like'] = data['like']
                    dic_coment['comment'] = data['content']['message']
                    dic_coment['time'] = datetime.fromtimestamp(data['ctime'])
                    dic_coment['rpid'] = data['rpid_str']
                    comment_data_lst.append(dic_coment)
                    print('昵称: {}\n点赞数：{}\n评论：{}\n'.format(dic_coment['member'],
                                                           dic_coment['like'], dic_coment['comment']))
                    # 这个是下一步封装完爬取回复数据的函数后才添加的
                    comment_data_lst.extend(self._getreplies(dic_coment['member'], dic_coment['rpid']))

                time.sleep(1)
                # 			if comment_page > 1:
                # 				break
                comment_page += 1

            except Exception as Comment_Page_Error:
                break

        return comment_data_lst

    def _getreplies(self, uname, rpid):
        reply_page = 1
        reply_data_lst = []
        while True:
            reply_url = 'https://api.bilibili.com/x/v2/reply/reply?&pn={}&type=1&oid={}&ps=10&root={}'.format(
                reply_page, self.aid, rpid)
            html = requests.get(url=reply_url, headers=self.dic_header)
            reply_data = html.json()['data']['replies']
            if reply_data is not None:
                print('\t正在爬取用户{}的评论回复数据中的第{}页......'.format(uname, reply_page))
            try:
                for data in reply_data:
                    dic_reply = {}
                    dic_reply['comment'] = data['content']['message']
                    dic_reply['member'] = data['member']['uname']
                    dic_reply['like'] = data['like']
                    dic_reply['time'] = datetime.fromtimestamp(data['ctime'])
                    reply_data_lst.append(dic_reply)
                    print('\t回复{} 昵称: {}\n\t点赞数：{}\n\t评论：{}\n'.format(uname, dic_reply['member'],
                                                                      dic_reply['like'], dic_reply['comment']))

                # 			if reply_page > 1:
                # 				break
                reply_page += 1
            except Exception as Reply_Page_Error:
                break

        return reply_data_lst

    def getinfo(self):
        base_info_url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={self.aid}'
        base_info = requests.get(base_info_url, headers=self.dic_header).json()['data']
        # print(base_info) #可以输出转化为json形式的数据
        print('视频基本信息：\n')
        print('播放数量：{}\n弹幕数量：{}\n收藏数量：{}\n硬币数量：{}\n分享数量：{}\n点赞数量：{}\n评论数量：{}\n'.format(
            base_info['view'], base_info['danmaku'], base_info['favorite'],
            base_info['coin'], base_info['share'], base_info['like'], base_info['reply']
        ))
        return base_info

    def _dec(self, x):
        r = 0
        for i in range(6):
            r += self.tr[x[self.s[i]]] * 58 ** i
        return (r - self.add) ^ self.xor

    def _enc(self, x):
        x = (x ^ self.xor) + self.add
        r = list('BV1  4 1 7  ')
        for i in range(6):
            r[self.s[i]] = self.table[x // 58 ** i % 58]
        return ''.join(r)

    def _getcid(self, bv, index=0):
        url = 'https://api.bilibili.com/x/player/pagelist?bvid=' + bv + '&jsonp=jsonp'
        res = requests.get(url).text
        json_dict = json.loads(res)
        # pprint(json_dict)
        # 对于多节的视频，根据序号i选择返回的cid，默认是0
        if index == -1:
            length = len(json_dict["data"])
            cid_list = []
            for i in range(0, length):
                cid_list.append(json_dict["data"][i]["cid"])
            return cid_list
        else:
            return json_dict["data"][index]["cid"]


# 类函数转换为静态函数
def getcid(bv, index=0):
    url = 'https://api.bilibili.com/x/player/pagelist?bvid=' + bv + '&jsonp=jsonp'
    res = requests.get(url).text
    json_dict = json.loads(res)
    # pprint(json_dict)
    # 对于多节的视频，根据序号i选择返回的cid，默认是0
    if index == -1:
        length = len(json_dict["data"])
        cid_list = []
        for i in range(0, length):
            cid_list.append(json_dict["data"][i]["cid"])
        return cid_list
    else:
        return json_dict["data"][index]["cid"]


def getinfo(aid, dic_header=None):
    if dic_header is None:
        dic_header = {'User-Agent': 'Mozilla/5.0'}
    base_info_url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}'
    base_info = requests.get(base_info_url, headers=dic_header).json()['data']
    # print(base_info) #可以输出转化为json形式的数据
    print('视频基本信息：\n')
    print('播放数量：{}\n弹幕数量：{}\n收藏数量：{}\n硬币数量：{}\n分享数量：{}\n点赞数量：{}\n评论数量：{}\n'.format(
        base_info['view'], base_info['danmaku'], base_info['favorite'],
        base_info['coin'], base_info['share'], base_info['like'], base_info['reply']
    ))
    return base_info


def getaid(bvid):
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    r = 0
    for i in range(6):
        r += tr[bvid[s[i]]] * 58 ** i
    return (r - add) ^ xor


def getbullet(cid):
    bullet_url = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + str(cid)
    bullet_res = requests.get(bullet_url)
    bullet_res.encoding = chardet.detect(bullet_res.content)['encoding']
    bullet_res = bullet_res.text
    pattern = re.compile('<d.*?>(.*?)</d>')
    data = pattern.findall(bullet_res)
    # pprint(data)
    return data


if __name__ == '__main__':
    # oid = 369363302
    # get_base_info(oid)
    a = BilibiliInfo(bv='BV1qk4y1C752', index=-1)
    pprint(a.getbullet())
    a.getinfo()
    a.getcomments()
    # bvid = a.enc(170001)
    # pprint(type(a.get_cid(bvid, -1)))
    # pprint(type(a.get_cid(bvid, 0)))
    # pprint(type(a.get_cid(bvid, 1)))
    # print(a.enc(170001))
