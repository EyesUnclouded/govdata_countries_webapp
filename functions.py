import mysql.connector
import numpy as np

def mysql_connect():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database='europeandataportal'
    )
    return mydb


def percentage(value, total):
    return round(100 * float(value) / float(total), 2)

"""
detect_outliers
Khandelwal, R. (2018). Finding outliers in dataset using python. Retrieved April 6, 2020 from https://medium.com/datadriveninvestor/finding-outliers-in-dataset-using-python-efc3fce6ce32
"""
def detect_outliers(data_1):
    outliers = []
    threshold = 3
    mean_1 = np.mean(data_1)
    std_1 = np.std(data_1)

    for y in data_1:
        z_score = (y - mean_1) / std_1
        if np.abs(z_score) > threshold:
            outliers.append(y)
    return outliers

