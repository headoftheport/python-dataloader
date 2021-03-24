Project python_dataloader {
  database_type: 'SQLite'
  Note: 'this database is used to store the old and new id mapping from the salesforce'
}

Table job_details {
  job_id char[5] [primary key]
  source_sandbox varchar [not null]
  destination_sandbox varchar [not null]
  job_date datetime 

}
 
Table id_mapping {
  job_id char[5] [ref: > job_details.job_id]
  object_name varchar [not null]
  source_id varchar[18] [not null]
  destination_id varchar[18] [not null]
  
}