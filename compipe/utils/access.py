import json
import os

from .hash_code_helper import decrypt_str, encrypt_str
from .io_helper import full_path, json_loader, json_writer
from .logging import logger
from .parameters import ARG_EXECUTABLE_TOOLS
from .singleton import Singleton

CREDENTIAL_PATH = full_path(path=os.path.join(
    'utils', 'credentials', 'keys.json'))

# credential keys ==========================
GITHUB_TOKEN_KEY = 'github-app-token'
GOOGLE_APP_KEY = 'google-app'
SLACK_APP_KEY = 'tars-token'
CONFLUENCE_APP_KEY = 'confluence-app-token'
X_HUB_SIGNATURE = 'x-hub-signature'

# server runtime env keys ==================
FERNET_KEY = 'FERNET_KEY'
CIPHER_TEXT = 'CIPHER_TEXT'
SERVER_CONFIG = 'SERVER_CONFIG'

# local credhash key name
CREDHASH = 'credhash'

CREDENTIAL_KEYS = [SLACK_APP_KEY, GOOGLE_APP_KEY,
                   GITHUB_TOKEN_KEY, X_HUB_SIGNATURE]


class AccessHub(metaclass=Singleton):

    def __init__(self):
        self.keys = {}
        self.server_config = {}

        # if not self.load_credential_from_env_variable():
        #     # try to load credential from local when failing to load env variable from cloud env
        #     logger.debug('Loaded credential from local json dataset')
        #     self.load_access_from_local()

    # def get_server_config(self, config_payload: dict = {}):
    #     # return the resolved server config if the config's been initialized
    #     if self.server_config:
    #         return self.server_config

    #     self.server_config.update(config_payload)

    #     # start parsing the config from system env or local json
    #     # config_txt = self.get_env(SERVER_CONFIG, None)
    #     # if config_txt:
    #     #     self.server_config = json.loads(config_txt)
    #     # else:
    #     #     server_config_path = full_path(path='environment.json')
    #     #     self.server_config = json_loader(path=server_config_path).get(platform or 'win32')

    #     # update executable tool path to system
    #     for key, path in self.server_config.get(ARG_EXECUTABLE_TOOLS, {}).items():
    #         if not path:
    #             logger.debug(f'Executable Tool [{key}] path is invalid!')
    #         else:
    #             logger.debug(f'Executable Tool [{key}] : added path [{path}] to system env.')
    #             os.environ["PATH"] += os.pathsep + path
    #             # sys.path.insert(0, path)

    #     # update system info
    #     self.server_config.update({
    #         'os_platform': platform
    #     })

    #     # check cuda support
    #     # is_cuda_supported = False
    #     # try:
    #     #     import torch
    #     #     is_cuda_supported = True
    #     # except ImportError:
    #     #     pass

    #     # self.server_config.update({
    #     #     'cuda_enabled': is_cuda_supported and torch.cuda.is_available()
    #     # })

    #     return self.server_config

    # def load_credential_from_env_variable(self):
    #     # get fernet key
    #     fernet_key = self.get_env(FERNET_KEY)
    #     cipher_text = self.get_env(CIPHER_TEXT)

    #     self.keys = decrypt_str(fernet_key, cipher_text)

    #     return self.keys != None

    def load_access_from_local(self):
        if os.path.exists(CREDENTIAL_PATH):
            self.keys = json_loader(path=CREDENTIAL_PATH)
        else:
            logger.error(f'Local configs are missing! \n{CREDENTIAL_PATH}')

    def get_credential(self, key):
        return self.keys.get(key)

    def to_hash(self, save_local=False):
        key_str = json.dumps(self.keys)
        data = encrypt_str(key_str)
        if save_local:
            self.save_encrypted_keys(data)
        return data

    def save_encrypted_keys(self, data, output):
        """Kep a copy of the encrypted keys, which is used to update in the 
        cloud environment variables.

        Args:
            data (dict): represent the encrypted hash data.
            e.g.,
            {
                "FERNET_KEY": "7K-oa7bp1xOWz09xj-Tg_llXbID9pYfgOjXDr2F2h94=",
                "CIPHER_TEXT": "gAAAAABgMd3IVTwsr78e0zwKLhoWWluCvQXC2mDYK4Nf...."
            }
        """
        # update the local server config
        data.update({
            SERVER_CONFIG: json.dumps(self.server_config)
        })
        json_writer(output, data)
        logger.debug(f'Exported the latest keys to local:{output}')
