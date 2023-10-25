# Run it all local

change the persister to Global Variable
export FLASK_APP=flask_app.py
cd /app
flask run --reload
ngrok http 500
Take the ngrok and put it in the TWillio Phone Number page

export API_KEY=auth-key-value

# run it custom


# run it hosted
change the persister to PersisterS3



# AWS Setup

API Gateway?
Lambda?
What did i do for sleepy baby?


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
aws lambda add-permission --function-name CBFunction --statement-id apigateway-invoke-permissions --action lambda:InvokeFunction --principal apigateway.amazonaws.com --source-arn "arn:aws:execute-api:us-east-1:212905216651:jrkve800qh/default/GET/test"


# AUTH

* For twilio, a parameter is added to the url string in twilio config
* For lambda and local flask, environment variable is being checked vs x-api-key