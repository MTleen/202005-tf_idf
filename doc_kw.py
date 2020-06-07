# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import traceback
from data import Data
import argparse
from tfidf import Tfidf
from word2vec import WV
import json
import numpy as np
from jieba import analyse
import math


class DocKw(object):
    """
    构建 gui
    """

    def __init__(self):
        self.wv_model = None
        self.status = {}
        self.idf_dir = './dataset/data'
        self.idf_path = None
        self.root = tk.Toplevel()
        self.idf_root = None
        self.path_var = None

        self.doc_title = tk.Variable(self.root, value='文件内容展示')
        self.doc_panel = tk.Text(self.root, width=50, height=20)
        self.frm_kw = tk.Frame(self.root)
        self.frm_ours = tk.Frame(self.frm_kw)
        self.frm_jieba = tk.Frame(self.frm_kw)
        self.kw_ours_var = tk.Variable(self.frm_ours, value='Ours')
        self.kw_jieba_var = tk.Variable(self.frm_jieba, value='Jieba')
        self.kw_panel_ours = tk.Listbox(self.frm_ours, width=20, height=10)
        self.kw_panel_jieba = tk.Listbox(self.frm_jieba, width=20, height=10)
        self.doc_panel_r1 = tk.Text(self.root, width=50, height=10)
        self.doc_title_r1 = tk.Variable(self.root, value='文件内容展示')
        self.doc_title_r2 = tk.Variable(self.root, value='文件内容展示')
        self.doc_panel_r2 = tk.Text(self.root, width=50, height=10)
        self.show_sim_btn = tk.Button(self.root, text='展示相似度', command=self.show_similarity)
        self.sim_panel = tk.Listbox(self.root, width=50, height=10)

    def construct_gui(self):
        set_win_size(self.root, 400, 700)
        self.root.title('提取关键字')
        # 构建关键词提取模块界面
        tk.Label(self.root, text='关键词提取模块').pack()
        tk.Button(self.root, text='选择文件', command=lambda: self.reveal_doc('dp')).pack()
        tk.Label(self.root, textvariable=self.doc_title).pack()
        self.doc_panel.pack(padx=20)
        tk.Label(self.root, text='关键词展示').pack()
        tk.Button(self.root, text='生成关键词', command=self.refresh_key_words).pack()
        self.frm_kw.pack()
        self.frm_ours.pack(side='left', padx=10)
        tk.Label(self.frm_ours, textvariable=self.kw_ours_var).pack()
        self.kw_panel_ours.pack()
        self.frm_jieba.pack(side='right', padx=10)
        tk.Label(self.frm_jieba, textvariable=self.kw_jieba_var).pack()
        self.kw_panel_jieba.pack()

    def construct_sim_gui(self):
        # 相似度输出模块
        set_win_size(self.root, 400, 700)
        self.root.title('相似度对比')
        tk.Label(self.root, text='相似度输出模块').pack()
        tk.Button(self.root, text='选择文件 1', command=lambda: self.reveal_doc('dp_r1')).pack()
        tk.Label(self.root, textvariable=self.doc_title_r1).pack()
        self.doc_panel_r1.pack()

        tk.Button(self.root, text='选择文件 2', command=lambda: self.reveal_doc('dp_r2')).pack(pady=5)
        tk.Label(self.root, textvariable=self.doc_title_r2).pack()
        self.doc_panel_r2.pack()
        tk.Label(self.root, text='相似度').pack()
        self.show_sim_btn.pack(pady=5)
        self.sim_panel.pack(pady=10, padx=20)

    def reveal_doc(self, text_panel):
        """
        点击“选择文件”按钮调用此函数，获取文件路径，并将文档内容展示在相应的文本框中
        Args:
            text_panel: 'dp': 表示关键词展示模块中的text框
                        'dp_r1': 表示文档相似度对比模块中的第一个text框
                        'dp_r2': 表示文档相似度对比模块中的第二个text框
        """
        self.root.wm_attributes('-topmost', 0)
        if text_panel == 'dp':
            t = self.doc_panel
            title = self.doc_title
        elif text_panel == 'dp_r1':
            t = self.doc_panel_r1
            title = self.doc_title_r1
        elif text_panel == 'dp_r2':
            t = self.doc_panel_r2
            title = self.doc_title_r2
        file_path = filedialog.askopenfilename()
        print('file_path', file_path)
        # 判断是否选择了文件
        if not file_path:
            self.show_error('请选择正确的文件。')
            return
        try:
            # 先清除文本框
            t.delete('1.0', 'end')
            data = Data(file_path)
            title.set(os.path.split(file_path)[-1])
            print('file:', os.path.split(file_path)[-1])
            t.insert('end', data.corpus)
            # 计算 tf_idf score
            tf_idf = Tfidf(data.corpus, len(data.corpus) // 20)
            # 保存当前文档的data、tfidf对象，用于后续的提取关键词或者计算相似度
            self.status[text_panel] = {
                'data': data,
                'tfidf': tf_idf
            }
            if text_panel == 'dp':
                # 提取关键词模块，默认提取20个关键词
                self.kw_ours_var.set('Ours')
                self.kw_jieba_var.set('Jieba')
                self.kw_panel_jieba.delete(0, 'end')
                self.kw_panel_ours.delete(0, 'end')
            elif text_panel == 'dp_r1' or text_panel == 'dp_r2':
                # 当文档相似度模块选择新的文档时，清空相似度输出的文本框
                self.sim_panel.delete(0, 'end')
            self.root.wm_attributes('-topmost', 1)
        except Exception:
            traceback.print_exc()
            # messagebox.showerror(message=traceback.format_exc())

    def refresh_key_words(self):
        """
        点击”生成关键词“按钮调用词函数，会刷新关键词
        """
        try:
            topK = 20
            tf_idf = self.status['dp']['tfidf']
            data = self.status['dp']['data']
            self.kw_panel_jieba.delete(0, 'end')
            self.kw_panel_ours.delete(0, 'end')
            keywords = tf_idf.scores
            self.kw_ours_var.set('Ours({})'.format(len(keywords)))
            for key, val in keywords.items():
                self.kw_panel_ours.insert('end', '{}: {:.5f}'.format(key, float(val)))
            jieba_keywords = extract_kw(topK, data, is_jieba=True)[0]
            self.kw_jieba_var.set('Jieba({})'.format(len(jieba_keywords)))
            for key, val in jieba_keywords.items():
                self.kw_panel_jieba.insert('end', '{}: {:.5f}'.format(key, float(val)))
        except KeyError:
            self.show_error('请先选择文档。')
            traceback.print_exc()

    def show_similarity(self):
        """展示相似度，点击”显示相似度”按钮调用此函数“"""
        self.sim_panel.delete(0, 'end')
        # tf_idf 相似度计算
        tfidf_dpr1 = self.status['dp_r1']['tfidf']
        tfidf_dpr2 = self.status['dp_r2']['tfidf']
        data1 = self.status['dp_r1']['data']
        data2 = self.status['dp_r2']['data']
        wd1 = tfidf_dpr1.scores
        wd2 = tfidf_dpr2.scores
        vect1, vect2 = merge(wd1, wd2)
        print("关键词为：")
        for key in wd1.keys():
            print(key, end=' ')
        print("\n关键词为：")
        for key in wd2.keys():
            print(key, end=' ')
        print()
        print("\n两个文档的相似度为：")
        sim = cosine_similarity(vect1, vect2)
        print(sim)
        self.sim_panel.insert('end', '相似度：{:.5f}'.format(sim))

    def show_error(self, message):
        self.root.wm_attributes('-topmost', 0)
        messagebox.showerror(message=message)
        self.root.wm_attributes('-topmost', 1)


def set_win_size(panel, wid, hei):
    # 设置窗口大小
    win_width = wid
    win_height = hei
    # 获取屏幕分辨率
    screen_width = panel.winfo_screenwidth()
    screen_height = panel.winfo_screenheight()

    x = int((screen_width - win_width) / 2)
    y = int((screen_height - win_height) / 2)
    panel.geometry("%sx%s+%s+%s" % (win_width, win_height, x, y))
    # self.root.geometry("%sx%s" % (win_width, win_height))
    panel.resizable(0, 0)


def cosine_similarity(vect1, vect2):
    """
       计算两个向量之间的余弦相似度
       :param vect1: 向量 1
       :param vect2: 向量 2
       :return: sim
       """
    # 计算余弦相似度
    sum = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(vect1)):
        sum += vect1[i] * vect2[i]
        sq1 += pow(vect1[i], 2)
        sq2 += pow(vect2[i], 2)
    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0
    # print(result)
    return result


def extract_kw(topK, *entities, is_jieba=False):
    """
    提取关键词
    Args:
        topK: 提取前 topK 个关键词
        *entities: tuple, 每个元素是一个Tfidf对象或Data对象
        is_jieba: bool，表示是否是用jieba提取关键词

    Return：
        一个关键词字典的列表，字典的key是关键词，value是对应的tf-idf分数
    """
    kws = []
    for entity in entities:
        if is_jieba:
            # kw = dict(analyse.extract_tags(''.join(entity.corpus[0]), topK=topK, withWeight=True))
            kw = dict(analyse.extract_tags(entity.corpus, topK=topK, withWeight=True))
        else:
            kw = entity.extract_key_words(topK)[0]
        kws.append(kw)
    return kws


def merge(words1, words2):
    # 合并两个文档的词向量关键词词频词典，返回生成两个文档的关键词的词向量，用于计算相似度
    v1 = []
    v2 = []
    for key in words1:
        v1.append(words1[key])
        if key in words2:
            v2.append(words2[key])
        else:
            v2.append(0.0)
    for key in words2:
        if key not in words1:
            v2.append(words2[key])
            v1.append(0.0)
    return v1, v2
