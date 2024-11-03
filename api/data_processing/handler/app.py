import json
import os
import boto3

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    try:
        # Get the S3 bucket and key from the event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        # Prepare input for the state machines
        state_machine_input = {
            "bucket": bucket,
            "key": key
        }
        
        # Start the data processing state machine execution
        data_processing_response = stepfunctions.start_execution(
            stateMachineArn=os.environ['DATA_WORKFLOW_ARN'],
            input=json.dumps(state_machine_input)
        )
        
        # Wait for data processing to complete
        waiter = stepfunctions.get_waiter('execution_completed')
        waiter.wait(
            executionArn=data_processing_response['executionArn'],
            WaiterConfig={'Delay': 5, 'MaxAttempts': 60}
        )
        
        # Get the output from data processing execution
        execution_history = stepfunctions.get_execution_history(
            executionArn=data_processing_response['executionArn'],
            reverseOrder=True,
            maxResults=1
        )
        
        data_processing_output = json.loads(execution_history['events'][0]['executionSucceededEventDetails']['output'])
        
        # Start the ingestion state machine with the processed data
        ingestion_response = stepfunctions.start_execution(
            stateMachineArn=os.environ['INGESTION_WORKFLOW_ARN'],
            input=json.dumps(data_processing_output)
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully started Data Collection and Ingestion state machine executions',
                'dataProcessingExecutionArn': data_processing_response['executionArn'],
                'ingestionExecutionArn': ingestion_response['executionArn']
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }