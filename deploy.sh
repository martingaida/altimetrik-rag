#!/bin/bash

# Check if AWS CLI is configured with valid credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "AWS credentials are not configured or are invalid. Please run 'aws configure' and try again."
        exit 1
    fi
}

# Function to check and install dependencies
check_dependencies() {
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "AWS CLI is not installed. Installing..."
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    fi

    # Check for SAM CLI
    if ! command -v sam &> /dev/null; then
        echo "SAM CLI is not installed. Installing..."
        pip install aws-sam-cli
    fi

    # Check for Python
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3 and try again."
        exit 1
    fi
}

deploy_data_processing() {
    echo "Deploying data processing components..."
    cd api/data_processing

    # Check for .env file and source it if it exists
    if [ -f .env ]; then
        echo "Found .env file. Loading environment variables..."
        export $(grep -v '^#' .env | xargs)
    fi

    # Build the SAM application
    sam build
    if [ $? -ne 0 ]; then
        echo "Error: SAM build failed"
        exit 1
    fi

    # Deploy with parameter overrides
    sam deploy --stack-name rag-data-processing \
               --capabilities CAPABILITY_IAM \
               --region us-east-1 \
               --no-confirm-changeset \
               --resolve-s3 \
               --parameter-overrides \
                   ParameterKey=DataUploadBucket,ParameterValue=${DATA_UPLOAD_BUCKET:-rag-data-uploads-$(date +%s)} \
                   ParameterKey=DataWorkflowArn,ParameterValue=${DATA_WORKFLOW_ARN}

    if [ $? -ne 0 ]; then
        echo "Error: SAM deploy failed"
        exit 1
    fi

    cd ../..
    
    # Store outputs in environment file
    echo "Storing deployment outputs..."
    HANDLER_FUNCTION_ARN=$(aws cloudformation describe-stacks --stack-name rag-data-processing --query "Stacks[0].Outputs[?OutputKey=='DataProcessingHandlerFunctionArn'].OutputValue" --output text)
    DATA_UPLOAD_BUCKET=$(aws cloudformation describe-stacks --stack-name rag-data-processing --query "Stacks[0].Parameters[?ParameterKey=='DataUploadBucket'].ParameterValue" --output text)
    
    echo "DATA_PROCESSING_HANDLER_ARN=$HANDLER_FUNCTION_ARN" > .env
    echo "DATA_UPLOAD_BUCKET=$DATA_UPLOAD_BUCKET" >> .env
    
    echo "Data Processing deployment completed successfully"
    echo "Handler Function ARN: $HANDLER_FUNCTION_ARN"
    echo "Data Upload Bucket: $DATA_UPLOAD_BUCKET"
}

# Fail-safe
set -eo pipefail

# Check and install dependencies
check_dependencies
check_aws_credentials

# Deploy based on the provided argument
if [ "$1" == "data-processing" ]; then
    deploy_data_processing
elif [ "$1" == "all" ]; then
    deploy_data_processing
else
    echo "Invalid command. Please use one of the following arguments:"
    echo "  data-processing - Deploy the data processing components"
    echo "  all            - Deploy everything"
fi