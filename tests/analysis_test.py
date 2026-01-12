import mysql.connector
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import AffinityPropagation

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database='europeandataportal'
)

mycursor = mydb.cursor()


country_id = 'de'

sql_select = """SELECT cl.country_title,
    COUNT(CASE WHEN c.eu_name = 'Agriculture, fisheries, forestry and food' THEN cl.country_id ELSE NULL END) AS Agriculture,
    COUNT(CASE WHEN c.eu_name = 'Economy and finance' THEN cl.country_id ELSE NULL END) AS Economy,
    COUNT(CASE WHEN c.eu_name = 'Education, culture and sport' THEN cl.country_id ELSE NULL END) AS Education,
    COUNT(CASE WHEN c.eu_name = 'Energy' THEN cl.country_id ELSE NULL END) AS Energy,
    COUNT(CASE WHEN c.eu_name = 'Environment' THEN cl.country_id ELSE NULL END) AS Environment,
    COUNT(CASE WHEN c.eu_name = 'Government and public sector' THEN cl.country_id ELSE NULL END) AS Government,
    COUNT(CASE WHEN c.eu_name = 'Health' THEN cl.country_id ELSE NULL END) AS Health,
    COUNT(CASE WHEN c.eu_name = 'International issues' THEN cl.country_id ELSE NULL END) AS International,
    COUNT(CASE WHEN c.eu_name = 'Justice, legal system and public safety' THEN cl.country_id ELSE NULL END) AS Justice,
    COUNT(CASE WHEN c.eu_name = 'Population and society' THEN cl.country_id ELSE NULL END) AS Population,
    COUNT(CASE WHEN c.eu_name = 'Provisional_data' THEN cl.country_id ELSE NULL END) AS Provisional,
    COUNT(CASE WHEN c.eu_name = 'Regions and cities' THEN cl.country_id ELSE NULL END) AS Regions,
    COUNT(CASE WHEN c.eu_name = 'Science and technology' THEN cl.country_id ELSE NULL END) AS Science,
    COUNT(CASE WHEN c.eu_name = 'Transport' THEN cl.country_id ELSE NULL END) AS Transport
    FROM datasets d, catalogues cl, categories c, datasets_to_categories dc
    WHERE d.catalogue_id = cl.catalogue_id
    AND d.dataset_id = dc.dataset_id
    AND c.category_id = dc.category_id
    AND cl.country_id = %s
    GROUP BY cl.country_id"""

mycursor = mydb.cursor()

mycursor.execute(sql_select, (country_id,))

result = mycursor.fetchone()

categories = ['Agriculture, fisheries, forestry and food', 'Economy and finance', 'Education, culture and sport', 'Energy', 'Environment', 'Government and public sector', 'Health', 'International issues', 'Justice, legal system and public safety', 'Population and society', 'Provisional_data', 'Regions and cities', 'Science and technology', 'Transport']

data = {'count_categories': {'categories': categories, 'count': []}, 'count_catalogues': {'catalogues': {'title': [], 'desc': []}, 'count': []}}

if result == None:
    print('fail')
else:
    for elem in result:
        data['count_categories']['count'].append(elem)

sql_select = """SELECT cl.title, cl.description, COUNT(d.dataset_id)
                FROM datasets d, catalogues cl, categories c, datasets_to_categories dc
                WHERE d.catalogue_id = cl.catalogue_id
                AND d.dataset_id = dc.dataset_id
                AND c.category_id = dc.category_id
                AND cl.country_id = %s
                GROUP BY cl.catalogue_id"""

mycursor.execute(sql_select, (country_id,))

result = mycursor.fetchall()

if result == None:
    print('fail')
else:
    for catalogue in result:
        data['count_catalogues']['catalogues']['title'].append(catalogue[0])
        data['count_catalogues']['catalogues']['desc'].append(catalogue[1])
        data['count_catalogues']['count'].append(catalogue[2])

mycursor.close()

print(data)

cats = ['Economy and finance','Justice, legal system and public safety','Environment','Population and society','Transport','Science and technology','Education, culture and sport','Government and public sector','Health','Energy','Agriculture, fisheries, forestry and food','Regions and cities','International issues','Provisional data']

sql_select = """SELECT cl.country_title, COUNT(DISTINCT d.dataset_id) AS total, cl.country_id,
COUNT(CASE WHEN c.eu_name = 'Agriculture, fisheries, forestry and food' THEN cl.country_id ELSE NULL END) AS Agriculture,
COUNT(CASE WHEN c.eu_name = 'Economy and finance' THEN cl.country_id ELSE NULL END) AS Economy,
COUNT(CASE WHEN c.eu_name = 'Education, culture and sport' THEN cl.country_id ELSE NULL END) AS Education,
COUNT(CASE WHEN c.eu_name = 'Energy' THEN cl.country_id ELSE NULL END) AS Energy,
COUNT(CASE WHEN c.eu_name = 'Environment' THEN cl.country_id ELSE NULL END) AS Environment,
COUNT(CASE WHEN c.eu_name = 'Government and public sector' THEN cl.country_id ELSE NULL END) AS Government,
COUNT(CASE WHEN c.eu_name = 'Health' THEN cl.country_id ELSE NULL END) AS Health,
COUNT(CASE WHEN c.eu_name = 'International issues' THEN cl.country_id ELSE NULL END) AS International,
COUNT(CASE WHEN c.eu_name = 'Justice, legal system and public safety' THEN cl.country_id ELSE NULL END) AS Justice,
COUNT(CASE WHEN c.eu_name = 'Population and society' THEN cl.country_id ELSE NULL END) AS Population,
COUNT(CASE WHEN c.eu_name = 'Provisional_data' THEN cl.country_id ELSE NULL END) AS Provisional,
COUNT(CASE WHEN c.eu_name = 'Regions and cities' THEN cl.country_id ELSE NULL END) AS Regions,
COUNT(CASE WHEN c.eu_name = 'Science and technology' THEN cl.country_id ELSE NULL END) AS Science,
COUNT(CASE WHEN c.eu_name = 'Transport' THEN cl.country_id ELSE NULL END) AS Transport
FROM datasets d, catalogues cl, categories c, datasets_to_categories dc
WHERE d.catalogue_id = cl.catalogue_id
AND d.dataset_id = dc.dataset_id
AND c.category_id = dc.category_id
AND cl.country_id <> 'eu'
GROUP BY cl.country_id"""

mycursor.execute(sql_select)

country_rows = mycursor.fetchall()

data_list = []
data_metadata = []
data_metadata_titles = []
data_metadata_ids = []

for row in country_rows:
    # mysql returns tuples
    row_list = list(row)
    # first elem is the country and second is total count
    data_metadata.append([row_list[0], row_list[1]])
    data_metadata_titles.append(row_list[0])
    data_metadata_ids.append(row_list[2])
    total = row_list[1]
    row_list.pop(0)
    row_list.pop(0)
    row_list.pop(0)

    # normalize values by using percentages
    normalized_row = []
    for count in row_list:
        new_value = 100 * (float(count) / float(total))
        normalized_row.append(round(new_value))

    data_list.append(normalized_row)

# print(data_list)
X = np.array(data_list)

"""
Affinity Propagation clustering
"""

clustering = AffinityPropagation().fit(X)


#print(data_metadata_titles)
#print(clustering.labels_)

#clusters_countries = [[] for i in range(clustering.cluster_centers_indices_.size)]
clusters_countries = {}

for i in range(0, clustering.labels_.size):
    #clusters_countries[clustering.labels_[i]].append(data_metadata_ids[i])
    clusters_countries[data_metadata_ids[i]] = clustering.labels_[i] + 1

print(clusters_countries)



#https://towardsdatascience.com/machine-learning-algorithms-part-9-k-means-example-in-python-f2ad05ed5203
"""
find optimal number of clusters by trying kmeans with different n and saving intertia_ property (WCSS) or cost function
looking at the graph, 3 is best so n = 3

wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)
plt.plot(range(1, 11), wcss)
plt.title('Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()


kmeans = KMeans(n_clusters=6, init='k-means++', max_iter=300, n_init=10, random_state=0)
pred_y = kmeans.fit_predict(X)
plt.scatter(X[:,0], X[:,1])
#plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red')
plt.show()
"""

"""
https://towardsdatascience.com/unsupervised-machine-learning-affinity-propagation-algorithm-explained-d1fef85f22c8


Affinity Propagation clustering

"""

