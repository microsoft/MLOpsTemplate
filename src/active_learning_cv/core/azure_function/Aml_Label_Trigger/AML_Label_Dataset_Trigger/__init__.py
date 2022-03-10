import logging
import json
import requests
import os

import azure.functions as func

def main(msg: func.QueueMessage):
    logging.info('Python queue trigger function processed a queue item.')

    result = json.dumps({
        'id': msg.id,
        'body': msg.get_body().decode('utf-8'),
        'expiration_time': (msg.expiration_time.isoformat()
                            if msg.expiration_time else None),
        'insertion_time': (msg.insertion_time.isoformat()
                           if msg.insertion_time else None),
        'time_next_visible': (msg.time_next_visible.isoformat()
                              if msg.time_next_visible else None),
        'pop_receipt': msg.pop_receipt,
        'dequeue_count': msg.dequeue_count
    })
    github_workflow_uri =os.getenv("github_workflow_uri")
    token=os.getenv("github_workflow_token")
    # Set the content type
    headers = {'Content-Type': 'application/json'}
    # If authentication is enabled, set the authorization header
    headers['Authorization'] = f'Bearer {token}'
    data = {"event_type": "training"}

    input_data = json.dumps(data)
    # Make the request and display the response
    resp = requests.post(github_workflow_uri, headers=headers, data=input_data)
    logging.info(resp.text)

    logging.info(result)