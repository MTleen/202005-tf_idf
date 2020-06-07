# -*- coding: utf-8 -*-
import math
import json
import os
import pandas as pd
from data import Data
import jieba
import jieba.posseg as psg


def sort(dic, reverse=True):
    """
    从大到小排序 dict
    Args:
        dic: 需要进行排序的字典
        reverse: bool, True 表示从大到小，False 表示从小到大

    Returns:
        排序好的 dict
    """
    dic = sorted(dic.items(), key=lambda item: item[1], reverse=reverse)
    return dic


class Tfidf(object):
    def __init__(self, corpus, topK):
        """
        Args:
            corpus: list， 每个元素是一个分词后的文档词list
            topK: 关键词个数
        """
        self.corpus = corpus
        self.scores = self.cal(topK)

    def cal(self, n):
        # 处理输入文档，对文档进行分词、去停用词、词性标注、位置标注
        # 生成词性词典、词频词典、词长词典，组合为TF权重
        # 调入特定语料的IDF字典，计算文档词语的TFIDF向量，返回前n个关键词的TFIDF向量

        jieba.load_userdict('dict.txt')
        words = psg.lcut(self.corpus)
        print(words)
        wlen = len(words)
        print(wlen)

        pos = {}  # 词性词典：词语：词性
        freq = {}  # 词频词典：词语：词频/文档词数
        #   loc = {}   #位置词典
        wl = {}  # 词长词典：词语，词长/最长的词长
        pf = {}  # 词性权值词典：词语：词性权值
        stopwords = [line.strip() for line in open('stopwords.txt', encoding='UTF-8').readlines()]
        max = 6  # 最长的分词词语，假设为6
        for key, p in words:
            if len(key.strip()) < 2:
                continue
            if key not in stopwords:
                pos[key] = p
                if p in ['n', 'nz']:
                    pf[key] = 0.5
                elif p in ['vd', 'vn', 'v']:
                    pf[key] = 0.3
                elif p in ['a', 'ad', 'an']:
                    pf[key] = 0.2
                else:
                    pf[key] = 0.0
                freq[key] = freq.get(key, 0) + 1 / wlen
                wl[key] = len(key) / max
        # print(pos)
        # print(pf)
        # print(wl)
        # print(freq)
        idf_file = 'idf.txt'
        idf = {}
        c = 0  # idf文档单词总数
        with open(idf_file, 'r', encoding='utf-8') as f:
            for line in f:
                word, f = line.strip().split(' ')
                idf[word] = float(f)
                c += 1
        idf_mean = sum(idf.values()) / c  # 平均idf值，填充新词的idf
        tfg = {}  # 组合的TF值：tfg=词频+词性权重+词长权重
        tf_idf = {}  # tfidf
        for key in pos:
            tfg[key] = freq[key] + pf[key] + wl[key]
            tf_idf[key] = tfg[key] * idf.get(key, idf_mean)
        # print(tf_idf)
        keywords = sorted(tf_idf.items(), key=lambda tf_idf: tf_idf[1], reverse=True)
        key = {}

        for i in range(n):
            k = keywords[i][0]

            f = keywords[i][1]

            key[k] = f

        return key
