# -*- coding: utf-8 -*-
import re


class Data(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_text = None
        self.corpus = self._load_data()

    def _load_data(self):
        """加载原始文档"""
        sentence = open(self.file_path, 'r', encoding='utf-8', errors='ignore').read()

        sentence = sentence.encode('utf-8').decode('utf-8-sig')
        sentence = re.sub('[0-9 ]', '', sentence.replace('\n', ''))
        return sentence
