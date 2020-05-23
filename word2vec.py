# -*- coding: utf-8 -*-
from gensim.models import word2vec
import numpy as np
import traceback
import pandas as pd
import os


class WV(object):
    """
    利用gensim包加载word2vec与训练模型，并生成相应的词向量
    """

    def __init__(self, model_path):
        """
        Args:
            model_path: 预训练模型的路径
        """
        self.model_path = model_path
        self.model = word2vec.Word2Vec.load(self.model_path)
        # self.token_counts, self.dim, self.vectors = self.load_model()

    # def load_model(self):
    #     """
    #     此函数暂时用不到，之前是为了测试不同与训练模型的效果。
    #     """
    #     csv_path = self.model_path + '.csv'
    #     if os.path.exists(csv_path):
    #         vectors = pd.read_csv(csv_path, index_col=0, header=None)
    #         token_counts, dim = vectors.shape
    #     else:
    #         with open(self.model_path, 'r', encoding='utf-8') as f:
    #             token_counts, dim = f.readline().strip().split(' ')
    #             vectors = pd.DataFrame(np.zeros([int(token_counts), int(dim)], dtype=np.float))
    #             i = 0
    #             tokens = []
    #             while 1:
    #                 line = f.readline()
    #                 if not line:
    #                     break
    #                 # if i > 5:
    #                 #     break
    #                 print('正在读取 w2v 向量：{}/{}'.format(i + 1, token_counts))
    #                 line = line.strip().split(' ')
    #                 # vectors[line[0]] = np.array(line[1:])
    #                 vec = pd.DataFrame(np.array(line[1:]).astype(np.float).reshape([1, -1]), index=[line[0]])
    #                 vec.to_csv(csv_path, encoding='utf-8', header=False, index=True, mode='a')
    #                 # vectors.iloc[i] = np.array(line[1:]).astype(np.float)
    #                 # tokens.append(line[0])
    #                 i += 1
    #
    #             vectors.index = tokens
    #
    #     return token_counts, dim, vectors

    # def get_vector(self, token):
    #     return self.vectors.loc[token].values

    def doc2vec(self, doc):
        """
        文档转向量
        Args:
            doc: 文章分词后的 list

        Return:
            文档向量，由所有词向量相加并取均值。
        """
        vec = None
        # 统计一篇文档的总词数
        actual_counts = 0
        # 遍历文档
        for token in doc:
            try:
                # 获取词向量
                token_vec = self.model.wv.get_vector(token)
                # token_vec = self.get_vector(token)
                vec = np.array(token_vec) if vec is None else vec + np.array(token_vec)
                actual_counts += 1
            except KeyError:
                traceback.print_exc()
                continue
        return vec / float(actual_counts)
