# -*- coding: UTF-8 -*-
# @Project ：bilibiliDanMu 
# @File    ：getBilibiliComment.py
# @Author  ：Ma Haoyu
# @Date    ：2021/7/20 16:27 
import json, requests, time
import pandas as pd


def get_base_info(oid):
    base_info_url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={oid}'
    base_info = requests.get(base_info_url, headers=dic_header).json()['data']
    # print(base_info) #可以输出转化为json形式的数据
    print('EDG vs RNG大战视频基本信息：\n')
    print('播放数量：{}\n弹幕数量：{}\n收藏数量：{}\n硬币数量：{}\n分享数量：{}\n点赞数量：{}\n------\n评论数量：{}'.format(
        base_info['view'], base_info['danmaku'], base_info['favorite'],
        base_info['coin'], base_info['share'], base_info['like'], base_info['reply']
    ))


if __name__ == '__main__':
    dic_header = {'User-Agent': 'Mozilla/5.0'}
    oid = 370124445
    get_base_info(oid)