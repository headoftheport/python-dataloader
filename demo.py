from dataloader import dataloader, DBsession

objectList = ['obj A', 'obj B']
#export
sf = dataloader(instance = 'test', 
                userName = '<source-username>', 
                password = '<source-password>',
                securityToken = '<source-token>'
            )
sf.exportRelationship(objectList)
for item in objectList:
    sf.exportData(item)

#import
db = DBsession('<unique-ID>','<source>','<destination>')
sf = dataloader(
                instance = 'test', 
                userName = '<destination-username>', 
                password = '<destination-password>',
                securityToken = '<destination-token>'
            )
for item in objectList:
    sf.insertData(item, db)
for item in objectList:
    sf.updateData(item, db)