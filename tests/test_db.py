import requests
import json
import mysql.connector
import dateutil.parser
import traceback

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database='europeandataportal'
)

mycursor = mydb.cursor()


# save categories/catalogues in variable so we don't have to query it every time
# keep count of catalogues and categories that have already been inserted
categories_in_db = {}
catalogues_in_db = {}
datasets_no_resources = []
datasets_not_resources_inserted = []

def dataset_to_db(dataset):
    """

    CATALOGUE

    """
    if "organization" in dataset:

        if "idName" in dataset["organization"] and dataset["organization"]["idName"] is not None:
            idName = dataset["organization"]["idName"]
        else:
            idName = ""

        if idName not in catalogues_in_db:
            sql_check_catalogue = "SELECT catalogue_id FROM catalogues WHERE idName = %s"

            # query + values, (dataset,) the comma because tuple with single element
            mycursor.execute(sql_check_catalogue, (dataset["organization"]["idName"],))

            catalogue = mycursor.fetchone()

            if catalogue == None:
                # insert
                # check for all fields

                if "country" in dataset["organization"]:
                    country = dataset["organization"]["country"]
                    if "title" in country:
                        country_title = country["title"]
                    else:
                        country_title = ""

                    if "id" in country:
                        country_id = country["id"]
                    else:
                        country_id = ""
                else:
                    country_title = ""
                    country_id = ""

                if ("description" in dataset["organization"]) and (dataset["organization"]["description"] != None) and (len(dataset["organization"]["description"]) > 0):
                    # get description of organization
                    desc_dict = dataset["organization"]["description"]
                    if "en" in desc_dict:
                        # get english description
                        catalogue_description = desc_dict["en"]
                    else:
                        # if not available take first language (mostly just one available)
                        catalogue_description = desc_dict[list(desc_dict.keys())[0]]
                else:
                    catalogue_description = ""

                if ("title" in dataset["organization"]) and (dataset["organization"]["title"] != None) and (len(dataset["organization"]["title"]) > 0):
                    # get title the same like description
                    title_dict = dataset["organization"]["title"]
                    if "en" in title_dict:
                        catalogue_title = title_dict["en"]
                    else:
                        catalogue_title = title_dict[list(title_dict.keys())[0]]
                else:
                    catalogue_title = ""

                # finally insert

                sql_catalogue = "INSERT INTO catalogues (idName, title, description, country_title, country_id) VALUES (%s, %s, %s, %s, %s)"
                val_catalogue = (idName, catalogue_title, catalogue_description, country_title, country_id)

                #print("catalogue: ", val_catalogue)

                mycursor.execute(sql_catalogue, val_catalogue)

                catalogue_id = mycursor.lastrowid

                catalogues_in_db[dataset["organization"]["idName"]] = catalogue_id
            else:
                catalogue_id = catalogue[0]
        else:
            catalogue_id = catalogues_in_db[idName]
    else:
        # 0 which stands for no catalogue
        catalogue_id = 0

    """

    DATASET

    """
    # check if values exist
    field_list = ["id", "name", "title", "metadata_created", "metadata_modified", "licence_id", "licence"]
    for field in field_list:
        if field not in dataset:
            dataset[field] = None
        elif (field == "metadata_created" or field == "metadata_modified") and dataset[field] is not None:
            # dates are in iso 8601, need to convert to database datetime
            isodate = dataset[field]
            mydate = dateutil.parser.parse(isodate)
            dataset[field] = mydate.strftime('%Y-%m-%d %H:%M:%S')

    sql_dataset = "INSERT INTO datasets (eu_id, eu_name, title, metadata_created, metadata_modified, license_id, license, catalogue_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val_dataset = (dataset["id"], dataset["name"], dataset["title"], dataset["metadata_created"], dataset["metadata_modified"], dataset["licence_id"], dataset["licence"], catalogue_id)

    #print("dataset: ", val_dataset)

    mycursor.execute(sql_dataset, val_dataset)

    dataset_id = mycursor.lastrowid

    """
    
    CATEGORIES
    
    """
    if "groups" in dataset and len(dataset["groups"]) > 0:

        groups = dataset["groups"]

        for group in groups:
            # check if group/category in db if not insert
            if ("name" not in group) and ("id" not in group):
                continue

            elif group['name'] not in categories_in_db:
                sql_check_category = "SELECT category_id FROM categories WHERE eu_name = %s OR eu_id = %s"

                mycursor.execute(sql_check_category, (group['name'], group['id']))

                category = mycursor.fetchone()

                if category == None:
                    sql_category = "INSERT INTO categories (eu_name, eu_id) VALUES (%s, %s)"
                    val_category = (group['name'], group['id'])

                    mycursor.execute(sql_category, val_category)

                    category_id = mycursor.lastrowid

                else:
                    category_id = category[0]

                categories_in_db[group['name']] = category_id

            else:
                category_id = categories_in_db[group['name']]

            # connect dataset with category
            sql_group = "INSERT INTO datasets_to_categories (dataset_id, category_id) VALUES (%s, %s)"

            mycursor.execute(sql_group, (dataset_id, category_id))

    mydb.commit()
    """
    
    RESOURCES
    
    """

    if "resources" in dataset and len(dataset["resources"]) > 0:
        resources = dataset["resources"]
        #print(resources)
        field_list = ["id", "access_url", "format", "created", "last_modified"]
        val_resource_list = []
        for resource in resources:
            #check if values exist
            for field in field_list:
                if field not in resource:
                    resource[field] = None
                elif (field == "created" or field == "last_modified") and resource[field] is not None:
                    # dates are in iso 8601, need to convert to database datetime
                    isodate = resource[field]
                    mydate = dateutil.parser.parse(isodate)
                    resource[field] = mydate.strftime('%Y-%m-%d %H:%M:%S')

            val_resource_list.append((resource["id"], resource["access_url"], resource["format"], resource["created"], resource["last_modified"], dataset_id))

        #print(val_resource_list)
        sql_resource = """INSERT INTO resources (eu_id, access_url, formatting, created, last_modified, dataset_id) VALUES (%s, %s, %s, %s, %s, %s)"""

        #print("resources: ", val_resource_list)

        mycursor.executemany(sql_resource, val_resource_list)

        mydb.commit()

        # check if all resources got inserted

        sql_select = """SELECT COUNT(1) as count_resources FROM resources WHERE dataset_id = %s"""
        mycursor.execute(sql_select, (dataset_id,))

        count_resources = mycursor.fetchone()

        if (count_resources[0] != len(dataset["resources"])) or (count_resources[0] != len(val_resource_list)):
            datasets_not_resources_inserted.append([dataset_id, dataset])
    else:
        datasets_no_resources.append(dataset_id)

    """
    
    RETURN
    
    """
    return 1

faulty_datasets = []

def get_europeandataportal():
    max_limit = 700000000
    count = 0
    limit = 1000
    result_number = limit
    offset = 0
    # package_search is limited to 1000 results per page/offset on europeandataportal
    # repeat request until results are less than the limit 1000 which means there is no next offset
    while offset < max_limit and result_number == limit:
        data_request = requests.get("https://www.europeandataportal.eu/data/search/ckan/package_search?rows="+str(limit)+"&start="+str(offset)).json()
        data_list = data_request["result"]["results"]

        result_number = len(data_list)
        offset += limit
        # do this for every dataset:
        for dataset in data_list:
            # print(dataset)
            try:
                dataset_to_db(dataset)
            except Exception as ex:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                print(">>>>ERROR IN DATASET<<<<:", dataset)
                faulty_datasets.append([message, dataset])

        print('not all resources inserted:')
        print(datasets_not_resources_inserted)
        print(offset)



get_europeandataportal()

#test specific dataset
"""
data_request = requests.get("https://www.europeandataportal.eu/data/search/ckan/package_show?id=epixeirhseis-poy-diegrafhsan-apo-to-mhtrwo-taxydromikwn-epixeirhsewn").json()
dataset = data_request["result"]

print(dataset)
dataset_to_db(dataset)
"""
print('no resources:')
print(datasets_no_resources)

print('failed to insert:')
print(faulty_datasets)

print('not all resources inserted:')
print(datasets_not_resources_inserted)