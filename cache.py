import redis
import pickle
from time import time
import os

redis_instance = None

def get_redis_instance():
    global redis_instance
    if redis_instance is None:
        init()
    return redis_instance


def get_timestamp():
    return int(time())

def init():
    global redis_instance
    redis_uri = os.getenv('REDIS_URL', "redis://localhost:6379/0")
    redis_instance = redis.Redis.from_url(redis_uri)


def set(key,obj,expire_at=None):
    redis_instance = get_redis_instance()
    data = {'value' : obj }
    data['expire_at'] = int(expire_at) if expire_at is not None else None
    data = pickle.dumps(data)
    redis_instance.set(key, data)


def get(key):
    redis_instance = get_redis_instance()
    data = redis_instance.get(key)
    if data is not None:
        data = pickle.loads(data)
        if not is_expired(data):
            data = data['value']
        else:
            data = None
    return data


def is_expired(data):
    return data['expire_at'] is not None and data['expire_at'] < get_timestamp()


def remember(key,func,expire_at=None):
    while(True):
        value = get(key)
        if value is not None:
            break
        value = func()
        set(key,value,expire_at)
    return value

def forget(key):
    redis_instance = get_redis_instance()
    redis_instance.delete(key)


def expire_date(seconds=0,minutes=0, hours=0,days=0):
    hours = hours + 24 * days
    minutes = minutes + hours * 60
    seconds = seconds + 60 * minutes
    f = get_timestamp() + seconds
    return f

def flushall():
    redis_instance = get_redis_instance()
    redis_instance.flushall()
