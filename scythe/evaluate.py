""" Contains classes for evaluating abbreviated measures. """

import numpy as np
import abc
from scythe.base import Measure



class Evaluator(object):
    ''' Base Evaluator class. '''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def evaluate(self, measure, individual):
        """ Apply the loss function to the AbbreviatedMeasure produced by 
        selecting the passed items from the passed measure.
        Args:
            measure: a Measure instance to abbreviate and evaluate.
            individual: the individual/chromosome to evaluate.
        """



class YarkoniEvaluator(Evaluator):


    def __init__(self, item_cost=0.05):

        self.item_cost = item_cost


    def evaluate(self, measure, weights=None):

        # Compute R^2
        d = measure.dataset
        pred_y = np.dot(d.X, measure.key)
        r_squared = (np.corrcoef(d.y, pred_y, rowvar=0)[0:measure.n_y, measure.n_y::] ** 2).diagonal()

        # Item cost: just the scaled number of items kept
        used = measure.key.any(axis=1)
        item_cost = np.sum(used) * self.item_cost

        # Compute variance cost--just mean variance unaccounted for in each scale
        if weights is not None:
            r_squared *= weights
        variance_cost = measure.n_y - np.sum(r_squared)

        return float(item_cost + variance_cost)

