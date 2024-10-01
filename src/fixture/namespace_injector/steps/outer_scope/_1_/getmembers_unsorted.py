def getmembers_unsorted(object, predicates: list):
    # http://192.168.2.1:3000/alewandowski/django-fixtures/issues/4
    return [
        (name, member)
        for (name, member) in object.__dict__.items()
        if any(p(member) for p in predicates)
    ]
