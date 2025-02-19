TODO
* add ability to edit members phone numbers/names
* add the idea of accounts for different CBs (how are you going to do authentication?) simple password. Url? Have them send in twilio account information
* prepend all logs with teh cb account. 
* for each account, all adding twilio account for each cb
* better authentication of incoming twilio text? 
* put behind a url labsbell.com/cbvoting/ 


# Run it all local

change the persister to Global Variable and the Logger
export FLASK_APP=flask_app.py
cd /app
flask run --reload
ngrok http 500
Take the ngrok and put it in the TWillio Phone Number page

export API_KEY=auth-key-value


# deploy hosted
sh deploy_lambda.sh 


# AWS Setup

API Gateway - setup endpoints
Lambda - create with the attached script, comment out the create


# create the twilio_layer
mkdir python
cd python
vim requirements.txt add urllib3<2 and twilio
pip3 install -r requirements.txt -t ./
zip -r python.zip .
In the AWS Lambda console, navigate to the "Layers" section. Click the "Create layer" button, and then:

Enter a name for your layer.
Provide a description (optional).
Upload the python.zip file.
Choose a compatible runtime (e.g., Python 3.8 or the runtime you intend to use).
Click "Create" to create the Lambda layer.

# Lambda permissions
aws lambda add-permission --function-name CBFunction --statement-id apigateway-invoke-permissions --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-1:accound:lambda/default/GET/test"

# AUTH
* For twilio, a parameter is added to the url string in twilio config
* For lambda and local flask, environment variable is being checked vs x-api-key

# python scrip to upload members.csv to s3 as members.json
python3 uploadmembers.py