from .helpers import engine, Session , jobDetail, idMapping

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
    values = list(dict(job_id = dbsession.jobId,object_name=objectName, source_id = key, destination_id = value ) for key , value in mapping.items())
    dbsession.newSession.bulk_insert_mappings(idMapping,values)
    dbsession.newSession.commit()

def retrieveMapping(dbsession: DBsession, objectList: list) -> dict:
    result = dbsession.newSession.query(idMapping).filter(idMapping.object_name.in_(objectList),idMapping.job_id == dbsession.jobId)
    returnResult  = dict()
    for item in result:
        returnResult[str(item.source_id)] = str(item.destination_id)
    return returnResult

