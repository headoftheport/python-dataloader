import os

import pandas as pd
import numpy as np

from .helpers import mkdir
from .database import retrieveMapping

def processCSV(session, objectName, relationInfo, action):

    fields = set(relationInfo['creatableFields'])
    lookupFields = set(relationInfo['lookUp'].keys())
    masterDetailFields = set(relationInfo['masterDetail'].keys())

    sourcePath = f'./data/export/{objectName}.csv'
    df = pd.read_csv(sourcePath)
    if action == 'insert':
        #if the action is insert remove the columns in lookup field
        fields = fields.difference(lookupFields)
        fields.add('Id')
        #if master fields not empty resolve relationships
        resolveList = set()
        for key, value in relationInfo['masterDetail'].items():
            resolveList.add(value)
        if len(resolveList) > 0:
            resolveIds = retrieveMapping(session, resolveList)
            df = df.replace(resolveIds)
 
    elif action == 'update':
        fields = lookupFields
        fields.add('Id')
        #resolve for the lookup relationship
        resolveList = set({objectName})
        for key, value in relationInfo['lookUp'].items():
            resolveList.add(value)
        resolveIds = retrieveMapping(session, resolveList)
        df = df.replace(resolveIds)

    fileColumns = set(df.columns.values)
    finalColumns = fileColumns.intersection(set(fields))
    df = df[finalColumns].dropna(how='all',axis='columns')

    destPath = f'./data/import/{objectName}-{action}.csv'
    df.to_csv(destPath,index = False)

    return destPath

