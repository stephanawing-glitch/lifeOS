class InboxItem(object):
    def __init__(self, text, created_at=None, item_id=None):
        self.id = item_id
        self.text = text
        self.created_at = created_at


class Task(object):
    def __init__(
        self,
        title,
        kind=None,
        status=None,
        created_at=None,
        last_seen_at=None,
        days_skipped=0,
        snooze_until=None,
        snooze_count=0,
        leverage=None,
        resistance=None,
        est_minutes=None,
        task_id=None,
    ):
        self.id = task_id
        self.title = title
        self.kind = kind
        self.status = status
        self.created_at = created_at
        self.last_seen_at = last_seen_at
        self.days_skipped = days_skipped
        self.snooze_until = snooze_until
        self.snooze_count = snooze_count
        self.leverage = leverage
        self.resistance = resistance
        self.est_minutes = est_minutes

