# -*- coding: utf-8 -*-
import math
import json
import os
import pandas as pd
from data import Data
import jieba
import jieba.posseg as psg


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
    # def __init__(self, corpus, idf_dict):
    def __init__(self, corpus, topK):

        """
        Args:
            corpus: list， 每个元素是一个分词后的文档词list
            idf_dict: idf字典
        """
        # self.idf_dict = idf_dict
        self.corpus = corpus
        self.scores = self.cal(topK)

    def cal(self, n):
        # scores = []
        # for doc in self.corpus:
        #     doc_score = self._cal_score(doc)
        #     scores.append(doc_score)
        # return scores

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

    # def _cal_score(self, doc):
    #     """
    #     计算每篇文档中词的 tf-idf 分数
    #     Args:
    #         doc: list，文档词汇列表
    #
    #     Return:
    #         list, 每个元素为一个二元组，(token, score)，按分数从大到小排列
    #     """
    #     token_freq = pd.DataFrame(doc).iloc[:, 0].value_counts()
    #     # token_freq = token_freq.values / float(len(doc))
    #     token_freq = dict(zip(token_freq.index, token_freq.values / float(len(doc))))
    #     score = {key: '%.10f' % (float(val) * float(self.idf_dict.get(key, 0))) for key, val in token_freq.items()}
    #     return sort(score)
    #
    # def extract_key_words(self, topK):
    #     key_words = []
    #     for score in self.scores:
    #         key_words.append(dict(score[:topK]))
    #     return key_words


def main():
    # 语料数据预处理
    file_dir = './dataset/data'
    data = Data(file_dir)
    corpus = data.corpus
    idf = Idf(corpus)
    idf.save()


if __name__ == '__main__':
    main()
