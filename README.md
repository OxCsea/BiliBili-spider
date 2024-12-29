# BiliBili-Spider

## 1. Introduction

基于视频BV爬取指定视频信息和弹幕内容。

- 视频基本信息。basic_info.csv：['bv', 'title', 'duration', 'intro', 'tag', 'view', 'barrage', 'like', 'coin', 'star', 'share'] 
  - duration：视频时长
  - intro：视频简介
  - tag：视频标签
  - barrage：弹幕数
-  视频弹幕信息。bars.csv：['bv', 'title', 'timing', 'text']
  - timing：弹幕出现的时刻

## 2. Environment 

Python=3.10.x

## 3. Structure

- code

  - bilibili-spider.py
    - 爬取B站视频基本信息和弹幕内容。
- data

  - data-crawl-list.xlsx
    - 要爬取的B站视频列表
- TODO： duration + 分p视频出bug

## 4. Usage

1. 整理要爬取的B站视频BV号存入data-crawl-list.xlsx
2. 运行bilibili-spider.py爬取对应B站视频信息

## 5. Contact

Created by [OxCsea](https://github.com/OxCsea) - feel free to reach out!

> https://t.me/magic_Cxsea