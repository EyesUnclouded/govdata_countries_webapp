import mysql.connector
import urllib.request
import multiprocessing

mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database='europeandataportal'
    )

mycursor = mydb.cursor(buffered=True)
mycursor2 = mydb.cursor()

def request_and_return(resource):
    resource_id = resource[0]
    access_url = resource[1]

    try:
        response_status = urllib.request.urlopen(access_url, timeout=5).getcode()

        if response_status == 200 or response_status == 300:
            accessible = 1
        else:
            accessible = 0
    except:
        accessible = 0

    return (accessible, resource_id)

def multiprocessing_requests(resources):
    print('start multiprocessing')
    #p = multiprocessing.Pool(multiprocessing.cpu_count())
    p = multiprocessing.Pool(50)
    resources_values = p.map(request_and_return, resources)

    sql_update = """
        UPDATE resources
        SET url_accessible = %s
        WHERE resource_id = %s;
        """

    mycursor2.executemany(sql_update, resources_values)
    mydb.commit()

    print("+ 100")

    p.close()
    p.join()

if __name__ == '__main__':
    sql_select = """SELECT r.resource_id, r.access_url 
    FROM resources r, datasets d, catalogues cl 
    WHERE r.dataset_id = d.dataset_id 
    AND d.catalogue_id = cl.catalogue_id 
    AND cl.country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua') 
    AND r.url_accessible IS NULL 
    ORDER BY r.resource_id ASC"""

    mycursor.execute(sql_select)

    fetchsize = 100000
    batch_size = 500

    # crash_breaker to not use while True
    crash_breaker = 0
    while crash_breaker < 99999999:
        crash_breaker += 1
        print(crash_breaker)

        resources = mycursor.fetchmany(fetchsize)
        if not resources:
            break

        for i in range(0, len(resources), batch_size):
            multiprocessing_requests(resources[i:i + batch_size])

    mycursor.close()
    mydb.close()


