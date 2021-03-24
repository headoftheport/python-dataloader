import getpass
import os
from json.decoder import JSONDecodeError
import json

from simple_salesforce import Salesforce

from .helpers import mkdir
from .operations import exportData, relationshipInfo, insertData, updateData
from .csvProcessor import processCSV
from .database import insertMapping

class dataloader:

    def __init__(self, instance = 'test',userName = None, password = None, securityToken = None):
        self.instance = instance
    
        if self.instance != 'test':
            raise
        userName = userName if userName != None else input("username: ")
        password = password if password != None else getpass.getpass(prompt = 'password: ')
        securityToken = securityToken if securityToken != None else getpass.getpass(prompt = 'security token: ')
        self.sf = Salesforce(
            username= userName, 
            password= password, 
            security_token= securityToken, 
            client_id='Python Dataloader', 
            domain= self.instance
        )

    def exportRelationship(self,objectList):
        mkdir(os.getcwd() + '/data/describe')
        fileContent = {}  
        if os.path.exists("./data/relationship-info.json"):
            with open("./data/relationship-info.json","r") as file:
                try:
                    fileContent = json.load(file)
                except JSONDecodeError: 
                    pass

        for item in objectList:
            tempDict = relationshipInfo(self.sf,item)
            fileContent[item] = tempDict

        with open("./data/relationship-info.json","w") as file:
            json.dump(fileContent,file)

    def exportData(self,objectName):
        mkdir(os.getcwd() + '/data/export')
        fileContent = {}
        with open("./data/relationship-info.json","r") as file:
            fileContent = json.load(file)

        query = fileContent[objectName]['query']
        exportData(self.sf,objectName, query)

    def insertData(self,objectName, session):
        mkdir(os.getcwd() + '/data/import')
        mkdir(os.getcwd() + '/data/success')
        fileContent = {}
        with open("./data/relationship-info.json","r") as file:
            fileContent = json.load(file)
            
        filePath = processCSV(session,objectName,fileContent[objectName],'insert')
        idMapping = insertData(self.sf,objectName, filePath)
        insertMapping(session,objectName,idMapping)
    
    def updateData(self,objectName, session):
        mkdir(os.getcwd() + '/data/import')
        mkdir(os.getcwd() + '/data/success')
        fileContent = {}
        with open("./data/relationship-info.json","r") as file:
            fileContent = json.load(file)
        
        filePath = processCSV(session,objectName,fileContent[objectName],'update')
        updateData(self.sf,objectName, filePath)

    def __getattr__(self, objectName):
        return objectLoader(self.sf,objectName)


class objectLoader:

    def __init__(self,sfToken,objectName):
        self.sfToken = sfToken
        self.objectName = objectName

    def getRelationship(self):
        mkdir(os.getcwd() + '/data/describe')
        return relationshipInfo(self.sfToken, self.objectName)

    def exportData(self,  fields = []):
        mkdir(os.getcwd() + '/data/export')
        if len(fields) == 0:
            return exportData(self.sfToken,self.objectName, self.getRelationship()['query'])
        query = 'SELECT ' + ','.join(fields) + ' FROM ' + self.objectName
        return exportData(self.sfToken,self.objectName, query)

    def insertData(self, filePath):
        return insertData(self.sfToken,self.objectName, filePath)

    def updateData(self, filePath):
        return updateData(self.sfToken,self.objectName, filePath)



