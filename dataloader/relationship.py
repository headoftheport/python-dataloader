import os
import json
from json.decoder import JSONDecodeError

def relationshipInfo(sfToken, objectName):
        objectInfo = {}
        
        jsonElement = sfToken.__getattr__(objectName).describe()

        with open(f"./data/describe/{objectName}.json",'w') as file:
            json.dump(jsonElement,file)
        
        tempDict, masterDeatil, lookup = {}, {}, {}
        fields, creatableFields = [], []
        
        for item in jsonElement['fields']:
            
            fields.append(item["name"])

            if item["nillable"] == False and item["type"] == "reference" and item["custom"]:
                masterDeatil[item["name"]] = item["referenceTo"][0]
            elif item["type"] == "reference" and item["custom"]:
                lookup[item["name"]] = item["referenceTo"][0]

            if item["createable"]:
                creatableFields.append(item["name"])
                
        queryString = ','.join(fields)
        tempDict['query'] = 'SELECT ' + queryString + f' FROM {objectName}'
        tempDict['creatableFields'] = creatableFields
        tempDict['masterDetail'] = masterDeatil
        tempDict['lookUp'] = lookup
    
        return tempDict

