import json
from datetime import datetime
from enum import Enum, unique
from typing import Union, List, Tuple

import requests
import urllib.parse


ROOT_URL = "http://database:8080"


class InvalidRequestError(RuntimeError):
    def __init__(self, *args):
        super(InvalidRequestError, self).__init__(*args)


@unique
class Outcome(Enum):
    Win = 1
    Loss = 2
    Draw = 3


class User:
    def __init__(self, user_id: str, display_name: str):
        self.user_id = str(user_id)
        self.display_name = str(display_name)

    @staticmethod
    def create(username: str) -> 'User':
        return _get("add_user", dict(username=username))

    @staticmethod
    def get(user_id: str) -> 'User':
        return _get("get_user", dict(user_id=user_id))

    def is_bot(self) -> bool:
        return _get("is_user_bot", dict(user_id=self.user_id))

    def is_admin(self) -> bool:
        return _get("is_user_admin", dict(user_id=self.user_id))

    @staticmethod
    def make_or_get_google_user(google_id: str, name: str) -> 'User':
        return _get("make_or_get_google_user", dict(google_id=google_id, name=name))

    def get_latest_submission(self) -> 'Submission':
        return _get("get_latest_submission", dict(user_id=self.user_id))

    @staticmethod
    def from_dict(d) -> "User":
        return User(d['user_id'], d['display_name'])

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'user',
                'user_id': self.user_id,
                'display_name': self.display_name}


class Submission:
    def __init__(self, submission_id: str, user_id: str, submission_date: datetime, url: str, active: bool,
                 files_hash: str):
        self.submission_id = str(submission_id)
        self.user_id = str(user_id)
        self.submission_date = submission_date
        self.url = str(url)
        self.active = bool(active)
        self.files_hash = str(files_hash)

    @staticmethod
    def create(user: Union[User, str], url: str) -> 'Submission':
        if user is User:
            user = user.user_id

        return _get("add_submission", dict(user_id=user, url=url))

    def get_health(self) -> float:
        return _get("get_health", dict(submission_id=self.submission_id))

    @staticmethod
    def from_dict(d) -> "Submission":
        submission_date = datetime.fromisoformat(d['submission_date'])
        return Submission(d['submission_id'], d['user_id'], submission_date, d['url'], d['active'], d['files_hash'])

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'submission',
                'submission_id': self.submission_id,
                'user_id': self.user_id,
                'submission_date': self.submission_date.isoformat(),
                'url': self.url,
                'active': self.active,
                'files_hash': self.files_hash}


class Match:
    def __init__(self, match_id: str, match_date: datetime, recording: str):
        self.match_id = str(match_id)
        self.match_date = match_date
        self.recording = recording

    @staticmethod
    def create_win_loss(winner: Union[Submission, str], loser: Union[Submission, str], recording: str) -> 'Match':
        if winner is Submission:
            winner = winner.submission_id
        if loser is Submission:
            loser = loser.submission_id

        return _get("record_win_loss", dict(submission1=winner, submission2=loser, recording=recording))

    @staticmethod
    def create_draw(submission1: Union[Submission, str], submission2: Union[Submission, str],
                    recording: str) -> 'Match':
        if submission1 is Submission:
            submission1 = submission1.submission_id
        if submission2 is Submission:
            submission2 = submission2.submission_id

        return _get("record_win_loss", dict(submission1=submission1, submission2=submission2, recording=recording))

    @staticmethod
    def create_crash(submission1: Union[Submission, str], submission2: Union[Submission, str],
                     recording: str) -> 'Match':
        if submission1 is Submission:
            submission1 = submission1.submission_id
        if submission2 is Submission:
            submission2 = submission2.submission_id

        return _get("record_crash", dict(submission1=submission1, submission2=submission2, recording=recording))

    @staticmethod
    def from_dict(d) -> "Match":
        match_date = datetime.fromisoformat(d['match_date'])
        return Match(d['match_id'], match_date, d['recording'])

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'match',
                'match_id': self.match_id,
                'match_date': self.match_date.isoformat(),
                'recording': self.recording}


class Result:
    def __init__(self, match_id: str, submission_id: str, outcome: Outcome, milli_points_delta: int, healthy: bool,
                 player_id: str):
        """
        :param match_id: The id of the match associated with this result
        :param submission_id: The id of the submission associated with this result
        :param outcome: The outcome of the match for the given submission
        :param milli_points_delta: The change in points for the given submission
        :param healthy: Whether the game was played to completion, false if the code crashed or some other fault
        :param player_id: eg. 'white', 'black', 'team_1' etc.
        """
        self.match_id = str(match_id)
        self.submission_id = str(submission_id)
        self.outcome = outcome if isinstance(outcome, Outcome) else Outcome(outcome)
        self.milli_points_delta = int(milli_points_delta)
        self.healthy = bool(healthy)
        self.player_id = str(player_id)

    @staticmethod
    def from_dict(d) -> "Result":
        outcome = Outcome(d['outcome'])
        return Result(d['match_id'], d['submission_id'], outcome, d['milli_points_delta'], d['healthy'], d['player_id'])

    def to_dict(self) -> dict:
        return {'_cuwais_type': 'result',
                'match_id': self.match_id,
                'submission_id': self.submission_id,
                'outcome': self.outcome.value,
                'milli_points_delta': self.milli_points_delta,
                'healthy': self.healthy,
                'player_id': self.player_id}


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


def _get(dest, data):
    url = urllib.parse.urljoin(ROOT_URL, dest)
    response = requests.get(url, data)

    if response.status_code >= 300:
        raise InvalidRequestError(response)
    
    return decode(response.content)


def get_scoreboard() -> List[Tuple[Submission, float]]:
    return [(a, b) for [a, b] in _get('get_scoreboard', dict())]


def get_random_latest_submissions(count=2) -> List[Tuple[Submission, float]]:
    return _get('get_random_latest_submissions', dict(count=count))
