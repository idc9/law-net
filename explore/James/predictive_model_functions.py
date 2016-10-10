import sys

sys.path.append('../../code/')
import os
import json
from datetime import datetime
import time
from math import *
import numpy as np
import pandas as pd
import igraph as ig
from collections import *
from load_data import load_citation_network_igraph, case_info

#takes a graph of cases and returns the min and max years in a tuple
def find_year_range(graph):
    min_year = 10000
    max_year = -1
    
    for v in graph.vs:
        year = v["year"]
        if year < min_year:
            min_year = year
        if year > max_year:
            max_year = year
    return (min_year, max_year)
 
#takes a graph and creates a subgraph for each year containing all vertices and edges explicitly before that year
def make_subgraph_dict(graph):
    time1 = time.time()
    
    subgraph_dict = {}
    min_year = find_year_range(graph)[0]
    max_year = find_year_range(graph)[1]    
    
    #for each year finds all vertices that have a year attrubute less than year i,
    #  makes a subgraph from those vertices, and adds that subgraph to a dict with year as the key
    for i in range (min_year,max_year+2):
        sub_vs = graph.vs.select(year_lt=i)
        sub_G = graph.subgraph(sub_vs)
        subgraph_dict[i] = sub_G

    time2 = time.time()
    print "Making sub-graph dict took " + str(time2-time1) + " seconds"
    return subgraph_dict
    
#determines the number of citing cases to a particular case that are within some year difference (threshold)
def time_decay_indegree(graph, vertex, threshold=10):
    td_indeg = 0
    vertex_year = vertex["year"]
    neighbors = graph.neighbors(vertex.index, mode='IN')
    #for each in-edge adds 1 to the count only if the year diff is less than the given threshold
    for neighbor in neighbors:
        neighbor_year = graph.vs[neighbor]["year"]
        if neighbor_year - vertex_year <= threshold:
            td_indeg += 1
    return td_indeg

#takes a dict of subgraphs by year and returns a dict of case tuples that contain info and that are sorted by a metric
#  current metrics supported are: indegree, pagerank, and timedecay (indegree with a time decay threshold)
def make_case_dict(subgraph_dict, metric="indegree"):
    time1 = time.time()

    past_cases_dict = {}
    min_year = sorted(subgraph_dict.keys())[0]
    max_year = sorted(subgraph_dict.keys())[-1]
    
    #for each year multiple list are filled and zipped together to form a list of tuples
    for i in range (min_year,max_year+1):
        sub_G = subgraph_dict[i]

        tuple_list = []
        igraph_subg_index_list = []
        name_list = []
        year_list = []
        metric_list = []
        
        #pagerank metric calculates a list of values for all vertices
        if metric == "pagerank":
            metric_list = sub_G.pagerank()
        
        #goes through all vertices in the subgraph and adds info to lists
        for j in range(0,len(sub_G.vs)):
            vertex = sub_G.vs[j]
            igraph_subg_index_list.append(vertex.index)
            name_list.append(vertex['name'])
            year_list.append(vertex['year'])
            
            #these two metrics calculate value for each individual vertex 
            if metric == "indegree":
                metric_list.append(vertex.indegree())
            if metric == "timedecay":
                metric_list.append(time_decay_indegree(sub_G, vertex, 10))
        
        tuple_list = zip(igraph_subg_index_list, name_list, year_list, metric_list)

        #sorts the tuples by their metric value so each case's rank is now its index + 1
        sorted_tuple_list = sorted(tuple_list, key=lambda tup: tup[3], reverse=True)

        past_cases_dict[i] = sorted_tuple_list

    time2 = time.time()
    print "Making past case dict for " + metric + " took " + str(time2-time1) + " seconds"
    return past_cases_dict
    
#produces a score for a particular case based on the metric that the past_case_dict is sorted by
def calculate_score_for_case(graph, case_index, past_cases_dict):
    all_past_cases = past_cases_dict[graph.vs[case_index]['year']]
    
    #finds the neighbors the particular case points to and creates a list of their court_listener names
    neighbors = graph.neighbors(case_index, mode='OUT')
    neighbors_names = [graph.vs[i]['name'] for i in neighbors]
    
    #finds the ranks of all neighbors that are in the sub_graph of cases before the case's year
    #  (so cases with the same year as the particular case will not be found)
    ranks = [i+1.0 for i, v in enumerate(all_past_cases) if v[1] in neighbors_names]

    #calculates scores based on rank and total number of ases before
    scores = []
    for some_rank in ranks:
        some_score = 1 - some_rank/len(all_past_cases)
        scores.append(some_score)
    
    #sums up scores to find the final score for the case
    final_score = sum(scores)
    return final_score
    
#finds the total score for all cases in a graph based on the metric of the past_case_dict
def calculate_score_from_case_dict(graph, past_case_dict):
    time1 = time.time()
    
#combines all the functions to calculate the score of a supported metric from just the original graph
def calculate_metric_score_from_graph(graph, metric="indegree"):
    subgraph_dict = make_subgraph_dict(graph)
    case_dict = make_case_dict(subgraph_dict, metric)
    metric_score = calculate_score_from_case_dict(G, case_dict)
    return metric_score

    metric_score = 0
    for i in graph.vs():
        metric_score += calculate_score_for_case(graph, i.index, past_case_dict)

    time2 = time.time()
    print "Total score was: " + str(metric_score)
    print "This took " + str(time2-time1) + " seconds"
    return metric_score