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

docpanel_status = {}


def construct_gui():
    """构建 GUI"""
    root = tk.Tk()
    root.title('TFIDF')
    root.geometry('800x700')
    # 定义三个框架 frame
    frm = tk.Frame(root)
    frm.pack()
    frm_l = tk.Frame(frm)
    frm_l.pack(side='left', padx=40)
    frm_r = tk.Frame(frm)
    frm_r.pack(side='right', padx=40)

    def reveal_doc(text_panel):
        """
        点击“选择文件”按钮调用此函数
        """
        if text_panel == 'dp':
            t = doc_panel
        elif text_panel == 'dp_r1':
            t = doc_panel_r1
        elif text_panel == 'dp_r2':
            t = doc_panel_r2
        file_path = filedialog.askopenfilename()
        print('file_path', file_path)
        # 判断是否选择了文件
        if not file_path:
            messagebox.showinfo(message='请选择正确的文件。')
            return
        try:
            # 先清除文本框
            t.delete('1.0', 'end')
            # key_word_panel.delete(0, 'end')

            data = Data(file_path)
            t.insert('end', data.raw_text)
            # 加载 idf 字典
            idf = load_idf(os.path.dirname(file_path))
            # 计算 tf_idf score
            tf_idf = Tfidf(data.corpus, idf)
            docpanel_status[text_panel] = {
                'data': data,
                'tfidf': tf_idf
            }
            if text_panel == 'dp':
                refresh_key_words(20)
            elif text_panel == 'dp_r1' or text_panel == 'dp_r2':
                if docpanel_status.get('dp_r1', None) and docpanel_status.get('dp_r2', None):
                    show_similarity(docpanel_status['dp_r1']['data'].corpus[0],
                                    docpanel_status['dp_r2']['data'].corpus[0])
            # keywords = tf_idf.extract_key_words(5)
            # for key, val in keywords[0].items():
            #     key_word_panel.insert('end', '{}: {:.5f}'.format(key, float(val)))
        except Exception:
            traceback.print_exc()
            messagebox.showerror(message=traceback.format_exc())

    def refresh_key_words(topK=None):
        if topK is None:
            topK = topk_entry.get()
        try:
            topK = int(topK)
        except Exception:
            messagebox.showerror(message='请输入正确的 topK 值。')
            return
        tf_idf = docpanel_status['dp']['tfidf']
        key_word_panel.delete(0, 'end')
        keywords = tf_idf.extract_key_words(topK)
        for key, val in keywords[0].items():
            key_word_panel.insert('end', '{}: {:.5f}'.format(key, float(val)))

    def show_similarity(doc1, doc2):
        sim_panel.delete(0, 'end')
        # tf_idf 相似度计算

        # word2vec 相似度计算
        wv_model = WV('model\\model7.model')
        doc1_vec = wv_model.doc2vec(doc1)
        doc2_vec = wv_model.doc2vec(doc2)
        sim_panel.insert('end', 'word2vec: {:.5f}'.format(cosine_similarity(doc1_vec, doc2_vec)))

    # 构建关键词提取模块界面
    tk.Label(frm_l, text='关键词提取模块').pack()
    doc_panel = tk.Text(frm_l, width=50, height=20)
    tk.Button(frm_l, text='选择文件', command=lambda: reveal_doc('dp')).pack()
    tk.Label(frm_l, text='文件内容展示').pack()
    doc_panel.pack()
    tk.Label(frm_l, text='关键词展示').pack()
    frm_topk = tk.Frame(frm_l)
    frm_topk.pack(pady=10)
    topk_entry = tk.Entry(frm_topk, text=5)
    topk_entry.pack(side='left')
    topk_button = tk.Button(frm_topk, text='生成关键词', command=refresh_key_words)
    topk_button.pack(side='right', padx=10)
    key_word_panel = tk.Listbox(frm_l, width=30, height=10)
    key_word_panel.pack()

    # 相似度输出模块
    tk.Label(frm_r, text='相似度输出模块').pack()
    doc_panel_r1 = tk.Text(frm_r, width=50, height=10)
    tk.Button(frm_r, text='选择文件 1', command=lambda: reveal_doc('dp_r1')).pack()
    tk.Label(frm_r, text='文件内容展示').pack()
    doc_panel_r1.pack()

    doc_panel_r2 = tk.Text(frm_r, width=50, height=10)
    tk.Button(frm_r, text='选择文件 2', command=lambda: reveal_doc('dp_r2')).pack(pady=5)
    tk.Label(frm_r, text='文件内容展示').pack()
    doc_panel_r2.pack()
    tk.Label(frm_r, text='相似度').pack()
    sim_panel = tk.Listbox(frm_r, width=30, height=10)
    sim_panel.pack()

    root.mainloop()


def load_idf(idf_dir):
    with open(os.path.join(idf_dir, 'idf_dict.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def cosine_similarity(vec1, vec2):
    dot = np.sum(vec1 * vec2)
    dis = np.sqrt(np.sum(vec1 ** 2)) * np.sqrt(np.sum(vec2 ** 2))
    return dot / dis


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
    construct_gui()


if __name__ == '__main__':
    main()
