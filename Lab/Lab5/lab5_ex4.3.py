"""
This example shows how to test the API with a Python Client. 
"""

import requests


host = 'http://localhost:8080'

# Check the service status
response = requests.get(host + '/status')
if response.status_code == 200:
    # print(response.json())
    status = response.json()['status']
    print(f'The server is {status}.')
else:
    print('The server is offline.')
    exit()

# Add a new to-do item with a POST request.
# First, define the request body.
# You can use a Python object. 
# The "requests" package will handle the conversion to JSON internally.
payload = {'message': 'Buy Coffee'}
# Specify the request body with "json" argument of the post method.
response = requests.post(host + '/todos', json=payload)

# Check the response code. The expected value is 200.
if response.status_code == 200:
    print('To-do item added.')
else:
    exit()

# Print the list of all to-do items
response = requests.get(host + '/todos')

if response.status_code == 200:
    print('All items:')
    for item in response.json():
        # print(response.json())
        uid = item['id']
        message = item['message']
        completed = item['completed']
        print(f'{uid} - {message} (completed: {completed})')
else:
    exit()

# Print the list of the completed to-do items
# First, define the request query parameters.
# You can use a Python object. 
# The "requests" package will handle the conversion to query internally.
payload = {"completed": True}
# Specify the request query parameters with the "params" argument of the get method.
# GET {{host}}/todos?completed=true
response = requests.get(host + '/todos', params=payload)

if response.status_code == 200:
    print()
    print('Completed items:')
    for item in response.json():
        message = item['message']
        print(message)
else:
    exit()

# Update the completed flag
uid = 'f0f4a9b7-bddc-4163-9df6-59272e56ac2c'
payload = {'message': 'Buy Coffee', 'completed': True}
response = requests.put(host + f'/todo/{uid}', json=payload)

if response.status_code == 200:
    print()
    print('Item updated.')
else:
    exit()

# Delete todo item
response = requests.delete(host + f'/todo/{uid}')
if response.status_code == 200:
    print()
    print('Item deleted.')
else:
    exit()