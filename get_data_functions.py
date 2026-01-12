import json
import numpy as np
from functions import mysql_connect, percentage, detect_outliers

"""

FUNCTIONS FOR GETTING DATA FOR THE CLUSTERING METHODS

"""

def get_in_countries (countries):
    if countries is not None and countries != '' and countries != '0' and countries != 'null':
        countries_list = countries.split(',')
        countries_str = ''
        for country_id in countries_list:
            countries_str += "'"+ country_id +"',"
        return "IN (" + countries_str.rstrip(',') + ")", countries_list
    else:
        return "NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md')", []

def get_timeliness_factors(in_countries="NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md')"):
    """
    outer select to get the average of the date difference between a day of publication and the next day of publication
    first subquery gets all publication days of each country and also gets for each date the next day of publication with LEAD()
    second subquery gets the first day of publication with MIN() for each country and puts as next day the starting day of the time period that is tested
    """

    sql_select = """SELECT DISTINCT cls.country_id, cls.country_title, AVG(DATEDIFF(A.pub_day, A.next_date)) AS pub_diff
    FROM catalogues cls, (
    (SELECT cl.country_id, DATE_FORMAT(d.metadata_created, '%Y-%m-%d') as pub_day, 
    LEAD(DATE_FORMAT(d.metadata_created, '%Y-%m-%d'),1,DATE_FORMAT(db.last_updated, '%Y-%m-%d')) OVER (PARTITION BY cl.country_id ORDER BY DATE_FORMAT(d.metadata_created, '%Y-%m-%d')) as next_date
    FROM datasets d, catalogues cl, db_metadata db
    WHERE d.catalogue_id = cl.catalogue_id 
    AND d.metadata_created IS NOT NULL 
    AND db.db_metadata_id = 1
    AND (d.metadata_created BETWEEN DATE_SUB(db.last_updated, INTERVAL 5 YEAR) AND db.last_updated) 
    AND cl.country_id """ + in_countries + """
    GROUP BY cl.country_id, pub_day
    ORDER BY pub_day ASC)

    UNION ALL

    (SELECT cccl.country_id, DATE_FORMAT(DATE_SUB(dddb.last_updated , INTERVAL 5 YEAR), '%Y-%m-%d') as pub_day, Y.min_day AS next_date
    FROM catalogues cccl, db_metadata dddb,
    (SELECT ycl.country_id, MIN(DATE_FORMAT(yd.metadata_created, '%Y-%m-%d')) AS min_day
    FROM datasets yd, catalogues ycl, db_metadata ydb
    WHERE yd.catalogue_id = ycl.catalogue_id 
    AND yd.metadata_created IS NOT NULL
    AND ydb.db_metadata_id = 1
    AND (yd.metadata_created BETWEEN DATE_SUB(ydb.last_updated , INTERVAL 5 YEAR) AND ydb.last_updated) 
    GROUP BY ycl.country_id
    ) as Y
    WHERE cccl.country_id = Y.country_id
    AND dddb.db_metadata_id = 1
    AND cccl.country_id """ + in_countries + """
    GROUP BY cccl.country_id)
    ) AS A
    WHERE A.country_id = cls.country_id
    GROUP BY cls.catalogue_id"""

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    mycursor.execute(sql_select)

    result = mycursor.fetchall()

    """
    countries_publications structure is {country_id: {'avg_day_diff': 10, 'avg_pub_week': 20, 'outliers': 3}}
    """
    countries_publications = {}

    for country in result:
        """
        take the absolute value because some differences are negative or positive even though it does not matter for the comparison
        """

        countries_publications[country[0]] = {'data': [round(abs(float(country[2])), 2)], 'country_title': country[1]}

    """
    get each week in the last 5 years with publications and the number of publications in that week for each country
    """

    sql_select2 = """SELECT cl.country_id AS country, COUNT(1) as count_datasets, CONCAT(YEAR(d.metadata_created), '/', WEEK(d.metadata_created)) as pub_day
    FROM datasets d, catalogues cl, db_metadata db
    WHERE d.catalogue_id = cl.catalogue_id 
    AND cl.country_id """ + in_countries + """
    AND d.metadata_created IS NOT NULL 
    AND db.db_metadata_id = 1
    AND (d.metadata_created BETWEEN DATE_SUB(db.last_updated , INTERVAL 5 YEAR) AND db.last_updated) 
    GROUP BY cl.country_id, pub_day
    ORDER BY cl.country_id, pub_day"""

    mycursor.execute(sql_select2)

    result2 = mycursor.fetchall()

    countries_weeks = {}
    for week in result2:
        if week[0] not in countries_weeks:
            countries_weeks[week[0]] = []

        countries_weeks[week[0]].append(week[1])

    mycursor.close()
    cnx.close()

    """
    use numpy for fast array methods for mean and detecting outliers
    """
    for country in countries_weeks:
        value_list = countries_weeks[country]
        np_value_list = np.array(value_list)

        outliers = detect_outliers(np_value_list)
        for idx, elem in enumerate(value_list):
            if elem in outliers:
                countries_weeks[country].pop(idx)

        """
        for the mean without the outliers the sum is divided by 260 (the total number of weeks) to include the missing weeks that would have the value 0
        this way every country can be compared even though they have different numbers of weeks with and without publications
        """

        countries_publications[country]['data'].append(round(np.sum(np.array(countries_weeks[country])) / 260, 2))
        countries_publications[country]['data'].append(len(outliers))

    return countries_publications


def get_categories(in_countries="NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md')"):
    sql_select = """SELECT cl.country_title,  COUNT(DISTINCT d.dataset_id) AS total, cl.country_id,
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
                    AND cl.country_id """ + in_countries + """
                    AND c.eu_name <> 'Provisional_data'
                    GROUP BY cl.country_id"""

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    # print(country_id)

    mycursor.execute(sql_select)

    results = mycursor.fetchall()

    mycursor.close()
    cnx.close()

    countries_data = {}

    if results is None:
        return json.dumps({'status': 'FAIL'})
    else:
        for country in results:
            country_categories = list(country)
            country_id = country_categories[2]
            total = country_categories[1]
            country_title = country_categories[0]

            country_categories.pop(0)
            country_categories.pop(0)
            country_categories.pop(0)

            # convert to percentages
            percentage_row = []
            for count in country_categories:
                if total > 0:
                    new_value = percentage(count, total)
                else:
                    new_value = 0
                percentage_row.append(round(new_value))

            countries_data[country_id] = {'country_title': country_title, 'count_total': total,
                                          'data': percentage_row}

    return countries_data

def get_formats(in_countries="NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs', 'md')"):
    """
    get the percentages of machine readable and non-proprietary formats of each country

    the lists of machine readable and non-proprietary are extracted from the custom vocabularies of the European Data Portal available here: https://gitlab.com/european-data-portal/edp-vocabularies
    but are originally from the Publications Office of the European Union (n. d.-a). EU Vocabularies. Controlled vocabularies. Authority tables - file-type. Document retrieved June 10, 2020, from https://op.europa.eu/en/web/eu-vocabularies/at-dataset/-/resource/dataset/file-type
    """
    machine_readable_list = ['csv', 'geojson', 'ics', 'json', 'kml', 'kmz', 'netcdf', 'ods', 'rdfa', 'rdfnquads', 'rdfntriples', 'rdftrig', 'rdfturtle', 'rdfxml', 'rss', 'shp', 'xls', 'xlsx', 'xml']

    non_proprietary_list = ['bmp', 'csv', 'dbf', 'geojson', 'gzip', 'html', 'ics', 'jpeg2000', 'json', 'kml', 'kmz', 'netcdf', 'ods', 'png', 'rdfnquads', 'rdfntriples', 'rdftrig', 'rdfturtle', 'rdfxml', 'rss', 'rtf', 'tar', 'tiff', 'tsv', 'txt', 'wms', 'xml', 'zip']
    
    countries_data = {}

    cnx = mysql_connect()
    mycursor = cnx.cursor()

    sql_select = """
                SELECT cl.country_id, GROUP_CONCAT(DISTINCT r.formatting), cl.country_title
                FROM datasets d, catalogues cl, resources r 
                WHERE r.dataset_id = d.dataset_id 
                AND d.catalogue_id = cl.catalogue_id 
                AND cl.country_id """+ in_countries +"""
                AND r.formatting IS NOT NULL
                GROUP BY r.dataset_id
                """

    mycursor.execute(sql_select)

    """
    for each dataset iterate over all its distributions' formats (create lists with GROUP_CONCAT) and find the best format which represents that dataset
    """
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
                countries_data[country_id] = {'data': [0] * 5, 'country_title': dataset[2], 'count_total': 0}

            format_scores = []

            """
            classify the dataset's format by checking all of its resources' formats and finding the best one or if machine readable or non-proprietary are available

            divide the frequencies into these 5 categories:
            ['none of both', 'machine readable', 'non-proprietary', 'machine readable or non-proprietary', 'machine readable and non-proprietary']
            """
            for format in formats:
                format = format.translate(str.maketrans('', '', ".-_/:!,;*+'#&|?\ ")).lower()
                is_machine_readable = False
                is_non_proprietary = False

                for mr_format in machine_readable_list:
                    if mr_format in format:
                        is_machine_readable = True
                        break

                for np_format in non_proprietary_list:
                    if np_format in format:
                        is_non_proprietary = True
                        break

                if is_machine_readable and not is_non_proprietary:
                    format_scores.append(1)
                elif not is_machine_readable and is_non_proprietary:
                    format_scores.append(2)
                elif is_machine_readable and is_non_proprietary:
                    format_scores.append(4)
                else:
                    format_scores.append(0)

            highest_score = max(format_scores)
            if (highest_score == 2) and (1 in format_scores):
                countries_data[country_id]['data'][3] += 1
            else:
                countries_data[country_id]['data'][highest_score] += 1

    mycursor.close()
    cnx.close()

    for country_id in countries_data:
        for format_score_count in countries_data[country_id]['data']:
            countries_data[country_id]['count_total'] += format_score_count

        for idx, val in enumerate(countries_data[country_id]['data']):
            percentage_count = percentage(val, countries_data[country_id]['count_total'])
            countries_data[country_id]['data'][idx] = percentage_count

    return countries_data


