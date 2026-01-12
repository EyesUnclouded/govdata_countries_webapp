import numpy as np
from sklearn.cluster import AffinityPropagation

def get_clusters(countries_data, clustering_method = ''):
    """
    prepare data so that it can be processed and then still be retrieved and labeled with metadata
    """
    data_list = []
    data_metadata_ids = []

    for country_id, country_dict in countries_data.items():
        data_list.append(countries_data[country_id]['data'])
        data_metadata_ids.append(country_id)

    """
    use numpy for faster array structure and scikit-learn clustering support
    """
    X = np.array(data_list)

    """
    Affinity Propagation clustering
    """
    #preference = np.min(pdist(X))

    clustering = AffinityPropagation().fit(X)

    #connectivity = kneighbors_graph(X, n_neighbors=10, include_self=False)
    #clustering = AgglomerativeClustering(n_clusters=6, connectivity=connectivity, linkage="ward").fit(X)

    #clustering = AgglomerativeClustering(n_clusters=9, affinity='euclidean', linkage="complete").fit(X)

    clusters_countries = {}
    clusters_countries_distributions = {}
    """
    create dict in which each elem is a cluster/dict with all its cluster members
    clusters_countries_distributions is for determining average distribution of values of a cluster's members
    """
    for i in range(0, clustering.labels_.size):
        # +1 so there is no cluster 0
        # count is the cluster
        cluster_number = str(clustering.labels_[i].item() + 1)
        if cluster_number not in clusters_countries_distributions:
            clusters_countries_distributions[cluster_number] = {}
        clusters_countries_distributions[cluster_number][data_metadata_ids[i]] = data_list[i]

    """ 
    sort cluster ids by member count
    """
    clusters_sorted = {}
    new_cluster_id = 1
    sorted_cluster_keys = sorted(clusters_countries_distributions, key=lambda k: len(clusters_countries_distributions[k]), reverse=True)

    for cluster in sorted_cluster_keys:
        clusters_sorted[new_cluster_id] = clusters_countries_distributions[cluster]
        new_cluster_id += 1

    clusters_countries_distributions = clusters_sorted
    clusters_average_distributions = {}

    #print(clusters_countries_distributions)
    """
    get average distribution of values of each cluster and create dict for map visualization
    """

    for cluster in clusters_countries_distributions:
        if len(clusters_countries_distributions[cluster]) > 1:
            cluster_np_arrays = []
            for country in clusters_countries_distributions[cluster]:
                """
                for map visualization
                """
                clusters_countries[country] = {
                    'country_title': countries_data[country]['country_title'], 'count': cluster}

                country_numpy = np.array(clusters_countries_distributions[cluster][country])
                cluster_np_arrays.append(country_numpy)

            np_average_distribution = np.round(np.mean(cluster_np_arrays, axis=0), 2).astype(float)
            clusters_average_distributions[cluster] = np_average_distribution.tolist()
        else:
            only_country = list(clusters_countries_distributions[cluster].keys())[0]
            """
            for map visualization
            """
            clusters_countries[only_country] = {
                'country_title': countries_data[only_country]['country_title'], 'count': cluster}

            clusters_average_distributions[cluster] = clusters_countries_distributions[cluster][only_country]

    return clusters_countries, len(clusters_countries_distributions), clusters_average_distributions

