from collections import defaultdict

_session_store = defaultdict(dict)

def set_local_flag(username, is_local: bool):
    _session_store[username]['is_local'] = is_local

def is_local_client(username) -> bool:
    return _session_store[username].get('is_local', False)
