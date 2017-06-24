__all__ = ["storage_save", "storage_get"]

data = {}

def storage_save(key,value):
    global data
    data[key] = value

def storage_get(key,default=None):
    global data
    result = data.get(key,default)
    if result is None:
        raise Exception("key not found")
    return result