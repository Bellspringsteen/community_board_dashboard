# Run it all local

change the persister to Global Variable
export FLASK_APP=flask_app.py
flask run --reload
ngrok http 500
Take the ngrok and put it in the TWillio Phone Number page


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

