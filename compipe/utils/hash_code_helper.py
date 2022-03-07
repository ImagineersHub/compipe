import base64
import hashlib
import json

from cryptography.fernet import Fernet


def encrypt_str(value):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    cipher_text = cipher_suite.encrypt(bytes(value, 'utf-8'))
    return {'FERNET_KEY': key.decode("utf-8"),
            'CIPHER_TEXT': cipher_text.decode("utf-8")}


def decrypt_str(key, cipher_text):
    if not key or not cipher_text:
        return None
    else:
        cipher_suite = Fernet(bytes(key, 'utf-8'))
        return json.loads(cipher_suite.decrypt(bytes(cipher_text, 'utf-8')))


def md5_string_to_hash(*args, **kwargs):
    """Simply convert string to md5 hash value.

    Args:
        args (list): Represent the string list for converting
        kwargs (Dict): key: 'encode' represent encoding standard.
                        Default value: utf-8
    Example:
        >>>compe md5hash -a "do less shit, do more awesome shit" encode=utf-8
    """
    encoding = kwargs['encode'] if hasattr(kwargs, 'encode') else 'utf-8'
    return [hashlib.md5(item.encode(encoding)).hexdigest() for item in args]


def hexdigest_str(*args):

    return [hashlib.sha224(bytes(item, 'utf-8')).hexdigest() for item in args]


def convert_string_to_base64(*args):
    """Simply convert string to base64.

    Example:
        compe str2b64 -a "hello world"
    """

    string = base64.b64encode(bytes(args[0], 'utf-8'))
    return string.decode("utf-8")
