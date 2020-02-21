class Message:
    data = []

    def __init__(self, message_id, from_, to, date, date_ts, subject='', labels=None, body=None):
        if labels is None:
            labels = {}

        self.data = {
            'message_id': message_id,
            'from': from_,
            'to': to,
            'subject': subject,
            'date': date,
            'date_ts': date_ts,
            'labels': labels,
        }

        if body is not None:
            self.data['body'] = body
            self.data['body_size'] = len(body)

    def get(self):
        return self.data

    def set_extra(self, key: str, data):
        self.data['extra'][key] = data
