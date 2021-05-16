import hashlib
from enum import Enum, unique


@unique
class Outcome(Enum):
    Win = 1
    Loss = 2
    Draw = 3


def calculate_git_hash(user_id: int, commit_hash: str, url: str) -> str:
    m = hashlib.sha256()
    m.update(str(user_id).encode('utf-8'))
    m.update(commit_hash.encode('utf-8'))
    # m.update(url.encode('utf-8'))
    return str(m.hexdigest())
