# -*- coding: utf-8 -*-
"""
Created on Mon Jan  1 19:22:48 2024

 视频基本信息 basic_info.csv：['bv', 'title', 'duration', 'intro', 'tag', 'view', 'barrage', 'like', 'coin', 'star', 'share'] duration需要自己手动记录
 视频弹幕信息 bars.csv：['bv', 'title', 'timing', 'text']

TODO： duration + 分p视频出bug
@author: OxCsea
"""

import random
import requests
import re
from bs4 import BeautifulSoup
import operator
import traceback
import os
import pandas as pd
from lxml import etree
from time import sleep
import json
import time
import math

user_agent = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

timeout = 5 

headers = {
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "origin": "https://www.bilibili.com",
        "referer": "",
        "cookie": "", # 请填写自己的cookie
        "user-agent": random.choice(user_agent),
}

def getHTML(url):
    try:
        response = requests.get(url=url, headers=headers,
                                timeout=timeout)
        # 自适应编码
        # response.encoding = response.apparent_encoding
        response.encoding = 'utf-8'
        return response.text
    except:
        print(f"reqeuset url : {url} error...")
        print(traceback.format_exc())
        return None


def parsePage(page):
    try:
        print("parsing...")
        html_ = etree.HTML(page)
        meta_title = html_.xpath('//meta[@name="title"]/@content')[0]
        if meta_title == '视频去哪了呢？_哔哩哔哩_bilibili':
            print(f'视频 404 not found')
            return [], '视频 404 not found'
        syntax = [':', '=']
        flag = 0
        keys = re.findall(r'"cid":[\d]*', page)
        if not keys:
            keys = re.findall(r'cid=[\d]*', page)
            flag = 1
        comments, title = {}, None
        keys = [keys[1]]
        for index, item in enumerate(keys):
            key = item.split(syntax[flag])[1]
            print(f'{index + 1}/{len(keys)}: {key}')
            comment_url = f'https://comment.bilibili.com/{key}.xml'  # 弹幕地址
            comment_text = getHTML(comment_url)
            bs4 = BeautifulSoup(comment_text, "html.parser", from_encoding='utf-8')
            if not title:
                title = BeautifulSoup(page, "html.parser").find('h1').get_text().strip()
            for comment in bs4.find_all('d'):
                time = float(comment.attrs['p'].split(',')[0])
                time = timeFormatter(time)
                comments[time] = comment.string
        sorted_comments = sorted(comments.items(), key=operator.itemgetter(0))  # 排序
        comments = dict(sorted_comments)
        print("parse finish")
        return comments, title
    except:
        print("parse error")
        print(traceback.format_exc())


def validateTitle(title):
    re_str = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(re_str, "_", title)  # 替换为下划线
    return new_title


def timeFormatter(param):
    minute = int(param) // 60
    second = float(param) - minute * 60
    return f'{str(minute).zfill(2)}:{str(second).zfill(5)}'

def getCounts(response):
    soup = BeautifulSoup(response, 'html.parser', from_encoding='utf-8')  # 使用 BeautifulSoup 解析 HTML 内容
    # 获取视频标题
    title = soup.find('title', {'data-vue-meta': 'true'}).text.strip() 
    title = title.replace("_哔哩哔哩_bilibili", "")
    # print(title)
    desp = soup.find('meta', {'data-vue-meta': 'true', \
                              'itemprop': 'description', \
                                  'name': 'description'}) \
        .get('content').strip()
    
    intro = re.search(r'(.*),\s*视频播放量', desp).group(1).strip()
    # print(intro)
    # 使用正则表达式提取数字
    match = re.search(r'视频播放量 (\d+)、弹幕量 (\d+)、点赞数 (\d+)、投硬币枚数 (\d+)、收藏人数 (\d+)、转发人数 (\d+), 视频作者', desp)

    # 将提取到的数字按照顺序存储到对应的变量中
    if match:
        view = match.group(1)
        barrage = match.group(2)
        like = match.group(3)
        coin = match.group(4)
        star = match.group(5)
        share = match.group(6)
        print(view, barrage, like, coin, star, share)
    else:
        view, barrage, like, coin, star, share = 0, 0, 0, 0, 0, 0
        print("未能提取到足够的数字信息")
    # 获取视频标签
    tag_contents = soup.find('meta', {'data-vue-meta':'true', \
                                       'itemprop': 'keywords', \
                                           'name':'keywords'}) \
        .get('content').strip()
    title_len = len(title)
    tag = tag_contents[title_len+1:-20]
    # print(tag)
    
    # return title, duration, intro, tag, view, barrage, like, coin, star, share
    return intro, tag, view, barrage, like, coin, star, share


def getCrawlList(path):
    crawl_df = pd.read_excel(path)
    return crawl_df
    
def main():
    # id	vtype	uploader	title	url	
    # bv	duration	mint	sec	total_sec	
    # isPlace	place1	place2	place3	product	ptype
    crawl_path = '../data/data-crawl-list.xlsx'
    crawl_df = getCrawlList(crawl_path)
    print(f'data-crawl-list.xlsx 一共有 {crawl_df.shape[0]} 条数据\n\n')
    
    # 创建一个 comments.csv 收集弹幕
    bar_df = pd.DataFrame(columns=['bv', 'title', 'timing', 'bar_content'])
    bar_file_path = '../data/bars.csv'
    bar_df.to_csv(bar_file_path, header=True, index=False)
    
    # 创建一个 basic_info.csv 收集视频基本信息
    basic_df = pd.DataFrame(columns=['bv', 'title', 'duration', 'intro', 'tag', 'view', 'barrage', 'like', 'coin', 'star', 'share'])
    basic_file_path = '../data/basic_info.csv'
    basic_df.to_csv(basic_file_path, header=True, index=False)
    
    crawl_basic_cnt = 0
    crawl_bar_cnt = 0
    
    for index, row in crawl_df.iterrows():
        url = row['url']
        title = row['title']
        bv = row['bv']
        dur = row['total_sec']
        if(pd.isna(bv)):
            continue
        response = getHTML(url)
        try:
            intro, tag, view, barrage, like, coin, star, share = getCounts(response)
            basic_row_data = {'bv':bv, 'title':title, 'duration':dur, \
                          'intro': intro, 'tag': tag, 'view':view, \
                              'barrage':barrage, 'like':like, 'coin': coin, \
                                  'star':star, 'share':share}
            basic_row_df = pd.DataFrame([basic_row_data])
            basic_row_df.to_csv(basic_file_path, mode='a', header=False, \
                                index=False, encoding='utf-8-sig')
            crawl_basic_cnt += 1
        except:
            print(f'ERR ======> 视频 {bv} 爬取视频基本信息出错!')
            continue
        
        try:
            comments, _ = parsePage(response)
            if len(comments) == 0:
                print(f'已经保存 {bv} 一共 0 条弹幕\n\n')
                continue
            
            bar_row_df = pd.DataFrame({'bv':bv, 'title':title, \
                                       'timing': list(comments.keys()), \
                                           'bar_content': list(comments.values())})
            
            # bar_row_df.drop_duplicates(subset=['timing', 'text'], keep='first', inplace=True)
            
            bar_row_df.to_csv(bar_file_path, mode='a', header=False, \
                              index=False, encoding='utf-8-sig')
            crawl_bar_cnt += 1
            print(f'已经保存 {bv} 一共 {bar_row_df.shape[0]} 条弹幕\n\n')
        except:
            print(f'ERR ======> 视频 {bv} 爬取视频基本信息出错!')
            continue
            
    print("=============== finish all comments collection ============")
    print(f'INFO ======> 一共完成 {crawl_basic_cnt} 条 基本信息，{crawl_bar_cnt} 条视频的弹幕爬取')

    
if __name__ == '__main__':
    main()