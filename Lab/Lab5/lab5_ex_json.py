"""
This code shows how to encode and decode JSON objects in Python.
"""
import json

my_dict = {
    'name': 'Tony',
    'surname': 'Stark',
    'age': 40,
    'hobbies': ['Sport', 'Technology'],
}

# Encode a dict to JSON string
my_string = json.dumps(my_dict)
print('The type of "my_string" is:', type(my_string))
print('The content is:')
print(my_string)

print()

# Encode dict to JSON file
with open('example.json', 'w') as fp:
    json.dump(my_dict, fp)

# Decode JSON string to dict
from_string_to_dict = json.loads(my_string)
print('The type of "from_string_to_dict" is:', type(from_string_to_dict))
print('The content is:')
print(from_string_to_dict)
print()

# Decode JSON file to dict
with open('example.json', 'r') as fp:
    from_file_to_dict = json.load(fp)

print('The type of "from_file_to_dict" is:', type(from_file_to_dict))
print('The content is:')
print(from_file_to_dict)
print()
