"""Represent the command parameter strings."""
ARG_COMMAND = 'command'
ARG_ARGUMENT = 'argument'
ARG_COUNT = 'count'
ARG_CHANNEL = 'channel'
ARG_CLIENT = 'client'
ARG_GUID = 'guid'
ARG_ID = 'id'
ARG_CHANGELIST = 'cl'
ARG_DEV_CHANNEL = 'dev_channel'
ARG_DEV = 'dev'
ARG_PROD = 'prod'
ARG_QUEUE_WORKER_NUMBER = 'worker_number'
ARG_CALLBACK = 'callback'
ARG_PAYLOAD = 'payload'
ARG_MESSAGE = 'message'
ARG_USER = 'user'
ARG_ERROR = 'error'
ARG_PATH = 'path'
ARG_ISO = 'iso'
ARG_DESCRIPTION = 'description'
ARG_SOURCE = 'source'
ARG_TARGET = 'target'
ARG_RESPONSE = 'response'
ARG_COMMAND_ID = 'command_id'
ARG_MESSAGE_TYPE = 'msg_status'
ARG_MODE = 'mode'
ARG_FOLDER = 'folder'
ARG_VERBOSE = 'verbose'
ARG_FORCE = 'force'
ARG_REBUILD = 'rebuild'
ARG_SHELVE = 'shelve'
ARG_CHECKOUT = 'co'
ARG_LOOP = 'loop'
ARG_SAVE = 'save'
ARG_SIMILARITY = 'sim'
ARG_UPLOAD = 'upload'
ARG_METADATA = 'metadata'
ARG_CONFIG = 'config'
ARG_RESET = 'reset'
ARG_NAME = 'name'
ARG_DOC = 'doc'
ARG_INDEX = 'index'
ARG_CQL = 'cql'
ARG_HEADERS = 'headers'
ARG_FILES = 'files'
ARG_FILE = 'file'
ARG_TXT = 'txt'
ARG_OUTPUT = 'output'
ARG_CDP = 'cdp'  # create document placeholder : doc_app
ARG_CTP = 'ctp'
ARG_VERSION = 'version'
ARG_SPACE = 'space'
ARG_PREBUILD = 'prebuild'
ARG_OUT_OF_SERVICE = 'oos'  # out of service
ARG_CID = 'cid'  # represent the flag checking CID build
ARG_DB_ALIAS = 'db_alias'
ARG_COMMIT = 'commit'
ARG_DUPLICATE = 'dup'  # duplicate (flag)
ARG_RENAME = 'rename'
ARG_COPY = 'copy'
ARG_ACTION = 'action'
ARG_COLOR = 'color'
ARG_OPTIMIZE = 'opt'
ARG_SYNC = 'sync'
ARG_DATA = 'data'
ARG_DIR = 'dir'
ARG_PARENT = 'parent'
ARG_POPULATE = 'populate'
ARG_PROJECT = 'project'
ARG_CLASS = 'cls'
ARG_OBJ = 'object'
ARG_CACHE = 'cache'
ARG_RESOURCE = 'resource'
ARG_DEBUG = 'debug'
ARG_QUEUE_WORKER_NUM = 'queue_worker_num'
ARG_SUBPROCESS_NUM = 'subprocess_num'
ARG_CLASSIFICATION = 'classification'
ARG_TEAM = 'team'
ARG_CONSOLE = 'console'
ARG_FILTER = 'filter'
ARG_PUSH = 'push'
ARG_ORIGINAL = 'original'
ARG_ORIGIN = 'origin'
ARG_DIRECTION = 'direction'
ARG_MAIN = 'main'
ARG_TRANSFORM = 'transform'
ARG_AXES = 'axes'
ARG_PATTERN = 'pattern'
ARG_REVERSE = 'reverse'
ARG_MESH = 'mesh'
ARG_OFFSET = 'offset'
ARG_FACTOR = 'factor'
ARG_SCALE = 'scale'
ARG_DENOISING = 'denoising'
ARG_MODEL = 'model'
ARG_DNN_MODELS = 'dnn_models'
ARG_REFORMAT = 'reformat'
ARG_SCENE = 'scene'
ARG_MATERIAL = 'material'
ARG_SIZE = 'size'
ARG_TEXTURE = 'texture'
ARG_TYPE = 'type'
ARG_FACES = 'faces'
ARG_SMOOTH_LEVEL = 'smooth_level'
ARG_MAX_FACES = 'max_faces'
ARG_DOMINANT = 'dominant'
ARG_SHOW = "show"
ARG_PREVIEW = "preview"
ARG_OPACITY = "opacity"
ARG_PADDING = 'padding'
ARG_CROP = 'crop'
ARG_DECIMATE = 'decimate'
ARG_RESAMPLE = 'resample'
ARG_LIMITS = 'limits'
ARG_BASE = 'base'
ARG_APP_INVOKE = 'app_invoke'

# space names
ARG_SPACE_HYPER = 'hyper'
ARG_SPACE_MARS = 'mars'


# values
ARG_FRAMES = 'frames'
ARG_FRAME = 'frame'

# Mars Project
ARG_LOCAL_DRIVE = 'local_drive'
ARG_SEGMENT = 'segment'
ARG_THRESHOLD = 'threshold'
ARG_TAGS = 'tags'
ARG_SPACING = 'spacing'
ARG_MODALITY = 'modality'
ARG_WORLDSPACE_OFFSET = 'worldspace_offset'

ARG_WINDOW_WIDTH = 'ww'
ARG_WINDOW_LEVEL = 'wl'

# server config
ARG_EXECUTABLE_TOOLS = 'executable_tools'
ARG_PYTHON_MODULES = 'python_modules'

# Channel Texture Maps
ARG_AMBIENTOCCLUSION_MAP = 'aomap'
ARG_EMISSION_MAP = 'emmap'
ARG_CHANNEL_MAP = 'chmap'
ARG_CHANNEL_TRANS_MAP = 'tchmap'
ARG_DIFFUSE_MAP = 'dcmap'


def parse_bool(value):
    return str(value).lower() in ("yes", "true", "t", "1")
