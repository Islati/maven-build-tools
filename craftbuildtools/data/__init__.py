from .project import Project
from .todo import ToDo, ToDoManager

DEFAULT_CONFIGURATION = {
    'ftp-server': {
        'ftp-host': "HOST",
        'ftp-username': "USERNAME",
        'ftp-password': "PASSWORD",
        'remote-upload-directory': "/Dev/plugins/"
    }
}
