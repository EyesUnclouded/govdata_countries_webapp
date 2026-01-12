from flask import Flask, render_template, request

import json

import numpy as np


app = Flask(__name__)

from functions import mysql_connect, percentage, detect_outliers
from get_data_functions import get_in_countries, get_formats, get_timeliness_factors, get_categories
from get_clusters import get_clusters

countries_dict_global = {'at': 'Austria', 'be': 'Belgium', 'bg': 'Bulgaria', 'cy': 'Cyprus', 'cz': 'Czechia', 'de': 'Germany',
                 'dk': 'Denmark', 'ee': 'Estonia', 'es': 'Spain', 'fi': 'Finland', 'fr': 'France',
                 'gb': 'United Kingdom', 'gr': 'Greece', 'hr': 'Croatia', 'hu': 'Hungary', 'ie': 'Ireland',
                 'it': 'Italy', 'lt': 'Lithuania', 'lu': 'Luxembourg', 'lv': 'Latvia', 'mt': 'Malta',
                 'nl': 'Netherlands', 'pl': 'Poland', 'pt': 'Portugal', 'ro': 'Romania', 'se': 'Sweden',
                 'si': 'Slovenia', 'sk': 'Slovakia'}

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/_get_european_borders", methods=['GET', 'POST'])
def get_european_borders():
    """
    get geojson country borders from database
    saved geojson in database to not have to put it in javascript and slow it down
    """
    sql_select = "SELECT geo_data FROM geojson WHERE geojson_id = 3"

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    mycursor.execute(sql_select)

    result = mycursor.fetchone()

    european_borders_geojson = json.loads(result[0])

    mycursor.close()
    cnx.close()

    return json.dumps({'status': 'OK', 'data': {'european_borders_geojson': european_borders_geojson}})

@app.route("/_count_country", methods=['GET', 'POST'])
def count_country():
    country_id = request.form.get("country_id")

    """
    A.ungrouped as ungrouped
    ,
        (SELECT COUNT(1) as ungrouped FROM datasets ds, datasets_to_categories dcs WHERE ds.dataset_id <> dcs.dataset_id) as A
    """

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
        COUNT(CASE WHEN c.eu_name = 'Regions and cities' THEN cl.country_id ELSE NULL END) AS Regions,
        COUNT(CASE WHEN c.eu_name = 'Science and technology' THEN cl.country_id ELSE NULL END) AS Science,
        COUNT(CASE WHEN c.eu_name = 'Transport' THEN cl.country_id ELSE NULL END) AS Transport
        FROM datasets d, catalogues cl, categories c, datasets_to_categories dc
        WHERE d.catalogue_id = cl.catalogue_id
        AND d.dataset_id = dc.dataset_id
        AND c.category_id = dc.category_id
        AND cl.country_id = %s
        AND c.eu_name <> 'Provisional_data'
        GROUP BY cl.country_id"""

    #print(sql_select)

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    #print(country_id)

    mycursor.execute(sql_select, (country_id,))

    result = mycursor.fetchone()

    #categories = ['Agriculture, fisheries, forestry and food', 'Economy and finance', 'Education, culture and sport', 'Energy', 'Environment', 'Government and public sector', 'Health', 'International issues', 'Justice, legal system and public safety', 'Population and society', 'Provisional_data', 'Regions and cities', 'Science and technology', 'Transport']
    categories = ['Agriculture', 'Economy', 'Education',
                  'Energy', 'Environment', 'Government', 'Health', 'International',
                  'Justice', 'Population',
                  'Regions', 'Science', 'Transport', 'not in category']
    data = {'country_title': '', 'count_categories': {'categories': categories, 'count': []}, 'count_catalogues': {'catalogues': {'title': [], 'desc': []}, 'count': []}}

    if result is None:
        return json.dumps({'status': 'FAIL'})
    else:
        result = list(result)

        data['country_title'] = result[0]

        result.pop(0)

        for elem in result:
            data['count_categories']['count'].append(elem)

    sql_select = """SELECT cl.title, cl.description, COUNT(1) 
                    FROM datasets d, catalogues cl 
                    WHERE d.catalogue_id = cl.catalogue_id 
                    AND cl.country_id = %s 
                    GROUP BY cl.catalogue_id ORDER BY country_title"""

    #print(sql_select)

    mycursor.execute(sql_select, (country_id,))

    result = mycursor.fetchall()

    if result is None:
        return json.dumps({'status': 'FAIL'})
    else:
        for catalogue in result:
            data['count_catalogues']['catalogues']['title'].append(catalogue[0])
            data['count_catalogues']['catalogues']['desc'].append(catalogue[1])
            data['count_catalogues']['count'].append(catalogue[2])

    mycursor.close()
    cnx.close()

    return json.dumps({'status': 'OK', 'data': data})

@app.route("/_count_all_datasets", methods=['GET', 'POST'])
def count_all_datasets():
    sql_select_count = """
    SELECT cl.country_id, count(1) as count_datasets, cl.country_title 
    FROM datasets d, catalogues cl 
    WHERE d.catalogue_id = cl.catalogue_id 
    AND cl.country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md') 
    GROUP BY cl.country_id"""

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    mycursor.execute(sql_select_count)

    data_count_all = {}
    result = mycursor.fetchall()

    data_list = []
    data_ids_list = []

    for country in result:
        data_count_all[country[0]] = {'count': country[1], 'country_title': country[2]}
        data_list.append(country[1])
        data_ids_list.append(country[0])

    X = np.array(data_list)

    print("mean")
    print(np.mean(X))

    mycursor.close()
    cnx.close()
    """
    feature removed
    remove the outliers from the data list so that we can get a more accurate representation of the mean
    """
    """
    outliers = detect_outliers(X)

    data_list2 = data_list
    data_ids_list2 = data_ids_list

    for idx, value in enumerate(data_list2):
        if value in outliers:
            data_list2.pop(idx)
            data_ids_list2.pop(idx)

    X = np.array(data_list2)
    count_std = np.std(X)
    count_mean = np.mean(X)

    count_1std = 0
    for idx, value in enumerate(data_list2):
        if (value > (count_mean - count_std)) and (value < (count_mean + count_std)):
            count_1std += 1
        else:
            print(data_ids_list2[idx])
            print(value)

    print(percentage(count_1std, len(data_list2)))
    """
    return json.dumps({'status': 'OK', 'data': data_count_all})

@app.route("/_count_accessible", methods=['GET', 'POST'])
def count_accessible():
    global countries_dict_global

    sql_select_count = """
        SELECT DISTINCT cl.country_id, ROUND(100*(B.accessible_datasets / A.total_datasets), 2) AS accessible_percent, cl.country_title
        FROM catalogues cl,
        (SELECT cl.country_id,  COUNT(d.dataset_id) as total_datasets
        FROM datasets d, catalogues cl
        WHERE d.catalogue_id = cl.catalogue_id
        GROUP BY cl.country_id) AS A,
        
        (SELECT cl.country_id,  COUNT(DISTINCT d.dataset_id) as accessible_datasets
        FROM datasets d, catalogues cl, resources r
        WHERE d.catalogue_id = cl.catalogue_id
        AND d.dataset_id = r.dataset_id
        AND r.url_accessible = 1
        GROUP BY cl.country_id) AS B
        
        WHERE cl.country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md') 
        AND cl.country_id = A.country_id
        AND cl.country_id = B.country_id
        """

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    mycursor.execute(sql_select_count)

    countries_data = {}
    results = mycursor.fetchall()

    for country in results:
        countries_data[country[0]] = {"count": float(country[1]), "country_title": country[2]}

    for country_id in countries_dict_global:
        if country_id not in countries_data:
            countries_data[country_id] = {'count': 0, 'country_title': countries_dict_global[country_id]}

    list_for_avg = []
    for country_id in countries_data:
        list_for_avg.append(countries_data[country_id]['count'])

    print('average')
    print(np.mean(np.array(list_for_avg)))

    return json.dumps({'status': 'OK', 'data': countries_data})

@app.route("/_country_licenses", methods=['GET', 'POST'])
def country_licenses():
    global countries_dict_global

    country_id = request.form.get("country_id")

    return_dict = {'open_licenses': {'data': [], 'licenses': []}, 'top5_licenses': {'data': [], 'licenses': []}}

    cnx = mysql_connect()
    mycursor = cnx.cursor()


    sql_select = """SELECT d.license_id, COUNT(1) AS license_count, cl.country_title
        FROM datasets d, catalogues cl, resources r 
        WHERE r.dataset_id = d.dataset_id 
        AND d.catalogue_id = cl.catalogue_id 
        AND cl.country_id = %s
        AND d.license_id IS NOT NULL
        GROUP BY cl.country_id, d.license_id
        ORDER BY license_count DESC"""

    mycursor.execute(sql_select, (country_id,))

    results = mycursor.fetchall()

    conformant_licenses = ['creativecommonsorglicensesby', 'creativecommonsorglicensesbysa', 'creativecommonscczero', 'cc0', 'httpscreativecommonsorgpublicdomainzero10',
                           'httpcreativecommonsorgpublicdomainzero10',
                           'opendatacommonspublicdomaindedicationandlicence', 'odcpddl', 'pddl',
                           'httpwwwopendatacommonsorglicensespddl10', 'httpswwwopendatacommonsorglicensespddl10',
                           'creativecommonsattribution40', 'ccby',
                           'opendatacommonsattributionlicense', 'odcby', 'httpopendatacommonsorglicensesby10',
                           'httpsopendatacommonsorglicensesby10',
                           'creativecommonsattributionsharealike', 'ccbysa', 'httpcreativecommonsorglicensesbysa40',
                           'httpscreativecommonsorglicensesbysa',
                           'opendatacommonsopendatabaselicense', 'odbl', 'httpopendatacommonsorglicensesodbl10',
                           'httpsopendatacommonsorglicensesodbl10']

    top5 = 0

    for license in results:
        license_str = str(license[0]).translate(str.maketrans('', '', ".-_/:!,;*+'#&|?\ ")).lower()
        license_id = license[0]

        if 'country_title' not in return_dict:
            return_dict['country_title'] = license[2]

        license_count = int(license[1])

        if top5 <= 5:
            return_dict['top5_licenses']['licenses'].append(license_id)
            return_dict['top5_licenses']['data'].append(license_count)
            top5 += 1

        for match_license in conformant_licenses:
            if match_license in license_str:
                return_dict['open_licenses']['licenses'].append(license_id)
                return_dict['open_licenses']['data'].append(license_count)

    mycursor.close()
    cnx.close()

    return json.dumps({'status': 'OK', 'data': return_dict})

@app.route("/_count_empty_licenses", methods=['GET', 'POST'])
def count_empty_licenses():
    global countries_dict_global

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    sql_select = """SELECT cl.country_id, COUNT(DISTINCT d.dataset_id) AS license_count, cl.country_title, A.total_count
        FROM datasets d, catalogues cl,
        (SELECT cll.country_id, COUNT(DISTINCT dd.dataset_id) AS total_count FROM datasets dd, catalogues cll WHERE dd.catalogue_id = cll.catalogue_id GROUP BY cll.country_id) as A
        WHERE cl.country_id = A.country_id
        AND d.catalogue_id = cl.catalogue_id 
        AND cl.country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md')
        AND d.license_id IS NOT NULL
        GROUP BY cl.country_id"""

    mycursor.execute(sql_select)

    results = mycursor.fetchall()

    mycursor.close()
    cnx.close()

    countries_data = {}

    for country in results:
        countries_data[country[0]] = {"count": round(percentage(int(country[1]), int(country[3])), 2), "country_title": country[2]}

    for country_id in countries_dict_global:
        if country_id not in countries_data:
            countries_data[country_id] = {'count': 0, 'country_title': countries_dict_global[country_id]}

    return json.dumps({'status': 'OK', 'data': countries_data})

@app.route("/_count_open_licenses", methods=['GET', 'POST'])
def count_open_licenses():
    global countries_dict_global

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    sql_select = """SELECT cl.country_id, d.license_id, COUNT(DISTINCT d.dataset_id) AS license_count, cl.country_title, A.total_count
    FROM datasets d, catalogues cl,
    (SELECT cll.country_id, COUNT(DISTINCT dd.dataset_id) AS total_count FROM datasets dd, catalogues cll WHERE dd.catalogue_id = cll.catalogue_id GROUP BY cll.country_id) as A
    WHERE cl.country_id = A.country_id
    AND d.catalogue_id = cl.catalogue_id 
    AND cl.country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md')
    AND d.license_id IS NOT NULL
    GROUP BY cl.country_id, d.license_id"""

    mycursor.execute(sql_select)

    results = mycursor.fetchall()

    mycursor.close()
    cnx.close()

    countries_data = {}

    conformant_licenses = ['creativecommonsorglicensesby', 'creativecommonsorglicensesbysa', 'creativecommonscczero', 'cc0', 'httpscreativecommonsorgpublicdomainzero10',
                           'httpcreativecommonsorgpublicdomainzero10',
                           'opendatacommonspublicdomaindedicationandlicence', 'odcpddl', 'pddl',
                           'httpwwwopendatacommonsorglicensespddl10', 'httpswwwopendatacommonsorglicensespddl10',
                           'creativecommonsattribution40', 'ccby',
                           'opendatacommonsattributionlicense', 'odcby', 'httpopendatacommonsorglicensesby10',
                           'httpsopendatacommonsorglicensesby10',
                           'creativecommonsattributionsharealike', 'ccbysa', 'httpcreativecommonsorglicensesbysa40',
                           'httpscreativecommonsorglicensesbysa',
                           'opendatacommonsopendatabaselicense', 'odbl', 'httpopendatacommonsorglicensesodbl10',
                           'httpsopendatacommonsorglicensesodbl10']

    """
    count per license
    """
    for license in results:
        license_str = str(license[1]).translate(str.maketrans('', '', ".-_/:!,;*+'#&|?\ ")).lower()
        country_id = license[0]
        country_title = license[3]
        license_count = license[2]
        all_datasets_count = license[4]

        if country_id not in countries_data:
            countries_data[country_id] = {'data': {}}

        for match_license in conformant_licenses:
            if match_license in license_str:
                if match_license not in countries_data[country_id]['data']:
                    countries_data[country_id]['data'][match_license] = license_count
                else:
                    countries_data[country_id]['data'][match_license] += license_count
                break

        countries_data[country_id]['country_title'] = country_title
        countries_data[country_id]['total_count'] = all_datasets_count

    """
    percentage of open licenses of total dataset count
    """
    for country_id in countries_data:
        count_total = 0
        for license in countries_data[country_id]['data']:
            count_total += countries_data[country_id]['data'][license]

        countries_data[country_id]['count'] = round(percentage(count_total, countries_data[country_id]['total_count']), 2)

    for country_id in countries_dict_global:
        if country_id not in countries_data:
            countries_data[country_id] = {'data': {}, 'count': 0, 'country_title': countries_dict_global[country_id]}

    list_for_avg = []
    for country_id in countries_data:
        list_for_avg.append(countries_data[country_id]['count'])

    print('average:')
    print(np.mean(np.array(list_for_avg)))

    return json.dumps({'status': 'OK', 'data': countries_data})

@app.route("/_count_linked_data", methods=['GET', 'POST'])
def count_linked_data():
    global countries_dict_global

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    sql_select = """
                    SELECT cl.country_id, GROUP_CONCAT(DISTINCT r.formatting), cl.country_title, A.count_total
                    FROM datasets d, catalogues cl, resources r,
                    (SELECT cll.country_id, COUNT(DISTINCT dd.dataset_id) AS count_total FROM datasets dd, catalogues cll WHERE dd.catalogue_id = cll.catalogue_id GROUP BY cll.country_id) as A
                    WHERE cl.country_id = A.country_id
                    AND r.dataset_id = d.dataset_id 
                    AND d.catalogue_id = cl.catalogue_id 
                    AND cl.country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md')
                    AND r.formatting IS NOT NULL
                    GROUP BY r.dataset_id
                    """
    mycursor.execute(sql_select)

    """
    for each dataset iterate over all its distributions' formats (create lists with GROUP_CONCAT) and detect RDF format
    """
    countries_data = {}
    fetchsize = 50000

    # crash_breaker to not use while(True)
    crash_breaker = 0
    while crash_breaker < 999999999:
        crash_breaker += 1

        datasets = mycursor.fetchmany(fetchsize)
        if not datasets:
            break

        for dataset in datasets:
            country_id = dataset[0]
            formats = str(dataset[1]).split(',')

            if country_id not in countries_data:
                countries_data[country_id] = {'count': 0, 'country_title': dataset[2], 'count_total': dataset[3]}

            for format in formats:
                format = format.translate(str.maketrans('', '', ".-_/:!,;*+'#&|?\ ")).lower()

                if 'rdf' in format:
                    countries_data[country_id]['count'] += 1
                    break

    for country_id in countries_dict_global:
        if country_id not in countries_data:
            countries_data[country_id] = {'count': 0, 'country_title': countries_dict_global[country_id]}
        else:
            countries_data[country_id]['count'] = percentage(countries_data[country_id]['count'], countries_data[country_id]['count_total'])

    return json.dumps({'status': 'OK', 'data': countries_data})

@app.route("/_publication_timeline", methods=['GET', 'POST'])
def publication_timeline():

    countries = request.form.get("countries")

    cluster = int(request.form.get("cluster"))

    countries_data = json.loads(request.form.get("countries_data"))

    clusters_average_distributions = json.loads(request.form.get("clusters_average_distributions"))

    in_countries, countries_list = get_in_countries(countries)

    if len(countries_data) > 0:
        if len(countries_list) > 0:
            new_countries_data = {}
            for country_id in countries_data:
                if country_id in countries_list:
                    new_countries_data[country_id] = countries_data[country_id]
        else:
            new_countries_data = countries_data

        if len(clusters_average_distributions) > 0 and cluster > 0:
            average_distribution = clusters_average_distributions[str(cluster)]
        else:
            average_distribution = 0

        return_dict = {'status': 'OK', 'data_factors': new_countries_data, 'average_distribution': average_distribution}
    else:
        countries_data = get_timeliness_factors()

        if cluster > 0:
            clusters_countries, n_clusters, clusters_average_distributions = get_clusters(countries_data)

            average_distribution = clusters_average_distributions[cluster]
        else:
            average_distribution = 0

        if len(countries_list) > 0:
            new_countries_data = {}
            for country_id in countries_data:
                if country_id in countries_list:
                    new_countries_data[country_id] = countries_data[country_id]
        else:
            new_countries_data = countries_data

        return_dict = {'status': 'OK', 'data_factors': new_countries_data, 'average_distribution': average_distribution}

    sql_select = """SELECT DATE_FORMAT(d.metadata_created, '%Y-%m') as pub_month, cl.country_id as id, cl.country_title, COUNT(1) as count_datasets, DATE_FORMAT(DATE_SUB(db.last_updated , INTERVAL 5 YEAR), '%Y-%m') AS start_month
    FROM datasets d, catalogues cl, db_metadata db
    WHERE d.catalogue_id = cl.catalogue_id 
    AND cl.country_id """+ in_countries +"""
    AND d.metadata_created IS NOT NULL 
    AND db.db_metadata_id = 1
    AND (d.metadata_created BETWEEN DATE_SUB(db.last_updated , INTERVAL 5 YEAR) AND db.last_updated)
    GROUP BY cl.country_id, pub_month 
    ORDER BY country_title, pub_month"""

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    mycursor.execute(sql_select)

    countries_publications = {}

    result = mycursor.fetchall()

    """
    countries_publications structure is {country_id: {'pub_month': {'2015-01': 4, '2015-02': 12}}}
    """
    start_month = None

    for country_month in result:
        if country_month[1] not in countries_publications:
            countries_publications[country_month[1]] = {'pub_month': {}, 'country_title': country_month[2], 'pub_total': 0}

        countries_publications[country_month[1]]['pub_month'][country_month[0]] = country_month[3]
        countries_publications[country_month[1]]['pub_total'] += country_month[3]

        if start_month is None:
            start_month = country_month[4]

    mycursor.close()
    cnx.close()

    return_dict['data_monthly'] = countries_publications
    return_dict['start_month'] = start_month

    return json.dumps(return_dict)

@app.route("/_categories", methods=['GET', 'POST'])
def categories():
    countries = request.form.get("countries")

    cluster = int(request.form.get("cluster"))

    countries_data = json.loads(request.form.get("countries_data"))

    clusters_average_distributions = json.loads(request.form.get("clusters_average_distributions"))

    categories = ['Agriculture', 'Economy', 'Education',
                  'Energy', 'Environment', 'Government', 'Health', 'International',
                  'Justice', 'Population',
                  'Regions', 'Science', 'Transport']

    in_countries, countries_list = get_in_countries(countries)

    """
    check if data is already loaded if not get data
    """
    if len(countries_data) > 0:
        if len(countries_list) > 0:
            new_countries_data = {}
            for country_id in countries_data:
                if country_id in countries_list:
                    new_countries_data[country_id] = countries_data[country_id]
        else:
            new_countries_data = countries_data

        if len(clusters_average_distributions) > 0 and cluster > 0:
            """
            str() because javascript transforms integer keys into strings
            """
            average_distribution = clusters_average_distributions[str(cluster)]
        else:
            average_distribution = 0

        return json.dumps({'status': 'OK', 'data': new_countries_data, 'categories': categories, 'average_distribution': average_distribution})
    else:
        countries_data = get_categories()

        if cluster > 0:
            clusters_countries, n_clusters, clusters_average_distributions = get_clusters(countries_data)

            average_distribution = clusters_average_distributions[cluster]
        else:
            average_distribution = 0

        if len(countries_list) > 0:
            new_countries_data = {}
            for country_id in countries_data:
                if country_id in countries_list:
                    new_countries_data[country_id] = countries_data[country_id]
        else:
            new_countries_data = countries_data

        return json.dumps({'status': 'OK', 'data': new_countries_data, 'categories': categories, 'average_distribution':average_distribution})


@app.route("/_formats", methods=['GET', 'POST'])
def formats():
    categories = ['none of both', 'machine readable (mr)', 'non-proprietary (np)', 'EITHER mr OR np', 'mr AND np']

    countries = request.form.get("countries")

    cluster = int(request.form.get("cluster"))

    countries_data = json.loads(request.form.get("countries_data"))

    clusters_average_distributions = json.loads(request.form.get("clusters_average_distributions"))

    in_countries, countries_list = get_in_countries(countries)

    if len(countries_data) > 0:
        if len(countries_list) > 0:
            new_countries_data = {}
            for country_id in countries_data:
                if country_id in countries_list:
                    new_countries_data[country_id] = countries_data[country_id]
        else:
            new_countries_data = countries_data

        if len(clusters_average_distributions) > 0 and cluster > 0:
            average_distribution = clusters_average_distributions[str(cluster)]
        else:
            average_distribution = 0

        return json.dumps({'status': 'OK', 'data': new_countries_data, 'categories': categories,
                           'average_distribution': average_distribution})
    else:
        countries_data = get_formats()

        if cluster > 0:
            clusters_countries, n_clusters, clusters_average_distributions = get_clusters(countries_data)

            average_distribution = clusters_average_distributions[cluster]
        else:
            average_distribution = 0

        if len(countries_list) > 0:
            new_countries_data = {}
            for country_id in countries_data:
                if country_id in countries_list:
                    new_countries_data[country_id] = countries_data[country_id]
        else:
            new_countries_data = countries_data

        return json.dumps({'status': 'OK', 'data': new_countries_data, 'categories': categories,
                           'average_distribution': average_distribution})

@app.route("/_cluster_publication_timeline", methods=['GET', 'POST'])
def cluster_publication_timeline():
    """
    get data from database and process it to get the timeliness factors for each country
    """
    countries_data = get_timeliness_factors()

    clusters_countries, n_clusters, clusters_average_distributions = get_clusters(countries_data)

    return json.dumps({'status': 'OK', 'data': clusters_countries, 'countries_timeliness_factors': countries_data, 'n_clusters': n_clusters, 'clusters_average_distributions': clusters_average_distributions})


@app.route("/_cluster_categories", methods=['GET', 'POST'])
def cluster_categories():
    """
    get data from database and create a dictionary where each key is a country and its frequencies
    """
    countries_data = get_categories()

    clusters_countries, n_clusters, clusters_average_distributions = get_clusters(countries_data)

    return json.dumps({'status': 'OK', 'data': clusters_countries, 'categories_countries_data': countries_data, 'n_clusters': n_clusters, 'clusters_average_distributions': clusters_average_distributions})


@app.route("/_cluster_formats", methods=['GET', 'POST'])
def cluster_formats():
    """
    get data from db and process it with the lists of machine readable and non-proprietary formats
    """
    countries_data = get_formats()

    clusters_countries, n_clusters, clusters_average_distributions = get_clusters(countries_data)

    return json.dumps({'status': 'OK', 'data': clusters_countries, 'countries_data': countries_data, 'n_clusters': n_clusters, 'clusters_average_distributions': clusters_average_distributions})


if __name__ == '__main__':
    app.run()
