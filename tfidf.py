# -*- coding: utf-8 -*-
import math
import json
import os
import pandas as pd
from data import Data


class Idf(object):
    """
    计算并存储 idf 字典。
    """
    def __init__(self, corpus):
        # corpus 是一个 dict，key为文件夹名
        self.corpus = corpus
        self.idf_dict = self._cal()

    def _cal(self):
        idf_dict = {}
        for d, docs in self.corpus.items():
            token_freq = {}
            doc_counts = len(docs)
            for index, doc in enumerate(docs):
                # 每10篇打印进度
                if index % 10 == 0:
                    print('正在计算文档 idf, {}/{}'.format(index + 1, doc_counts))
                for token in set(doc):
                    token_freq[token] = token_freq.get(token, 0) + 1
            # 计算每个词的 idf 值：math.log10(doc_counts / (val + 1))
            idf_dict[d] = {key: '%.10f' % math.log10(doc_counts / (val + 1)) for key, val in token_freq.items()}
            idf_dict[d] = dict(sort(idf_dict[d]))
        return idf_dict

    def save(self):
        for d in self.corpus.keys():
            idf_path = os.path.join(d, 'idf_dict.json')
            with open(idf_path, 'w', encoding='utf-8') as f:
                json.dump(self.idf_dict[d], f, ensure_ascii=False)
                # print(json.dumps(self.idf_dict, ensure_ascii=False))
            print('idf 字典已保存，路径：', idf_path)


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
    def __init__(self, corpus, idf_dict):
        """
        Args:
            corpus: list， 每个元素是一个分词后的文档词list
            idf_dict: idf字典
        """
        self.idf_dict = idf_dict
        self.corpus = corpus
        self.scores = self.cal()

    def cal(self):
        scores = []
        for doc in self.corpus:
            doc_score = self._cal_score(doc)
            scores.append(doc_score)
        return scores

    def _cal_score(self, doc):
        """
        计算每篇文档中词的 tf-idf 分数
        Args:
            doc: list，文档词汇列表

        Return:
            list, 每个元素为一个二元组，(token, score)，按分数从大到小排列
        """
        token_freq = pd.DataFrame(doc).iloc[:, 0].value_counts()
        # token_freq = token_freq.values / float(len(doc))
        token_freq = dict(zip(token_freq.index, token_freq.values / float(len(doc))))
        score = {key: '%.10f' % (float(val) * float(self.idf_dict.get(key, 0))) for key, val in token_freq.items()}
        return sort(score)

    def extract_key_words(self, topK):
        key_words = []
        for score in self.scores:
            key_words.append(dict(score[:topK]))
        return key_words


def main():
    # 语料数据预处理
    file_dir = './dataset/data'
    data = Data(file_dir)
    corpus = data.corpus
    idf = Idf(corpus)
    idf.save()


if __name__ == '__main__':
    main()
