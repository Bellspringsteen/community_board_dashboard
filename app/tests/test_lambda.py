
import json
import unittest
from unittest.mock import MagicMock, patch

from lambda_app import lambda_handler

class TestLambdaFunction(unittest.TestCase):
    def test_start_voting(self):
        # Define a sample event for /startvoting
        event = {
            'resource': '/startvoting',
            'httpMethod': 'POST',
            'title': 'Sample Voting Title',
            'headers': {
                'x-api-key': 'your-auth-key'  # Replace with your valid API key
            }
        }

        # Call the Lambda function
        response = lambda_handler(event, None)

        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '"OK"')

    def test_invalid_api_key(self):
        # Define an event with an invalid API key
        event = {
            'resource': '/startvoting',
            'httpMethod': 'POST',
            'title': 'Sample Voting Title',
            'headers': {
                'x-api-key': 'invalid-key'
            }
        }

        # Call the Lambda function
        response = lambda_handler(event, None)

        # Verify the response
        self.assertEqual(response['statusCode'], 401)
        self.assertEqual(response['body'], '"Unauthorized"')

if __name__ == '__main__':
    unittest.main()
