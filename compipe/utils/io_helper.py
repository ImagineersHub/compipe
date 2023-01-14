import json
import math
import os
import re
import shutil
import stat
from os.path import abspath, dirname
from typing import List, Dict

from ..exception.io_error import GErrorFileNotFound
from ..exception.validate_error import GErrorNullObject, GErrorValue

from .logging import logger


def on_rm_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def get_public_dir():
    return full_path('public')


def get_temp_dir():
    return full_path('temp')


def get_log_dir():
    return full_path('logs')


def get_config_dir():
    return full_path('configs')


def get_files(paths: list = [], ext_patterns=[], recursive: bool = True) -> List[str]:
    if not isinstance(paths, list):
        raise GErrorValue('The specified value is not "list" type.')
    file_paths = []
    for path in paths:
        if os.path.exists(path):
            for root, _, files in os.walk(path, topdown=True):
                for item in files:
                    _, ext = os.path.splitext(item)
                    if not ext_patterns or ext.lower()[1:] in ext_patterns:
                        file_paths.append(os.path.normpath(os.path.join(root, item)))
                if not recursive:
                    break
    return file_paths


def get_files_by_regex_basename(paths: list = [], reg_pattern=None, recursive: bool = True) -> List[str]:
    if not isinstance(paths, list):
        raise GErrorValue('The specified value is not "list" type.')
    if reg_pattern == None:
        raise GErrorNullObject('[reg_pattern] parameter does\'t have valid value!')
    if isinstance(reg_pattern,str):
        # force convert to reg pattern if it's str
        reg_pattern = re.compile(reg_pattern,re.IGNORECASE)
    file_paths = []
    for path in paths:
        if os.path.exists(path):
            for root, _, files in os.walk(path, topdown=True):
                for item in files:
                    basename = os.path.basename(item)
                    if reg_pattern.match(basename):
                        file_paths.append(os.path.normpath(os.path.join(root, item)))
                if not recursive:
                    break

    return file_paths


def convert_size(size_bytes) -> str:
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "{} {}".format(s, size_name[i])


def warm_up_path(path):
    # check if file exists, change file attribute for overwriting
    if os.path.isfile(path):
        os.chmod(path, 0o644)
        return True
    else:
        _, fileExtension = os.path.splitext(path)
        if fileExtension:
            path = os.path.dirname(path)
        os.makedirs(path, exist_ok=True)
        return False


def full_path(path) -> str:
    return os.path.normpath(os.path.join(os.getcwd(), path))


def remove_empty_folders(path, removeRoot=True):
    """Function to remove empty folders

    Arguments:
        path {str} -- Represent the root directory for cleaning up

    Keyword Arguments:
        removeRoot {bool} -- Represent the flag for deleting the root directory (default: {True})
    """
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        print("Removing empty folder:", path)
        os.rmdir(path)


def clean_up_folder(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def file_loader(path, read_lines=False):
    if not os.path.isabs(path):
        path = os.path.join(dirname(dirname(abspath(__file__))), path)
    if not os.path.exists(path):
        raise GErrorFileNotFound('File does not exist! [Path: {}]'.format(path))
    with open(path, encoding="utf-8") as f:
        return f.readlines() if read_lines else f.read()


def file_writer(path, data):
    with open(path, 'w') as outfile:
        outfile.write(data)


def json_loader(path) -> Dict:
    return json.loads(file_loader(path))


def json_writer(output, data, indent=None):
    path = os.path.dirname(output)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.debug('Resolved file path: {}'.format(path))
    else:
        if os.path.exists(output):
            try:
                os.remove(output)
            except PermissionError:
                print('IOPermissionError : resolved {}'.format(os.path.basename(output)))
                os.chmod(output, stat.S_IWRITE)
                os.remove(output)

    with open(output, 'w') as outfile:
        json.dump(data, outfile, indent=indent or 4)


def append_and_update_json(path, data, key_name='name'):
    over_summaries = []
    if os.path.isfile(path):
        json_data = json_loader(path)
        # load data and exclude the duplicate dict object
        over_summaries = [item for item in json_data if item[key_name] != data[key_name]]

    over_summaries.append(data)
    with open(path, 'w') as f:
        f.write(json.dumps(over_summaries, indent=4))


def make_archive(source, destination):
    if os.path.exists(destination):
        try:
            os.remove(destination)
        except PermissionError:
            print('PermissionError do change')
            os.chmod(destination, stat.S_IWRITE)
            os.remove(destination)

    base = os.path.basename(destination)
    name, format = os.path.splitext(base)
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format[-3:], archive_from, archive_to)
    shutil.move(base, destination)


def unpack_archive(zip_file_path, output_dir):
    package_name, _ = os.path.splitext(zip_file_path)
    if os.path.exists(package_name):
        shutil.rmtree(package_name, onerror=on_rm_error)
    shutil.unpack_archive(zip_file_path, output_dir)
