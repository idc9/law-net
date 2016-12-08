import glob
import pandas as pd


def load_snapshots(experiment_data_dir, train=True):
    """
    Loads the snapshot data frames into a dict indexed by the file names

    Parameters
    ----------
    experiment_data_dir: path to experiment data files

    Output
    ------
    python dict
    """
    # load all the vertex metric dataframes into a dict so
    # they only have to be read in once
    if train:
        snap_stub = 'snapshots_train/'
    else:
        snap_stub = 'snapshots/'

    path_to_vertex_metrics_folder = experiment_data_dir + snap_stub

    snapshot_paths = glob.glob(path_to_vertex_metrics_folder + \
                               "/vertex_metrics*.csv")
    snapshots_dict = {}
    for path in snapshot_paths:

        # snapshot file name is key
        snapshot_key = path.split(snap_stub)[1].split('.csv')[0]
        snapshots_dict[snapshot_key] = pd.read_csv(path, index_col=0)

    return snapshots_dict


def edge_data_row(citing_vertex, cited_vertex, ing_snapshot_df):
    """
    Returns one row of the edge data frame

    Parameters
    ----------
    citing_vertex, cited_vertex: igraph vertices

    ing_snapshot_df: vertex metrics from ing's year (data frame)

    Output
    ------
    returns a tuple
    """
    # grab vertex metadata
    citing_name = citing_vertex['name'][0]
    cited_name = cited_vertex['name'][0]
    citing_year = citing_vertex['year'][0]
    cited_year = cited_vertex['year'][0]

    cited_vertex_metrics = ing_snapshot_df.loc[cited_name].values.tolist()

    return (class_label) + \
           (citing_name, cited_name, citing_year, cited_year) + \
           (citing_year - cited_year) + \
           tuple(cited_vertex_metrics)


def get_snapshot_year(ing_year, snapshot_year_list):
    """
    Returns the smallest year greater than ing year
    """
    return min([y for y in snapshot_year_list if ing_year < y])
