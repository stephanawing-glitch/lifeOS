from . import db


def build_today_lists():
    frogs = db.list_open_tasks('frog', 3)
    tadpoles = db.list_open_tasks('tadpole', 8)
    return frogs, tadpoles

