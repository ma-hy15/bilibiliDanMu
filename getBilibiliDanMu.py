# -*- coding: utf-8 -*-
# @Project ：bilibiliDanMu
# @File    ：getBilibiliDanMu.py
# @Author  ：Ma Haoyu
# @Date    ：2021/7/15 11:00
import requests
import json
import chardet
import re
from pprint import pprint


# 1.根据bvid请求得到cid
def get_cid(BV,index=0):
    url = 'https://api.bilibili.com/x/player/pagelist?bvid='+BV+'&jsonp=jsonp'
    res = requests.get(url).text
    json_dict = json.loads(res)
    # pprint(json_dict)
    # 对于多节的视频，根据序号i选择返回的cid，默认是0
    return json_dict["data"][index]["cid"]



# 2.根据cid请求弹幕，解析弹幕得到最终的数据
def get_data(cid):
    final_url = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + str(cid)
    final_res = requests.get(final_url)
    final_res.encoding = chardet.detect(final_res.content)['encoding']
    final_res = final_res.text
    pattern = re.compile('<d.*?>(.*?)</d>')
    data = pattern.findall(final_res)
    # pprint(final_res)
    return data


cid = get_cid(BV='BV1SK4y1M7Xj')
get_data(cid)
