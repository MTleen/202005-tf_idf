# -*- coding: utf-8 -*-
from gensim.models import word2vec
import numpy as np
import traceback


class WV(object):
    def __init__(self, model_path):
        self.model = word2vec.Word2Vec.load(model_path)

    def doc2vec(self, doc):
        vec = None
        actual_counts = 0
        for token in doc:
            try:
                token_vec = self.model.wv.get_vector(token)
                vec = token_vec if vec is None else vec + token_vec
                actual_counts += 1
            except KeyError:
                traceback.print_exc()
                continue
        return vec / float(actual_counts)
