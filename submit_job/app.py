import json
import boto3
import logging
import os

from botocore.exceptions import ClientError

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def get_batch_client():
  return boto3.client('batch')

def get_env_var_value(env_var):
  '''Get the value of an environment variable
  :param env_var: the environment variable
  :returns: the environment variable's value, None if env var is not found
  '''
  value = os.getenv(env_var)
  if not value:
    log.warning(f'cannot get environment variable: {env_var}')

  return value

def lambda_handler(event, context):

    job_name = get_env_var_value('JOB_NAME')
    job_queue = get_env_var_value('JOB_QUEUE')
    job_definition = get_env_var_value('JOB_DEFINITION')

    try:
        client = get_batch_client()
        submitJobResponse = client.submit_job(
            jobName=job_name,
            jobQueue=job_queue,
            jobDefinition=job_definition
        )
        jobId = submitJobResponse['jobId']
        message = f'Submitted job [{job_name} - {jobId}] to the job queue [{job_queue}]'
        log.info(message)
        return {
          "statusCode": 200,
          "body": json.dumps({
            "message": message
          }),
        }
    except ClientError as e:
        message = e.response['Error']['Message']
        log.error(message)
        return {
          "statusCode": 400,
          "body": json.dumps({
            "message": message
          }),
        }

if __name__ == "__main__":
    lambda_handler("event","context")
