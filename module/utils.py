import subprocess
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os


def handle_uploaded_file(file, location, name):
    ext = file.name.split('.')[-1]
    alias = '{0}.{1}'.format(name, ext)
    fs = FileSystemStorage(location=location)
    filename = fs.save(alias, file)
    return alias


def terminal_out(command):
    process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode('utf-8')
    out = out.split('\n')
    for o in out:
        print(o)


def terminal(command):
    subprocess.run(command.split(' '))
