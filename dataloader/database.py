import logging

from .helpers import engine, Session , jobDetail, idMapping

log = logging.getLogger(__name__)
class DBsession:

    def __init__(self,sessionName,sourceName,destinationName):
        self.jobId = sessionName
        self.source = sourceName
        self.destination = destinationName
        self.newSession = Session()

    def __del__(self):
        self.newSession.close()
        

def insertMapping(dbsession: DBsession,objectName: str, mapping: dict):
    #check if the job exists insert new job if not there in the database
    job = dbsession.newSession.query(jobDetail).filter_by(job_id=dbsession.jobId).first()
    if(job == None):
        newJob = jobDetail(dbsession.jobId,dbsession.source,dbsession.destination)
        dbsession.newSession.add(newJob)
        dbsession.newSession.commit()
        log.info("New Job created in database. %s"%dbsession.jobId)
    values = list(dict(job_id = dbsession.jobId,object_name=objectName.lower(), source_id = key, destination_id = value ) for key , value in mapping.items())
    dbsession.newSession.bulk_insert_mappings(idMapping,values)
    dbsession.newSession.commit()
    log.info("Mappings inserted to database with jobId: %s ; %s ; %d mappings"%(dbsession.jobId,objectName, len(mapping.keys())))
    
def retrieveMapping(dbsession: DBsession, objectList: list) -> dict:
    log.info('Retrieving mappings for the objects: %s'%(','.join(objectList)))
    result = dbsession.newSession.query(idMapping).filter(idMapping.object_name.in_(objectList),idMapping.job_id == dbsession.jobId)
    returnResult  = dict()
    for item in result:
        returnResult[str(item.source_id)] = str(item.destination_id)
    return returnResult

