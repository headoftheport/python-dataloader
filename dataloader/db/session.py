import logging

from . import database, Session, jobDetail, idMapping

log = logging.getLogger(__name__)

class mapping_session(database):

    def __init__(self,sessionName,sourceName,destinationName):
        super().__init__(sessionName)
        self.jobId = sessionName
        self.source = sourceName
        self.destination = destinationName
        self.new_session = Session()
    
    def __del__(self):
        self.new_session.close()
        
    def insert_mapping(self,objectName: str, mapping: dict):
    #check if the job exists insert new job if not there in the database
        job = self.new_session.query(jobDetail).filter_by(job_id=self.jobId).first()
        if(job == None):
            newJob = jobDetail(self.jobId,self.source,self.destination)
            self.new_session.add(newJob)
            self.new_session.commit()
            log.info("New Job created in database. %s"%self.jobId)
        values = list(dict(job_id = self.jobId,object_name=objectName.lower(), source_id = key, destination_id = value ) for key , value in mapping.items())
        self.new_session.bulk_insert_mappings(idMapping,values)
        self.new_session.commit()
        log.info("Mappings inserted to database with jobId: %s ; %s ; %d mappings"%(self.jobId,objectName, len(mapping.keys())))
    
    def retrieve_mapping(self,objectList: list) -> dict:
        log.info('Retrieving mappings for the objects: %s'%(','.join(objectList)))
        result = self.new_session.query(idMapping).filter(idMapping.object_name.in_(objectList),idMapping.job_id == self.jobId)
        returnResult  = dict()
        for item in result:
            returnResult[str(item.source_id)] = str(item.destination_id)
        return returnResult

    def delete_mapping(self, objectList):
        log.info('Deleting mappings for the objects: %s'%(','.join(objectList)))
        objectList = list(map(lambda x: str.lower(x), objectList))
        delete_count = self.new_session.query(idMapping).filter(idMapping.object_name.in_(objectList),idMapping.job_id == self.jobId).delete(synchronize_session=False)
        self.new_session.commit()
        log.info('Total deleted rows : %d'%(delete_count))
        return delete_count