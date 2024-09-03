import cherrypy
import json
import redis
import uuid
from redis.commands.json.path import Path


REDIS_HOST = 'redis-11938.c293.eu-central-1-1.ec2.cloud.redislabs.com'
REDIS_PORT = 11938
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'pZIaK9HYlVQnpVCLoyqjcAUJSYsyLfIi'

# Connect to Redis server
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

# endpoint /status
class Status(object):
    exposed = True

    def GET(self, *path, **query):
        response_dict = {
            'status': 'online'
        }
        response = json.dumps(response_dict)

        return response

# endpoint /todos
class TodoList(object):
    exposed = True

    def GET(self, *path, **query):
        # print(query)
        keys = redis_client.keys('todo:*')
        print(keys)
        items = []

        completed = query.get('completed', None)
        if completed is not None:
            completed = bool(completed)

        message = query.get('message', None)

        for key in keys:
            key = key.decode()
            item = redis_client.json().get(key)
            uid = key.removeprefix('todo:')
            item['id'] = uid

            if completed is not None and message is not None:
                if completed == item['completed'] and message in item['message']:
                    items.append(item)
            elif completed is not None:
                if completed == item['completed']:
                    items.append(item)
            elif message is not None:
                if message in item['message']:
                    items.append(item)
            else:
                items.append(item)

        response = json.dumps(items)

        return response

    def POST(self, *path, **query):
        uid = uuid.uuid4()
        body = cherrypy.request.body.read()
        # print(body)
        body_dict = json.loads(body.decode())
        # print(body_dict)

        todo_data = {
            'message': body_dict['message'],
            'completed': False,
        }
        redis_client.json().set(f'todo:{uid}', Path.root_path(), todo_data)
        
        return

# endpoint /todo/{id}
class TodoDetail(object):
    exposed = True

    def GET(self, *path, **query):
        if len(path) != 1:
            raise cherrypy.HTTPError(400, 'Bad Request: missing id')
        uid = path[0]

        item = redis_client.json().get(f'todo:{path[0]}')

        if item is None:
             raise cherrypy.HTTPError(404, '404 Not Found')
        
        item['id'] = uid

        response = json.dumps(item)
        
        return response

    def PUT(self, *path, **query):
        if len(path) != 1:
            raise cherrypy.HTTPError(400, 'Bad Request: missing id')
        uid = path[0]

        item = redis_client.json().get(f'todo:{path[0]}')

        if item is None:
             raise cherrypy.HTTPError(404, '404 Not Found')
        
        body = cherrypy.request.body.read()
        body_dict = json.loads(body.decode())

        redis_client.json().set(f'todo:{uid}', Path.root_path(), body_dict)
        
        return

    def DELETE(self, *path, **query):
        if len(path) != 1:
            raise cherrypy.HTTPError(400, 'Bad Request: missing id')
        uid = path[0]
        
        found = redis_client.delete(f'todo:{uid}')

        if found == 0:
            raise cherrypy.HTTPError(404, '404 Not Found')

        return

if __name__ == '__main__':
    conf = {'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}}
    cherrypy.tree.mount(Status(), '/online', conf)
    cherrypy.tree.mount(TodoList(), '/todos', conf)
    cherrypy.tree.mount(TodoDetail(), '/todo', conf)
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()