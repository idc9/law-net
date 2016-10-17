import sys
import os
import json
from datetime import datetime
import time
from math import *

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

import igraph as ig

from collections import *

#takes a numpy adjacency matrix and returns the pagerank of the vertices
#all variable names follow along MLPP 17.34
#please note: the eigen vector that is returned is normalized, this is not the case for igraph.pagerank(),
#but this pagerank is proportional to igraph's pagerank
def PageRank(A):
    #the adjacency matrix used by MLPP is defined as Gij = 1 iff j points to i. This requires the transposed A.
    G = A.getT()
    n = A.shape[0]
    p = 0.85
    delta = (1.0-p)/n

    #vector which represents the outdegree of each vertex
    c = np.matrix(np.zeros((n,1)))
    for j in range(0,n):
        outdegree = np.sum(G[:,j])
        c[j] = outdegree

    #below these variable represent the decomposition of the transition matrix M
    D = np.matrix(np.zeros((n, n)))
    for j in range(0,n):
        if not c[j] == 0:
            D[j,j] = 1.0/c[j]
        else:
            D[j,j] = 0
 
    z = np.matrix(np.zeros((n,1)))
    for j in range(0,n):
        if not c[j] == 0:
            z[j] = delta
        else:
            z[j] = 1.0/n
    zT = z.getT()

    #variables are combined to produce M
    M = p*G*D + 1*zT

    #Power method to derive the first eigen-vector
    v = np.matrix(np.ones((n,1)))
    v = v/np.linalg.norm(v)
    iterations = 0
    converged = False
    while not converged:
        iterations += 1
        tmp = M*v
        norm = np.linalg.norm(tmp)
        new_v = tmp/norm
        
        difference = np.absolute(np.sum(v-new_v))
        if difference < 0.00001:
            converged = True
        
        v = new_v
        
    return v