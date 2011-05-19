class ObjectDictWrapper(dict):
    __getattr__ = dict.__getitem__


def recursive_update(original, update):
    if not(isinstance(original, dict) and isinstance(update, dict)):
        return update
    
    for k, v in update.iteritems():
        if k not in original:
            original[k] = v
        else:
            original[k] = recursive_update(original[k], v)

    return original
