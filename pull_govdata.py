import requests
import json
import datetime
import os.path

#"%I:%M%p on %B %d, %Y"
european_countries_dict = {'austria': 'www.data.gv.at/katalog', 'belgium': 'data.gov.be', 'bulgaria': 'opendata.government.bg', 'croatia': 'data.gov.hr', 'cyprus': 'data.gov.cy', 'czech_republic': 'datahub.io/organization/cz-ckan-net', 'denmark': 'portal.opendata.dk', 'finland': 'www.opendata.fi/data', 'france': 'data.gouv.fr/fr', 'germany': 'ckan.govdata.de', 'greece': 'data.gov.gr', 'ireland': 'data.gov.ie', 'italy': 'www.dati.gov.it', 'lithuania': 'opendata.gov.lt', 'luxembourg': 'data.public.lu', 'netherlands': 'data.overheid.nl/data', 'poland': 'danepubliczne.gov.pl', 'portugal': 'dados.gov.pt', 'romania': 'data.gov.ro', 'slovakia': 'data.gov.sk', 'spain': 'datos.gob.es', 'sweden': 'oppnadata.se', 'united_kingdom': 'data.gov.uk'}

def prepare_govdata_dict(data_resources, country, error = 0):
    # create sanitized output dict
    data_resources_dict = {"data": {},"date": datetime.datetime.now().isoformat(), "country": country}

    if error != 0:
        data_resources_dict[0]["error"] = error
        return data_resources_dict

    id_list = []
    id_duplicates = []

    for elem in data_resources:
        # check for duplicates
        if elem["id"] not in id_list:
            #name_list.append(elem["name"])
            id_list.append(elem["id"])
            data_resources_dict["data"][elem["id"]] = elem
        else:
            id_duplicates.append(elem)

    return data_resources_dict

def prepare_govdata_list(data_resources, country, error = 0):
    # create sanitized output dict
    #metadata = {"date": datetime.datetime.now().isoformat(), "country": country, "data": []}

    data_resources_return = [{"date": datetime.datetime.now().isoformat(), "country": country, "data": []}]


    if error != 0:
        data_resources_return[0]["error"] = error
        return data_resources_return

    id_list = []
    id_duplicates = []


    for elem in data_resources:
        # check for duplicates
        if elem["id"] in id_list:
            id_duplicates.append(elem)
        else:
            data_resources_return.append(elem)
            id_list.append(elem["id"])

    return data_resources_return

def select_fields(govdataset):
    compact_govdataset = {"id": govdataset["id"], "num_tags": govdataset["num_tags"], "metadata_created": govdataset["metadata_created"], "metadata_modified": govdataset["metadata_modified"], "author": govdataset["author"], "state": govdataset["state"], "type": govdataset["type"], "tags": [], "groups": [], "resources": []}

    for resource in govdataset["resources"]:
        compact_govdataset[resources].append({"id": resource["id"], "issued": resource["issued"], "modified": resource["modified"], "package_id": resource["package_id"], "license": resource["license"], "format": resource["format"]})

    return compact_govdataset

def get_govdata(govdata_url = "ckan.govdata.de", govdata_name = "germany"):
    error = 0
    limit = 1000
    data_resources = []
    result_number = limit
    offset = 0
    my_timeout = 60

    #current_package_list_with_resources is limited to 1000 results per page/offset
    #repeat request until results are less than the limit 1000 which means there is no next offset
    while result_number == limit:
        datasets_clean = []
        try:
            data_request = requests.get("https://"+govdata_url+"/api/3/action/current_package_list_with_resources?limit="+str(limit)+"&offset="+str(offset), timeout=my_timeout).json()
        except:
            try:
                data_request = requests.get("http://" + govdata_url + "/api/3/action/current_package_list_with_resources?limit=" + str(limit) + "&offset=" + str(offset), timeout=my_timeout).json()
            except:
                try:
                    data_request = requests.get("https://" + govdata_url + "/api/1/action/current_package_list_with_resources?limit=" + str(limit) + "&offset=" + str(offset), timeout=my_timeout).json()
                except:
                    try:
                        data_request = requests.get("http://" + govdata_url + "/api/1/action/current_package_list_with_resources?limit=" + str(limit) + "&offset=" + str(offset), timeout=my_timeout).json()
                    except:
                        error = 1
                        break
        #check if data is at the right place in the right shape
        if "result" in data_request and isinstance(data_request["result"], list):
            print(len(data_resources))
            result_number = len(data_request["result"])
            #sometimes the data is nested in another list
            if result_number > 1:
                datasets = data_request["result"]
            else:
                datasets = data_request["result"][0]


            #only pick necessary fields
            for dataset in datasets:
                tmp_dataset = {"id": dataset["id"], "groups": []}

                #literally every country has a different way to save the category
                if "groups" in dataset and len(dataset["groups"]) > 0:
                    for group in dataset["groups"]:
                        tmp_dataset["groups"].append(group["title"])
                elif "categorization" in dataset:
                    tmp_dataset["groups"].append(dataset["categorization"])
                elif "theme-primary" in dataset:
                    tmp_dataset["groups"].append(dataset["theme-primary"])

                datasets_clean.append(tmp_dataset)

            data_resources = data_resources + datasets_clean

        else:
            error = 2
            break
        #start next request at new offset
        offset += limit

    output_dict = prepare_govdata_list(data_resources, govdata_name, error)

    print(govdata_name + " error: "+ str(error))

    return output_dict


def create_govdata_countries():
    govdata_european_countries_dict = {}

    for country in european_countries_dict:
        """
        if os.path.exists("static/data/govdata_"+country+".json"):
            print("exists: "+country)
            continue
        
        try:
            with open("static/data/govdata_" + country + ".json") as govdata_file:
                govdata_str = govdata_file.read()
                try:
                    govdata = json.loads(govdata_str)
                except:
                    continue
                if len(govdata["data"]) > 0:
                    continue
        except:
            print(country)
        """

        govdata_european_countries_dict[country] = get_govdata(european_countries_dict[country], country)

        #create txt with each line as json object
        #so that i can read the files line by line and dont run out of memory
        with open('static/data/govdata_' + country + '.txt', 'w') as outfile:
            for elem in govdata_european_countries_dict[country]:
                outfile.write(json.dumps(elem) + "\n")

        #create one large nested json file
        """
        with open('static/data/govdata_' + country + '.json', 'w') as outfile:
            json.dump(govdata_european_countries_dict[country], outfile)
        """

    #return govdata_european_countries_dict


def test_portals():
    for country in european_countries_dict:
        govdata_url = european_countries_dict[country]
        my_timeout = 60
        print(country)
        try:
            data_request = requests.get("https://" + govdata_url + "/api/3/action/current_package_list_with_resources", timeout=my_timeout).json()
            print( "https://" + govdata_url + "/api/3/action/current_package_list_with_resources")
        except:
            try:
                data_request = requests.get("http://" + govdata_url + "/api/3/action/current_package_list_with_resources", timeout=my_timeout).json()
                print("http://" + govdata_url + "/api/3/action/current_package_list_with_resources")
            except:
                try:
                    data_request = requests.get("https://" + govdata_url + "/api/1/action/current_package_list_with_resources", timeout=my_timeout).json()
                    print("https://" + govdata_url + "/api/1/action/current_package_list_with_resources")
                except:
                    try:
                        data_request = requests.get("http://" + govdata_url + "/api/1/action/current_package_list_with_resources", timeout=my_timeout).json()
                        print("http://" + govdata_url + "/api/1/action/current_package_list_with_resources")
                    except:
                        continue

test_portals()




