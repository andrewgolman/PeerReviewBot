from collections import namedtuple


User = namedtuple('User', ['login'])


Task = namedtuple('Task', ['name'])


UserTask = namedtuple(
    'UserTask',
    ['id', 'user', 'task', 'url', 'status', 'timestamp']
)


Review = namedtuple('Review', ['reviewer', 'task_id', 'status'])

