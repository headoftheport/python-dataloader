import os
import pandas as pd
import json
import timeit
import numpy as np

def insertData(sfToken, objectName, sourecFile):
    oldNewMap = {}
    insertList = []
    #sourecFile = os.getcwd() + f"/data/import/{objectName}-insert.csv"
    df = pd.read_csv(sourecFile)
    df = df.replace(np.nan, '', regex=True)
    
    for index, row in df.iterrows():
        oldId = str(row['Id'])
        insertData = row.drop(labels=['Id'],index = None)
        finalData = dict((key,value) for key, value in insertData.to_dict().items() if value is not '')
        insertStatus = sfToken.__getattr__(objectName).create(finalData)
        if insertStatus['success'] == True and oldId != 'None':
            oldNewMap[oldId] = (str(insertStatus['id']))
        insertList.append(insertStatus)

    successDataFrame = pd.DataFrame(insertList)
    successFile = os.getcwd() + f"/data/success/{objectName}-insert-{str(timeit.default_timer())}.csv"
    successDataFrame.to_csv(successFile)

    return oldNewMap

def updateData(sfToken, objectName, sourecFile):
    # sourecFile = os.getcwd() + f"/data/import/{objectName}-update.csv"
    df = pd.read_csv(sourecFile)
    df = df.replace(np.nan, '', regex=True)
    recordList = df.to_dict('records')
    updateStatus = sfToken.bulk.__getattr__(objectName).update(recordList)

    successStrings = map(json.dumps,updateStatus)
    df['status'] = list(successStrings)

    successFile = os.getcwd() + f"/data/success/{objectName}-update-{str(timeit.default_timer())}.csv"
    df.to_csv(successFile)

    return successFile

def exportData(sfToken,objectName, query):
        
    records = sfToken.query_all(query)['records']
    json_data = json.dumps(records)
    df = pd.read_json(json_data)

    csvFileName = os.getcwd() + f'/data/export/{objectName}.csv'
    df.to_csv(csvFileName,index = False)
    
    return csvFileName

def relationshipInfo(sfToken, objectName):
        objectInfo = {}
        
        jsonElement = sfToken.__getattr__(objectName).describe()

        with open(f"./data/describe/{objectName}.json",'w') as file:
            json.dump(jsonElement,file)
        
        tempDict, masterDeatil, lookup = {}, {}, {}
        fields, creatableFields = [], []
        
        for item in jsonElement['fields']:
            
            fields.append(item["name"])

            if item["nillable"] == False and item["type"] == "reference" and item["createable"]:
                masterDeatil[item["name"]] = item["referenceTo"][0]
                creatableFields.append(item["name"])
            elif item["type"] == "reference" and item["createable"]:
                lookup[item["name"]] = item["referenceTo"][0]
                creatableFields.append(item["name"])
            elif item["createable"]:
                creatableFields.append(item["name"])
                
        queryString = ','.join(fields)
        tempDict['query'] = 'SELECT ' + queryString + f' FROM {objectName}'
        tempDict['creatableFields'] = creatableFields
        tempDict['masterDetail'] = masterDeatil
        tempDict['lookUp'] = lookup
    
        return tempDict


