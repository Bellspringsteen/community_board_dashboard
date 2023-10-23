#!/bin/bash

# Replace with your AWS Lambda function name and file paths
FUNCTION_NAME="CBFunction"
ZIP_FILE_PATH="cbpackage.zip"
HANDLER="lambda_app.lambda_handler"

# Package the Lambda function code
(cd ./app && zip -r $ZIP_FILE_PATH ./*)


# Deploy or update the Lambda function
# aws lambda create-function \
#     --function-name $FUNCTION_NAME \
#     --runtime python3.8 \
#     --role arn:aws:iam::212905216651:role/cb-dashboard-data-store-lambda-role \
#     --handler $HANDLER \
#     --zip-file fileb://$ZIP_FILE_PATH

# Optionally, update the Lambda function code (if you have already created it)
aws lambda update-function-code \
   --function-name $FUNCTION_NAME \
   --zip-file fileb://app/$ZIP_FILE_PATH

# Clean up the temporary package
rm ./app/$ZIP_FILE_PATH
