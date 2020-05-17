# -*- coding: utf-8 -*-
import os
import re
import time
import jieba
from tkinter import messagebox


class Data(object):
    def __init__(self, file_dir):
        self.file_dir = file_dir
        self.raw_text = None
        with open('./dataset/stopwords.txt', 'r', encoding='utf-8') as f:
            self.stopwords = f.read().strip().split('\n')
        self.corpus = self._data_prepro()

    # @staticmethod
    # def _str2uni(doc):
    #     """将语料统一编码格式为 utf-8"""
    #
    #     return doc

    def _load_data(self, file_path, d):
        """加载原始文档"""
        try:
            with open(os.path.join(d, file_path), 'r', encoding='utf-8') as f:
                doc = f.read().strip().replace(' ', '')
                if not os.path.isdir(self.file_dir):
                    self.raw_text = doc
                # doc = self._str2uni(doc)
            return doc
        except Exception:
            messagebox.showerror(message='{} 无法打开，请重新选择。'.format(os.path.join(d, file_path)))

    def _data_prepro(self):
        # corpus = {}
        # for d in self.file_dir:
        if os.path.isdir(self.file_dir):
            print('正在读取文件夹：', self.file_dir)
            corpus = {self.file_dir: []}
            for file_path in os.listdir(self.file_dir):
                if not os.path.splitext(file_path)[-1] == '.txt':
                    continue
                doc = self._corpora_per_doc(file_path=file_path, file_dir=self.file_dir)
                corpus[self.file_dir].append(doc)
        elif os.path.exists(self.file_dir):
            print('正在读取文件：', self.file_dir)
            corpus = [self._corpora_per_doc(self.file_dir)]
        else:
            raise FileExistsError
        return corpus

    @staticmethod
    def _cut(doc):
        doc = re.sub('[a-z0-9A-Z]', '', doc.replace('\n', ''))
        return jieba.cut(doc, cut_all=False)

    def _corpora_per_doc(self, file_path, file_dir=''):
        doc = self._load_data(file_path=file_path, d=file_dir)
        doc = self._cut(doc)
        return [token for token in doc if token not in self.stopwords]
