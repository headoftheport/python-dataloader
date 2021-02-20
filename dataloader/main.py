import getpass
import os
from json.decoder import JSONDecodeError
import json

from simple_salesforce import Salesforce

from .relationship import relationshipInfo
from .export import exportData,exportQuery
from .helpers import mkdir

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

    def exportData(self,objectList):
        mkdir(os.getcwd() + '/data/export')
        for item in objectList:
            exportData(self.sf,item)

    def __getattr__(self, objectName):
        return objectLoader(self.sf,objectName)


class objectLoader:

    def __init__(self,sfToken,objectName):
        self.sfToken = sfToken
        self.objectName = objectName

    def getRelationship(self):
        mkdir(os.getcwd() + '/data/describe')
        return relationshipInfo(self.sfToken, self.objectName)

    def exportData(self,fields, fileName = 'exportfile'):
        queryString = ','.join(fields)
        mkdir(os.getcwd() + '/data/export')
        query = 'SELECT ' + queryString + f' FROM {self.objectName}'
        exportQuery(self.sfToken, query, fileName = fileName)

