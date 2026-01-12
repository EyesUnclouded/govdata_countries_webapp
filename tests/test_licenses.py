import mysql.connector
import json
import urllib.request

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database='europeandataportal'
)

mycursor = mydb.cursor()

sql_select = """SELECT country_id, country_title FROM catalogues
WHERE country_id NOT IN ('eu', 'ch', 'li', 'is', 'no', 'ua')
GROUP BY country_id
ORDER BY country_id ASC"""

mycursor.execute(sql_select)

results = mycursor.fetchall()

countries = {}

for country in results:
    countries[country[0]] = country[1]

print(countries)

mycursor.close()
mydb.close()
mycursor = mydb.cursor()

sql_select = """SELECT cl.country_id, d.license_id, COUNT(1) AS license_count
FROM datasets d, catalogues cl, resources r 
WHERE r.dataset_id = d.dataset_id 
AND d.catalogue_id = cl.catalogue_id 
AND cl.country_id NOT IN ('eu', 'ch')
AND d.license_id IS NOT NULL
GROUP BY cl.country_id, d.license_id"""

mycursor.execute(sql_select)

results = mycursor.fetchall()

mycursor.close()
mydb.close()

countries_data = {}

full_conformant_licenses = ['Creative Commons CCZero', 'CC0', 'CCZero', 'https://creativecommons.org/publicdomain/zero/1.0/',
                       'http://creativecommons.org/publicdomain/zero/1.0/',
                       'Open Data Commons Public Domain Dedication and Licence', 'ODC PDDL', 'PDDL',
                       'http://www.opendatacommons.org/licenses/pddl/1.0/', 'Creative Commons Attribution 4.0',
                       'CC-BY-4.0', 'https://creativecommons.org/licenses/by/4.0/',
                       'http://creativecommons.org/licenses/by/4.0/', 'Open Data Commons Attribution License', 'ODC-BY',
                       'http://opendatacommons.org/licenses/by/1.0/', 'Creative Commons Attribution Share-Alike 4.0',
                       'CC-BY-SA-4.0', 'http://creativecommons.org/licenses/by-sa/4.0/',
                       'Open Data Commons Open Database License', 'ODbL',
                       'http://opendatacommons.org/licenses/odbl/1.0/', 'Against DRM', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

new_list = ['ccby', 'cc0', 'pddl', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

conformant_licenses = ['creativecommonscczero', 'cc0', 'httpscreativecommonsorgpublicdomainzero10', 'httpcreativecommonsorgpublicdomainzero10', 'opendatacommonspublicdomaindedicationandlicence', 'odcpddl', 'pddl', 'httpwwwopendatacommonsorglicensespddl10', 'creativecommonsattribution40', 'ccby40', 'httpscreativecommonsorglicensesby40', 'httpcreativecommonsorglicensesby40', 'opendatacommonsattributionlicense', 'odcby', 'httpopendatacommonsorglicensesby10', 'creativecommonsattributionsharealike40', 'ccbysa40', 'httpcreativecommonsorglicensesbysa40', 'opendatacommonsopendatabaselicense', 'odbl', 'httpopendatacommonsorglicensesodbl10']

for license in results:
    license_str = str(license[1]).translate({ord(c): None for c in ".-_/:!,;*+'#&|?\ "}).lower()
    country_id = license[0]
    license_count = license[2]

    if country_id not in countries_data:
        countries_data[country_id] = {'data': {}}

    for match_license in conformant_licenses:
        if match_license in license_str:
            if match_license not in countries_data[country_id]['data']:
                countries_data[country_id]['data'][match_license] = license_count
            else:
                countries_data[country_id]['data'][match_license] += license_count


for country_id in countries_data:
    count_total = 0
    for license in countries_data[country_id]['data']:
        count_total += countries_data[country_id]['data'][license]

    countries_data[country_id]['count_total'] = count_total

print(countries_data)


