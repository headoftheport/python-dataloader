import os
import pandas as pd
import json
import timeit
import numpy as np
import logging
from io import StringIO

from simple_salesforce import SalesforceMalformedRequest

from .exceptions import RecordInsertError

log = logging.getLogger(__name__)

def insert(sfToken, objectName, sourecFile):
    oldNewMap = {}
    insertList = []
    df = pd.read_csv(sourecFile)
    df = df.replace(np.nan, '', regex=True)
    
    for index, row in df.iterrows():
        try:
            oldId = str(row['Id'])
            insertData = row.drop(labels=['Id'],index = None)
            finalData = dict((key,value) for key, value in insertData.to_dict().items() if value is not '')
            
            insertStatus = sfToken.__getattr__(objectName).create(finalData)
            if insertStatus['success'] == True and oldId != 'None':
                oldNewMap[oldId] = (str(insertStatus['id']))
            insertList.append(insertStatus)
        except SalesforceMalformedRequest as e:
            log.error(e)
            raise RecordInsertError(objectName, oldNewMap, row, insertList)
            

    successDataFrame = pd.DataFrame(insertList)
    successFile = os.getcwd() + f"/data/success/{objectName}-insert-{str(timeit.default_timer())}.csv"
    log.info('Insert completed: %s ; Record Count: %d/%d'%(objectName, len(insertList), df.shape[0]))
    successDataFrame.to_csv(successFile)

    return oldNewMap

def update(sfToken, objectName, sourecFile):
    # sourecFile = os.getcwd() + f"/data/import/{objectName}-update.csv"
    df = pd.read_csv(sourecFile)
    df = df.replace(np.nan, '', regex=True)
    errorCount = 0
    successCount = 0
    recordList = df.to_dict('records')
    updateStatus = sfToken.bulk.__getattr__(objectName).update(recordList)

    successStrings = map(json.dumps,updateStatus)
    df['status'] = list(successStrings)
    for index, row in df.iterrows():
        if json.loads(row['status'])['success'] == True:
            successCount = successCount + 1
        else:
            errorCount = errorCount + 1

    successFile = os.getcwd() + f"/data/success/{objectName}-update-{str(timeit.default_timer())}.csv"
    log.info('Update completed: %s ; Record Count: %d ; Success : %d ; Error : %d '%(objectName, len(recordList), successCount, errorCount))
    df.to_csv(successFile)

    return successFile

def export(sfToken,objectName, query):
        
    queryResult = sfToken.query_all(query)
    records = queryResult['records']
    size = queryResult['totalSize']
    if size == 0:
        log.warning('No data exported: %s'%objectName)
        return None

    json_data = json.dumps(records)
    df = pd.read_json(StringIO(json_data))

    csvFileName = os.getcwd() + f'/data/export/{objectName}.csv'
    df.to_csv(csvFileName,index = False)
    
    log.info('Data exported: [%s]: Record Count: [%d]'%(objectName,size))

    return csvFileName

def relationshipInfo(sfToken, objectName):
        objectInfo = {}
        
        jsonElement = sfToken.__getattr__(objectName).describe()
        if jsonElement == None:
            log.warning('Metadata could not be extracted: %s'%objectName)
            return None
        

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
        log.info('Metadata extracted: [%s]'%objectName)
        return tempDict


