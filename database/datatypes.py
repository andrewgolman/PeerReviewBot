from collections import namedtuple


User = namedtuple('User', ['login'])


Task = namedtuple('Task', ['name'])


UserTask = namedtuple(
    'UserTask',
    ['user', 'task', 'url', 'status', 'timestamp']
)


Review = namedtuple(
    'Review',
    ['reviewer', 'reviewee', 'task', 'status']
)

