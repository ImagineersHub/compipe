from enum import Enum


class GMimeTypes(Enum):
    FOLDER = 'application/vnd.google-apps.folder'
    JSON = 'application/json'
    PNG = 'image/png'
    WEBP = 'image/webp'
    TXT = 'text/plain'
    # blow are lists of slack file type names
    # https://api.slack.com/types/file#file_types
    SLACK_TXT = 'text'
