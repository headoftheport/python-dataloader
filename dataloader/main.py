import getpass
import os
from json.decoder import JSONDecodeError
import json
import logging

from simple_salesforce import Salesforce

from .helpers import mkdir
from .operations import export, relationshipInfo, insert, update, queryToDelete, delete
from .csvProcessor import processCSV
from .database import insertMapping
from .exceptions import RecordInsertError

log = logging.getLogger(__name__)

LINE = '=' * 15
class dataloader:

    def __init__(self, instance = 'test',userName = None, password = None, securityToken = None, echo = True):
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
        if ( not echo):
            self._echo = False
            logging.getLogger(__package__).setLevel(logging.WARNING)

        log.info('Logged in to: %s as: %s'%(self.sf.sf_instance,userName))

    @property
    def echo(self):
        return self._echo

    @echo.setter
    def echo(self, value):
        if ( value == True):
            self._echo = True
            logging.getLogger(__package__).setLevel(logging.DEBUG)
        elif( value == False ):
            self._echo == False
            logging.getLogger(__package__).setLevel(logging.WARNING)
        else:
            log.warning('Invalid Value: %s'%str(value))

    def exportRelationship(self,objectList):
        metadataPath = mkdir(os.getcwd() + '/data/describe')
        fileContent = {}  
        if os.path.exists("./data/relationship-info.json"):
            with open("./data/relationship-info.json","r") as file:
                try:
                    fileContent = json.load(file)
                except JSONDecodeError: 
                    pass
        
        for item in objectList:
            tempDict = relationshipInfo(self.sf,item)
            if tempDict != None:
                fileContent[item] = tempDict
            
        with open("./data/relationship-info.json","w") as file:
            json.dump(fileContent,file)
            log.info('Updating relationship-info file...')
        
        log.info('Metadata Folder Path: %s'%metadataPath)
        return './data/relationship-info.json'

    def exportData(self,objectName):
        mkdir(os.getcwd() + '/data/export')
        fileContent = {}
        with open("./data/relationship-info.json","r") as file:
            fileContent = json.load(file)

        try:
            query = fileContent[objectName]['query']
            if query == None or query == '' or not (objectName in query):
                log.warning('Invalid Query: %s'%objectName)
                return None
            return export(self.sf,objectName, query)
        except KeyError:
            log.warning('Export query could not be found: %s'%objectName)
            return None

    def insertData(self,objectName, session):
        mkdir(os.getcwd() + '/data/import')
        mkdir(os.getcwd() + '/data/success')
        fileContent = {}
        with open("./data/relationship-info.json","r") as file:
            fileContent = json.load(file)

        log.info('\n%s INSERT: %s %s\n'%(LINE,objectName,LINE))
        if not (objectName in fileContent.keys()):
            log.warning('Object could not found in relationship-info.json: %s'%objectName)
            return None
        
        filePath = processCSV(session,objectName,fileContent[objectName],'insert')
        try:
            idMapping = insert(self.sf,objectName, filePath)
        except RecordInsertError as error:
            log.error(error)
            exit()
        
        if idMapping:
            insertMapping(session,objectName,idMapping)
            
        log.info('\n%s FINISH: %s %s\n'%(LINE,objectName,LINE))

    def updateData(self,objectName, session):

        log.info('\n%s UPDATE: %s %s\n'%(LINE,objectName,LINE))
        mkdir(os.getcwd() + '/data/import')
        mkdir(os.getcwd() + '/data/success')
        fileContent = {}
        with open("./data/relationship-info.json","r") as file:
            fileContent = json.load(file)
        
        if not (objectName in fileContent.keys()):
            log.warning('Object could not found in relationship-info.json: %s'%objectName)
            return None
        
        filePath = processCSV(session,objectName,fileContent[objectName],'update')
        
        update(self.sf,objectName, filePath)
        log.info('\n%s FINISH: %s %s\n'%(LINE,objectName,LINE))

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

    def deleteAll(self):
        deleteItems = queryToDelete(self.sfToken,self.objectName)
        if deleteItems == None:
            return
        delete(self.sfToken,self.objectName,deleteItems)


