import json
from datetime import datetime


class User:
    def __init__(self, user_id: str, username: str, display_name: str):
        self.user_id = user_id
        self.username = username
        self.display_name = display_name

    @staticmethod
    def from_dict(d) -> "User":
        return User(d['user_id'], d['username'], d['display_name'])

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'user',
                'user_id': self.user_id,
                'username': self.username,
                'display_name': self.display_name}


class Submission:
    def __init__(self, submission_id: str, user_id: str, submission_date: datetime, url: str):
        self.submission_id = submission_id
        self.user_id = user_id
        self.submission_date = submission_date
        self.url = url

    @staticmethod
    def from_dict(d) -> "Submission":
        submission_date = datetime.fromisoformat(d['submission_date'])
        return Submission(d['submission_id'], d['user_id'], submission_date, d['url'])

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'submission',
                'submission_id': self.submission_id,
                'user_id': self.user_id,
                'submission_date': self.submission_date.isoformat(),
                'url': self.url}


class Match:
    def __init__(self, match_id: str, match_date: datetime):
        self.match_id = match_id
        self.match_date = match_date

    @staticmethod
    def from_dict(d) -> "Match":
        match_date = datetime.fromisoformat(d['match_date'])
        return Match(d['match_id'], match_date)

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'match',
                'match_id': self.match_id,
                'match_date': self.match_date.isoformat()}


class Result:
    def __init__(self, match_id: str, submission_id: str, outcome: str, nano_points_delta: int):
        self.match_id = match_id
        self.submission_id = submission_id
        self.outcome = outcome
        self.nano_points_delta = nano_points_delta

    @staticmethod
    def from_dict(d) -> "Result":
        return Result(d['match_id'], d['submission_id'], d['outcome'], d['nano_points_delta'])

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'result',
                'match_id': self.match_id,
                'submission_id': self.submission_id,
                'outcome': self.outcome,
                'nano_points_delta': self.nano_points_delta}


class Encoder(json.JSONEncoder):
    _encoders = {User,
                 Submission,
                 Match,
                 Result}

    def default(self, obj):
        for cuwais_type in Encoder._encoders:
            if isinstance(obj, cuwais_type):
                return obj.to_dict()
        return super(Encoder, self).default(obj)


class Decoder(json.JSONDecoder):
    _decoders = {'user': User.from_dict,
                 'submission': Submission.from_dict,
                 'match': Match.from_dict,
                 'result': Result.from_dict}

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_cuwais_type' not in obj:
            return obj
        cuwais_type = obj['_cuwais_type']
        if cuwais_type in Decoder._decoders:
            return Decoder._decoders[cuwais_type](obj)
        return obj


def encode(data):
    return json.dumps(data, cls=Encoder)


def decode(data):
    return json.loads(data, cls=Decoder)

