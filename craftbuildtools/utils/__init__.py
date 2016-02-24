import fnmatch
import os
from urllib.parse import urlsplit, urlparse


def save_python_script(script_folder, script_url):
    import requests

    if not os.path.exists(script_folder):
        os.makedirs(script_folder)

    script_name = get_filename(script_url)
    script_data = requests.get(script_url).text

    script_loc = os.path.join(script_folder, script_name)

    write_file(script_loc, script_data)

    if not os.path.exists(script_loc):
        raise FileNotFoundError("Unable to locate file %s after attempting to save it" % script_loc)

    return script_loc


def is_url(url):
    return urlparse(url).scheme != ""


def get_filename(url_or_path):
    if not is_url(url_or_path):
        if not os.path.exists(url_or_path):
            return None
        return "%s%s" % os.path.splitext(url_or_path)
    else:
        return "%s%s" % os.path.splitext(os.path.basename(urlsplit(url_or_path).path))


def get_file_extension(path):
    if is_url(path):
        return "%s" % os.path.splitext(os.path.basename(urlsplit(path).path))[1]
    else:
        if not os.path.exists(path):
            return None
        return "%s" % os.path.splitext(path)[1]


def get_files_recursive(path, match='*.py'):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, match):
            matches.append(os.path.join(root, filename))

    return matches


def get_config_from_file(file, trim_newlines=True):
    with open(file, 'r') as config_file:
        data = config_file.read()
        if trim_newlines:
            data = data.replace('\n', '')
        return data


def write_file(file, data):
    with open(file, 'w') as data_file:
        data_file.write(data)


class ChangeDir:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    # Change directory with the new path
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    # Return back to previous directory
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]
