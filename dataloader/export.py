import os
import json
import pathlib

import pandas as pd

def exportData(sfToken,objectName):
        fileContent = {}
        with open("./data/relationship-info.json","r") as file:
            fileContent = json.load(file)

        if objectName in fileContent.keys():
            query = fileContent[objectName]['query']

            records = sfToken.query_all(query)['records']
            json_data = json.dumps(records)
            df = pd.read_json(json_data)

            csvFileName = f'./data/export/{objectName}.csv'
            df.to_csv(csvFileName)
            return True
        
        else:
            return False

def exportQuery(sfToken, query, fileName):
    records = sfToken.query_all(query)['records']
    json_data = json.dumps(records)
    df = pd.read_json(json_data)
   
    csvFileName = f'./data/export/{fileName}.csv'
    df.to_csv(csvFileName)
            
