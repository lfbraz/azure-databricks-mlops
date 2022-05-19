#!/bin/sh
JOB_ID=$(databricks jobs create --json-file jobs/create-train-job.json | jq .job_id)
RUN_ID=$(databricks jobs run-now --job-id $JOB_ID | jq '.run_id')

job_status="PENDING"
   while [ $job_status = "RUNNING" ] || [ $job_status = "PENDING" ]
   do
     sleep 2
     job_status=$(databricks runs get --run-id $RUN_ID | jq -r '.state.life_cycle_state')
     echo Status $job_status
   done
