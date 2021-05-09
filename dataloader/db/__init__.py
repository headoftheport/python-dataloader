print(__package__, __name__,__file__)

from datetime import date
import os

from sqlalchemy import create_engine, Column, String, Integer, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from dataloader.helpers.directoryCreator import mkdir

mkdir(os.getcwd() + '/data/import')

Base = declarative_base()
Session = sessionmaker()

class database:

    def __init__(self, dbName):
        global Base
        global Session
        engine = create_engine(f'sqlite:///sqlite/db/{dbName}.db',echo = False)
        Session.configure(bind=engine)
        Base.metadata.create_all(engine)
        
class jobDetail(Base):
    __tablename__ = 'job_detail'

    job_id = Column(String, primary_key=True)
    source_sandbox = Column(String)
    destination_sandbox = Column(String)
    job_date = Column(Date)
    mapping = relationship('idMapping')

    def __init__(self, job_id,source,destination):
        self.job_id = job_id
        self.source_sandbox = source
        self.destination_sandbox = destination
        self.job_date = date.today()


class idMapping(Base):
    __tablename__ = 'id_mapping'

    job_id = Column(String, ForeignKey ('job_detail.job_id'), primary_key=True)
    object_name = Column(String)
    source_id = Column(String(18), primary_key=True)
    destination_id = Column(String(18))
    mapping = relationship("jobDetail", backref=backref('id_mapping'))

    def __init__(self, jobId, objectName, sourceId, destId):
        self.job_id = jobId
        self.object_name = objectName
        self.source_id = sourceId
        self.destination_id = destId
        