import uuid


def take_uuid() -> str:
    return uuid.uuid4().hex