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


class Gui(object):
    def __init__(self):
        self.wv_model = WV('model\\model7.model')
        self.status = {}
        self.root = tk.Tk()
        self.frm = tk.Frame(self.root)
        self.frm_l = tk.Frame(self.frm)
        self.frm_r = tk.Frame(self.frm)
        self.menubar = tk.Menu(self.root)
        self.idf_menu = tk.Menu(self.menubar, tearoff=0)
        self.doc_title = tk.Variable(self.frm_l, value='文件内容展示')
        self.doc_panel = tk.Text(self.frm_l, width=50, height=20)
        self.frm_topk = tk.Frame(self.frm_l)
        self.topk_var = tk.Variable(self.frm_topk)
        self.topk_entry = tk.Entry(self.frm_topk, textvariable=self.topk_var)
        self.frm_kw = tk.Frame(self.frm_l)
        self.frm_ours = tk.Frame(self.frm_kw)
        self.frm_jieba = tk.Frame(self.frm_kw)
        self.kw_panel_ours = tk.Listbox(self.frm_ours, width=20, height=10)
        self.kw_panel_jieba = tk.Listbox(self.frm_jieba, width=20, height=10)
        self.doc_panel_r1 = tk.Text(self.frm_r, width=50, height=10)
        self.doc_title_r1 = tk.Variable(self.frm_l, value='文件内容展示')
        self.doc_title_r2 = tk.Variable(self.frm_l, value='文件内容展示')
        self.doc_panel_r2 = tk.Text(self.frm_r, width=50, height=10)
        self.show_sim_btn = tk.Button(self.frm_r, text='展示相似度', command=self.show_similarity)
        self.sim_panel = tk.Listbox(self.frm_r, width=50, height=10)

    def construct_gui(self):
        """构建 GUI"""
        self.root.title('TFIDF')
        self.root.geometry('900x700')
        # 定义三个框架 frame
        self.frm.pack()
        self.frm_l.pack(side='left', padx=40)
        self.frm_r.pack(side='right', padx=40)
        # self.menubar.add_cascade(label='idf', menu=self.idf_menu)
        self.menubar.add_command(label='生成 idf 字典', command=self._gen_idf)
        self.root.config(menu=self.menubar)
        # 构建关键词提取模块界面
        tk.Label(self.frm_l, text='关键词提取模块').pack()
        tk.Button(self.frm_l, text='选择文件', command=lambda: self.reveal_doc('dp')).pack()
        tk.Label(self.frm_l, textvariable=self.doc_title).pack()
        self.doc_panel.pack()
        tk.Label(self.frm_l, text='关键词展示').pack()
        self.frm_topk.pack(pady=10)
        self.topk_entry.pack(side='left')
        tk.Button(self.frm_topk, text='生成关键词', command=self.refresh_key_words).pack(side='right', padx=10)
        self.frm_kw.pack()
        self.frm_ours.pack(side='left', padx=10)
        tk.Label(self.frm_ours, text='Ours').pack()
        self.kw_panel_ours.pack()
        self.frm_jieba.pack(side='right', padx=10)
        tk.Label(self.frm_jieba, text='Jieba').pack()
        self.kw_panel_jieba.pack()

        # 相似度输出模块
        tk.Label(self.frm_r, text='相似度输出模块').pack()
        tk.Button(self.frm_r, text='选择文件 1', command=lambda: self.reveal_doc('dp_r1')).pack()
        tk.Label(self.frm_r, textvariable=self.doc_title_r1).pack()
        self.doc_panel_r1.pack()

        tk.Button(self.frm_r, text='选择文件 2', command=lambda: self.reveal_doc('dp_r2')).pack(pady=5)
        tk.Label(self.frm_r, textvariable=self.doc_title_r2).pack()
        self.doc_panel_r2.pack()
        tk.Label(self.frm_r, text='相似度').pack()
        self.show_sim_btn.pack(pady=5)
        self.sim_panel.pack()

        self.root.mainloop()

    def reveal_doc(self, text_panel):
        """
        点击“选择文件”按钮调用此函数
        """
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
            idf = load_idf(os.path.dirname(file_path))
            # 计算 tf_idf score
            tf_idf = Tfidf(data.corpus, idf)
            self.status[text_panel] = {
                'data': data,
                'tfidf': tf_idf
            }
            if text_panel == 'dp':
                self.topk_var.set(20)
                self.refresh_key_words()
            # elif text_panel == 'dp_r1' or text_panel == 'dp_r2':
            #     if self.status.get('dp_r1', None) and self.status.get('dp_r2', None):
            #         self.show_similarity()
        except Exception:
            traceback.print_exc()
            messagebox.showerror(message=traceback.format_exc())

    def refresh_key_words(self):
        topK = self.topk_entry.get()
        try:
            topK = int(topK)
            tf_idf = self.status['dp']['tfidf']
            doc = self.status['dp']['data'].corpus[0]
            self.kw_panel_jieba.delete(0, 'end')
            self.kw_panel_ours.delete(0, 'end')
            keywords = tf_idf.extract_key_words(topK)[0]
            for key, val in keywords.items():
                self.kw_panel_ours.insert('end', '{}: {:.5f}'.format(key, float(val)))
            jieba_keywords = analyse.extract_tags(''.join(doc), topK=topK, withWeight=True)
            for key, val in jieba_keywords:
                self.kw_panel_jieba.insert('end', '{}: {:.5f}'.format(key, float(val)))
        except ValueError:
            messagebox.showerror(message='请输入正确的 topK 值。')
            # traceback.print_exc()
            return
        except KeyError:
            messagebox.showerror(message='请先选择文档。')
            # traceback.print_exc()
            return
        except Exception:
            messagebox.showerror(message=traceback.format_exc())

    def show_similarity(self):
        self.sim_panel.delete(0, 'end')
        # tf_idf 相似度计算
        tfidf_dpr1 = self.status['dp_r1']['tfidf']
        tfidf_dpr2 = self.status['dp_r2']['tfidf']
        # 20 个关键词
        doc1_vec, doc2_vec = doc2vec_tfidf(20, tfidf_dpr1, tfidf_dpr2)
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end', 'tf-idf (topK=20): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        print('-' * 30)
        print('tfidf (topK=20): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        # 30 个关键字
        doc1_vec, doc2_vec = doc2vec_tfidf(30, tfidf_dpr1, tfidf_dpr2)
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end', 'tf-idf (topK=30): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        print('-' * 30)
        print('tfidf (topK=30): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        # 300 个关键字
        doc1_vec, doc2_vec = doc2vec_tfidf(300, tfidf_dpr1, tfidf_dpr2)
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end', 'tf-idf (topK=300): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        print('-' * 30)
        print('tfidf (topK=300): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        # word2vec 相似度计算
        doc1 = self.status['dp_r1']['data'].corpus[0]
        doc2 = self.status['dp_r2']['data'].corpus[0]
        doc1_vec = self.wv_model.doc2vec(doc1)
        doc2_vec = self.wv_model.doc2vec(doc2)
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end', 'word2vec (dim=300): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        print('-' * 30)
        print('word2vec (dim=300): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        # tfidf+wv 相似度计算
        doc1_kw = list(tfidf_dpr1.extract_key_words(20)[0].keys())
        doc2_kw = list(tfidf_dpr2.extract_key_words(20)[0].keys())
        doc1_vec = self.wv_model.doc2vec(doc1_kw)
        doc2_vec = self.wv_model.doc2vec(doc2_kw)
        self.sim_panel.insert('end', '-' * 30)
        self.sim_panel.insert('end',
                              'tfidf+word2vec (dim=300, topK=20): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))
        print('-' * 30)
        print('tfidf+word2vec (dim=300, topK=20): {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))

    @staticmethod
    def _gen_idf():
        try:
            data = Data('dataset/data')
            corpus = data.corpus
            idf = Idf(corpus)
            idf.save()
            tk.messagebox.showinfo(message='idf 字典保存成功\n保存路径：.\\dataset\\data\\idf_dict.json')
        except Exception:
            tk.messagebox.showerror(message='请将文档放在 ".\\dataset\\data" 文件夹下，然后重试。')


def load_idf(idf_dir):
    with open(os.path.join(idf_dir, 'idf_dict.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def cosine_similarity(vec1, vec2):
    dot = np.sum(vec1 * vec2)
    dis = np.sqrt(np.sum(vec1 ** 2)) * np.sqrt(np.sum(vec2 ** 2))
    return dot / dis


def doc2vec_tfidf(topK, *args):
    kw_set = set()
    docs_kw = []
    for tfidf in args:
        kw = tfidf.extract_key_words(topK)[0]
        docs_kw.append(kw)
        # kw_r2 = tfidf_dpr2.extract_key_words(20)[0]
        kw_set = kw_set.union(set(kw))
    docs_vec = []
    for i, _ in enumerate(args):
        doc_vec = []
        for kw in kw_set:
            doc_vec.append(float(docs_kw[i].get(kw, 0.)))
            # doc2_vec.append(float(kw_r2.get(kw, 0)))
        docs_vec.append(np.array(doc_vec))
    return docs_vec


def main():
    # topK, doc_num

    # 语料数据预处理
    # file_path = './dataset/data/key1_4.txt'
    # data = Data('./dataset/data')
    # corpus = data.corpus
    # idf = Idf(corpus)
    # idf.save()
    # idf = load_idf(os.path.dirname(file_path))
    # data = Data('./dataset/data/key1_4.txt')
    # tf_idf = Tfidf(data.corpus, idf)
    # tfidf_scores = tf_idf.scores
    # keywords = tf_idf.extract_key_words(5)
    gui = Gui()
    gui.construct_gui()


if __name__ == '__main__':
    main()
