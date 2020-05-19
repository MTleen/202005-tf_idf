# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import traceback
from data import Data
import argparse
from tfidf import Idf, Tfidf
from word2vec import WV
import json
import numpy as np
from jieba import analyse


class DocKw(object):
    """
    构建 gui
    """

    def __init__(self):
        self.wv_model = None
        self.status = {}
        self.idf_dir = './dataset/data'
        self.idf_path = None

        # self.root = tk.Tk()
        # self.frm = tk.Frame(self.root)
        # self.frm_l = tk.Frame(self.frm)
        self.root = tk.Toplevel()
        # self.frm_r = tk.Frame(self.frm)
        # self.menubar = tk.Menu(self.root)
        self.menubar = tk.Menu(self.root)
        self.idf_menu = tk.Menu(self.menubar, tearoff=0)
        self.idf_root = None
        self.path_var = None

        self.doc_title = tk.Variable(self.root, value='文件内容展示')
        self.doc_panel = tk.Text(self.root, width=50, height=20)
        self.frm_topk = tk.Frame(self.root)
        self.topk_var = tk.Variable(self.frm_topk)
        self.topk_entry = tk.Entry(self.frm_topk, textvariable=self.topk_var)
        self.frm_kw = tk.Frame(self.root)
        self.frm_ours = tk.Frame(self.frm_kw)
        self.frm_jieba = tk.Frame(self.frm_kw)
        self.kw_panel_ours = tk.Listbox(self.frm_ours, width=20, height=10)
        self.kw_panel_jieba = tk.Listbox(self.frm_jieba, width=20, height=10)
        self.doc_panel_r1 = tk.Text(self.root, width=50, height=10)
        self.doc_title_r1 = tk.Variable(self.root, value='文件内容展示')
        self.doc_title_r2 = tk.Variable(self.root, value='文件内容展示')
        self.doc_panel_r2 = tk.Text(self.root, width=50, height=10)
        self.show_sim_btn = tk.Button(self.root, text='展示相似度', command=self.show_similarity)
        self.sim_panel = tk.Listbox(self.root, width=50, height=10)

    def construct_gui(self):
        self.menubar.add_command(label='生成 idf 字典', command=self.gen_idf)
        self.root.config(menu=self.menubar)
        # 构建关键词提取模块界面
        tk.Label(self.root, text='关键词提取模块').pack()
        tk.Button(self.root, text='选择文件', command=lambda: self.reveal_doc('dp')).pack()
        tk.Label(self.root, textvariable=self.doc_title).pack()
        self.doc_panel.pack(padx=20)
        tk.Label(self.root, text='关键词展示').pack()
        self.frm_topk.pack(pady=10)
        self.topk_entry.pack(side='left')
        tk.Button(self.frm_topk, text='生成关键词', command=self.refresh_key_words).pack(side='right', padx=10)
        self.frm_kw.pack()
        self.frm_ours.pack(side='left', padx=10)
        tk.Label(self.frm_ours, text='Ours').pack()
        self.kw_panel_ours.pack()
        self.frm_jieba.pack(side='right', padx=10)
        tk.Label(self.frm_jieba, text='Jieba').pack()
        self.kw_panel_jieba.pack(pady=10)

    def construct_sim_gui(self):
        # 相似度输出模块
        self.menubar.add_command(label='生成 idf 字典', command=self.gen_idf)
        self.root.config(menu=self.menubar)
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
            messagebox.showinfo(message='请选择正确的文件。')
            return
        try:
            # 先清除文本框
            t.delete('1.0', 'end')
            data = Data(file_path)
            title.set(os.path.split(file_path)[-1])
            print('file:', os.path.split(file_path)[-1])
            t.insert('end', data.raw_text)
            # 加载 idf 字典
            idf = load_idf(self.idf_dir)
            # 计算 tf_idf score
            tf_idf = Tfidf(data.corpus, idf)
            # 保存当前文档的data、tfidf对象，用于后续的提取关键词或者计算相似度
            self.status[text_panel] = {
                'data': data,
                'tfidf': tf_idf
            }
            if text_panel == 'dp':
                # 提取关键词模块，默认提取20个关键词
                self.topk_var.set(20)
                self.refresh_key_words()
            elif text_panel == 'dp_r1' or text_panel == 'dp_r2':
                # if self.status.get('dp_r1', None) and self.status.get('dp_r2', None):
                #     self.show_similarity()
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
        topK = self.topk_var.get()
        try:
            topK = int(topK)
            tf_idf = self.status['dp']['tfidf']
            data = self.status['dp']['data']
            self.kw_panel_jieba.delete(0, 'end')
            self.kw_panel_ours.delete(0, 'end')
            keywords = extract_kw(topK, tf_idf, is_jieba=False)[0]
            for key, val in keywords.items():
                self.kw_panel_ours.insert('end', '{}: {:.5f}'.format(key, float(val)))
            jieba_keywords = extract_kw(topK, data, is_jieba=True)[0]
            for key, val in jieba_keywords.items():
                self.kw_panel_jieba.insert('end', '{}: {:.5f}'.format(key, float(val)))
        except ValueError:
            messagebox.showerror(message='请输入正确的 topK 值。')
            traceback.print_exc()
        except KeyError:
            messagebox.showerror(message='请先选择文档。')
            traceback.print_exc()
        # except Exception:
        #     messagebox.showerror(message=traceback.format_exc())

    def show_similarity(self):
        """展示相似度，点击”显示相似度”按钮调用此函数“"""
        self.sim_panel.delete(0, 'end')
        # 为了加快gui展示的速度，所以把加载模型的操作放到这里
        self.wv_model = WV('model\\model7.model')
        # tf_idf 相似度计算
        tfidf_dpr1 = self.status['dp_r1']['tfidf']
        tfidf_dpr2 = self.status['dp_r2']['tfidf']
        data1 = self.status['dp_r1']['data']
        data2 = self.status['dp_r2']['data']
        # tf-idf 相似度
        for topK in [20, 40, 200]:
            doc1_vec, doc2_vec = doc2vec_tfidf(topK, tfidf_dpr1, tfidf_dpr2)
            self.sim_panel.insert('end', '-' * 30)
            self.sim_panel.insert('end', 'tf-idf (topK={}): {:.5f}'.format(topK, cosine_similarity(doc1_vec, doc2_vec)))
            doc1_vec, doc2_vec = doc2vec_tfidf(20, data1, data2, is_jieba=True)
            # self.sim_panel.insert('end', '-' * 30)
            self.sim_panel.insert('end', 'jieba (topK={}): {:.5f}'.format(topK, cosine_similarity(doc1_vec, doc2_vec)))
        # word2vec 相似度计算
        doc1_vec = self.wv_model.doc2vec(data1.corpus[0])
        doc2_vec = self.wv_model.doc2vec(data2.corpus[0])
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end', 'word2vec (dim=300): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        # tfidf+wv 相似度计算
        doc1_kw, doc2_kw = extract_kw(20, tfidf_dpr1, tfidf_dpr2, is_jieba=False)
        doc1_vec = self.wv_model.doc2vec(list(doc1_kw.keys()))
        doc2_vec = self.wv_model.doc2vec(list(doc2_kw.keys()))
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end',
                              'tfidf+word2vec (dim=300, topK=20): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        # jieba+wv 相似度计算
        doc1_kw, doc2_kw = extract_kw(20, tfidf_dpr1, tfidf_dpr2, is_jieba=True)
        doc1_vec = self.wv_model.doc2vec(list(doc1_kw.keys()))
        doc2_vec = self.wv_model.doc2vec(list(doc2_kw.keys()))
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end',
                              'jieba+word2vec (dim=300, topK=20): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))

    def gen_idf(self):
        """
        点击“生成idf字典”按钮执行此函数，
        """
        self.idf_root = tk.Toplevel()
        self.idf_root.wm_attributes('-topmost', 1)
        self.idf_root.resizable(0, 0)
        self.idf_root.geometry('400x90')
        self.path_var = tk.Variable(self.idf_root, value='dataset\\data')
        self.idf_root.title('选择生成 idf 字典的文件夹。')
        tk.Label(self.idf_root, text='目标路径：').grid(row=0, column=0, padx=5)
        tk.Entry(self.idf_root, textvariable=self.path_var, width=35).grid(row=0, column=1)
        tk.Button(self.idf_root, text='选择路径', command=self.select_dir).grid(row=0, column=2, padx=10)
        tk.Button(self.idf_root, text='确定', command=self.confirm_dir).grid(row=1, column=1, pady=10)

    def select_dir(self):
        self.path_var.set(filedialog.askdirectory())

    def confirm_dir(self):
        self.idf_dir = self.path_var.get()
        self.idf_path = os.path.join(self.idf_dir, 'idf_dict.json')
        try:
            data = Data(self.idf_dir)
            corpus = data.corpus
            idf = Idf(corpus)
            idf.save()
            tk.messagebox.showinfo(message='idf 字典保存成功\n保存路径：{}'.format(self.idf_path))
            self.idf_root.destroy()
        except Exception:
            # tk.messagebox.showerror(message='请将文档放在 ".\\dataset\\data" 文件夹下，然后重试。')
            traceback.print_exc()


def load_idf(idf_dir):
    """
    加载idf字典
    Args:
        idf_dir: idf_dir所在文件夹，由选择的文件路径自动解析得到

    Return:
        idf 字典
    """
    print(idf_dir)
    idf_path = os.path.join(idf_dir, 'idf_dict.json')
    try:
        with open(os.path.join(idf_dir, 'idf_dict.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        tk.messagebox.showerror(message='idf 字典不存在，请先生成 idf 字典。'.format(idf_path))


def cosine_similarity(vec1, vec2):
    dot = np.sum(vec1 * vec2)
    dis = np.sqrt(np.sum(vec1 ** 2)) * np.sqrt(np.sum(vec2 ** 2))
    return dot / dis


def doc2vec_tfidf(topK, *args, is_jieba=False):
    """
    将文档转换为向量
    Args:
        topK: 关键词个数
        *args: 如果is_jieba为False，则为tfidf对象的列表，如果is_jieba为True，则为Data对象的列表
        is_jieba: 是否使用jieba提取关键词

    Return:
        文档向量 list
    """
    kw_set = set()
    # for arg in args:
    docs_kw = extract_kw(topK, *args, is_jieba=is_jieba)
    for kw in docs_kw:
        kw_set = kw_set.union(set(kw))
    docs_vec = []
    for i, _ in enumerate(args):
        doc_vec = []
        for kw in kw_set:
            doc_vec.append(float(docs_kw[i].get(kw, 0.)))
            # doc2_vec.append(float(kw_r2.get(kw, 0)))
        docs_vec.append(np.array(doc_vec))

    return docs_vec


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
            kw = dict(analyse.extract_tags(''.join(entity.corpus[0]), topK=topK, withWeight=True))
        else:
            kw = entity.extract_key_words(topK)[0]
        kws.append(kw)
    return kws
