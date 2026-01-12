import urllib.request
import concurrent.futures
import mysql.connector

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database='europeandataportal'
    )

mycursor = mydb.cursor(buffered=True)
mycursor2 = mydb.cursor()

def get_status(resource):
    try:
        response_status = urllib.request.urlopen(resource[1], timeout=5).getcode()
        if response_status == 200 or response_status == 300:
            accessible = 1
        else:
            accessible = 0
    except:
        accessible = 0
    return accessible, resource[0]

def multiprocessing_requests(resources):
    with concurrent.futures.ThreadPoolExecutor(max_workers=400) as executor:
        resources_values = list(executor.map(get_status, resources))

    sql_update = """
               UPDATE resources
               SET url_accessible = %s
               WHERE resource_id = %s;
               """
    mycursor2.executemany(sql_update, resources_values)
    mydb.commit()

if __name__ == "__main__":
    sql_select = """SELECT r.resource_id, r.access_url
        FROM resources r, datasets d, catalogues cl 
        WHERE r.dataset_id = d.dataset_id 
        AND d.catalogue_id = cl.catalogue_id 
        AND cl.country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua', 'rs') 
        AND r.url_accessible IS NULL"""
    mycursor.execute(sql_select)
    fetchsize = 1000
    crash_breaker = 0
    while crash_breaker < 999:
        crash_breaker += 1
        print(crash_breaker)
        resources = mycursor.fetchmany(fetchsize)
        if not resources:
            break
        multiprocessing_requests(resources)
    mycursor.close()
    mydb.close()
