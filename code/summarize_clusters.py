import numpy as np
import re
from collections import OrderedDict

def get_top_n_clusters(n, total_number_clusters, graph_clusters):
    """
    for modularity/walktrap:
    ------------------------
        prints summary of top 'n' clusters
        returns dictionary of top n clusters
            (key = cluster #, value = list of opinions)
    
    parameters
    -----------
        n = number of top clusters
        total_number_clusters = total number of clusters from clustering algorithm
        graph_clusters = pd.Series form of graph_clusters
    """
    
    clusters_size =[]
    for i in range(0,total_number_clusters):
        cluster_i = graph_clusters[graph_clusters == i].index.tolist() # list of opinions in cluster i
        clusters_size.append((i,len(cluster_i))) # (cluster #, size_of_cluster)

    # descending sort by size of cluster
    clusters_size = sorted(clusters_size, key=lambda x: x[1], reverse=True)

    # get top 'n' biggest clusters
    biggest_clusters = []
    for i in clusters_size:
        biggest_clusters.append(i[0])
    biggest_clusters = biggest_clusters[0:n]

    # summarize top 'n' biggest clusters
    for i in clusters_size[0:n]:
        print "cluster", i[0], ":", i[1], "opinions"

    clusters_dict = OrderedDict()
    for i in clusters_size[0:n]:
        cluster_i = graph_clusters[graph_clusters == i[0]].index.tolist() # list of opinions in cluster i
        clusters_dict[i[0]] = cluster_i

    return clusters_dict, biggest_clusters

def sort_coo(m): # helper function
    '''
    iterating through a csr (compressed sparse row) matrix:
    (row_index, column_index) tf_idf_value
    
    return a list of tuples (row, column, value), sorted by tf-idf values in descending order
    '''
    m = m.tocoo()
    list_of_tuples = []
    for i,j,k in zip(m.row, m.col, m.data):
        list_of_tuples.append((i,j,k)) # list of tuples
    return sorted(list_of_tuples, key=lambda x: x[2], reverse=True) # sort by tfidf values (descending)

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def all_opinions(file_paths): # helper function
    '''
    Get list of all opinions/text files from the (.txt) file paths
    '''
    
    all_opinions = []
    for i in file_paths:
        num = re.search(r'(\d+)', i)
        num = num.group()
        all_opinions.append(num)
    
    # sort the list
    all_opinions = map(int, all_opinions) # convert all elements of list into type(int)
    all_opinions.sort()
    
    # convert list back to list of strings
    all_opinions = map(str, all_opinions)
    
    return all_opinions



####################### Summarize Cluster 1 #######################
def top_k_words(opinions, num_words, tfidf_matrix, op_id_to_bow_id, vocab):
    """
    This function summarizes a set of opinions by returning the words that appear in these opinions with the highest tf-idf scores.

    Parameters
    -----------
    opinions: list of opinion ids
    num_words: number of words to return as the summary
    tfidf_matrix: the tf-idf matrix of all SCOTUS opinions
    op_id_to_bow_id: dict that maps opinion ids to rows of the tfidf matrix

    Output
    -------
    a list of the words with highest tf-idf scores amount the given opinions
    """
    
    # op_id_to_bow_id['opinion_id'] = 'row_index'
    
    vocab = np.array(vocab)
    n = num_words
    row_indices = []
    
    # get row indices corresponding to the opinions
    for each_opinion in opinions:
        row_index = op_id_to_bow_id[each_opinion]
        row_indices.append(row_index)
    
    # construct matrix with rows (opinions) from cluster
    new_matrix = tfidf_matrix[row_indices, :]
    
    # return the matrix as sorted listed-of-tuples (descending sort by tf-idf values)
    sorted_matrix = sort_coo(new_matrix)
    
    # get the unique column indices
    column_ind = [x[1] for x in sorted_matrix]
    column_ind = f7(column_ind) # unique and same ordering
    
    # get the words from column indices
    top_words = vocab[column_ind].tolist()[:n]
    return top_words



####################### Summarize Cluster 2 #######################
def top_k_words_from_mean_vector(opinions, num_words, tfidf_matrix, op_id_to_bow_id, vocab):
    '''
    compute the mean tf-idf vector of the cluster, return the top K words from this mean vector
    '''
    
    # op_id_to_bow_id['opinion_id'] = 'row_index'

    vocab = np.array(vocab)
    n = num_words
    row_indices = []
    
    # get row indices corresponding to the opinions
    for each_opinion in opinions:
        row_index = op_id_to_bow_id[each_opinion]
        row_indices.append(row_index)
    
    # construct a matrix with rows (opinions) from cluster
    new_matrix = tfidf_matrix[row_indices, :]
    
    # to take the mean of each col (use axis=1 to take mean of each row)
    mean_matrix = new_matrix.mean(axis=0) # 1 X 567570 row matrix 
    
    # get the column indices
    column_ind = np.argsort(mean_matrix, axis=1)[:, ::-1] # descending order
    
    # get the words from column indices
    top_words = vocab[column_ind].tolist()[0][:n]
    return top_words



####################### Summarize Cluster 3 #######################
def top_k_words_from_difference(opinions, all_opinions, num_words, tfidf_matrix, op_id_to_bow_id, vocab):
    '''
    compute the mean tf-idf vector of the cluster and also of the complement of the cluster, 
    take the difference mu_cluster - mu_complement, return the top K words in this difference    
    '''
    
    # op_id_to_bow_id['opinion_id'] = 'row_index'
    
    vocab = np.array(vocab)
    n = num_words
    row_indices = []
    
    # get row indices corresponding to the opinions
    for each_opinion in opinions:
        row_index = op_id_to_bow_id[each_opinion]
        row_indices.append(row_index)
    
    # construct a matrix with rowss (opinions) from cluster
    cluster_matrix = tfidf_matrix[row_indices, :]

    # to take the mean of each col (use axis=1 to take mean of each row)
    mean_matrix = cluster_matrix.mean(axis=0) # 1 X 567570 row matrix
    
    
    
    # complement of cluster (all the other opinions)
    opinions_compl = [x for x in all_opinions if x not in opinions]
    
    # get row indices corresponding to complement of cluster
    row_indices_compl = []
    for each_opinion in opinions_compl:
        row_index = op_id_to_bow_id[each_opinion]
        row_indices_compl.append(row_index)
    
    # construct a matrix with rows (opinions) from complement of cluster
    compl_matrix = tfidf_matrix[row_indices_compl, :]
    
    # to take the mean of each col (use axis=1 to take mean of each row)
    mean_matrix_compl = compl_matrix.mean(axis=0) # 1 X 567570 row matrix
    
    
    
    # mu_cluster - mu_complement
    final_mean_matrix = mean_matrix - mean_matrix_compl
    
    # get the column indices
    column_ind = np.argsort(final_mean_matrix, axis=1)[:, ::-1] # descending order
    
    # get the words from column indices
    top_words = vocab[column_ind].tolist()[0][:n]
    
    return top_words



####################### Summarize Cluster 4 #######################
def document_closest_to_mean(opinions, tfidf_matrix, op_id_to_bow_id):
    '''
    compute the mean tf-idf vector, return the document in the cluster closet to the mean  
    '''
    
    # op_id_to_bow_id['opinion_id'] = 'row_index'

    row_indices = []
    
    # get row indices corresponding to the opinions
    for each_opinion in opinions:
        row_index = op_id_to_bow_id[each_opinion]
        row_indices.append(row_index)
    
    # construct a matrix with rows (opinions) from cluster
    new_matrix = tfidf_matrix[row_indices, :]
    
    # to take the mean of each col (use axis=1 to take mean of each row)
    mean_matrix = new_matrix.mean(axis=0) # 1 X 567570 row matrix
    
    # convert to vector (since row matrix)
    mean_vector = np.squeeze(np.asarray(mean_matrix))
    
    # get the euclidean distance between mean vector and all other cluster, row vectors
    euc_dist = {}
    for i in row_indices:
        row_vector = np.squeeze(np.asarray(tfidf_matrix[i].toarray()))
        euc_dist[i] = np.linalg.norm(mean_vector-row_vector)
    
    # get row index closest to mean vector (minimum euclidian distance to mean vector)
    row_index_close = min(euc_dist, key=euc_dist.get)
    
    # get opinion closest to mean vector
    for opinion, row_index in op_id_to_bow_id.iteritems():
        if row_index == row_index_close:
            return opinion