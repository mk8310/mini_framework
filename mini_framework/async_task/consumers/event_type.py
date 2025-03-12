from enum import Enum


class EventType(str, Enum):
    event = 'event'
    progress = 'progress'
    failure = 'failure'
    success = 'success'
    cancel = 'cancel'
    timeout = 'timeout'
