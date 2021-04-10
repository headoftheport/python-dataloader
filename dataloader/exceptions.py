class ProcessFailureError(Exception):

    def __init__(self, action, objectName, message = 'Process Failed!'):
        self.action = action
        self.objectName = objectName
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.action} -> {self.objectName}: {self.message}'


class RecordInsertError(ProcessFailureError):

    def __init__(self, objectName, idMapping, failedRecord, successList, *args,**kwargs):
        self.idMapping = idMapping
        self.failedRecord = failedRecord
        self.objectName = objectName
        self.successList = successList
        super().__init__('Insert', objectName, *args, **kwargs)

    def __str__(self):
        return  f'Insert failed for a record -> {self.objectName}: Records Inserted: {len(self.successList)}'


