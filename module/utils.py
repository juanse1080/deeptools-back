import subprocess
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def select_view(list_):
    if 'output' in list_:
        if 'response' in list_:
            if 'graph' in list_:
                return 'docker/full.html'
            return 'docker/order.html'
        return 'docker/last.html'
    return 'docker/first.html'


def handle_uploaded_file(file, location, name):
    ext = file.name.split('.')[-1]
    alias = '{0}.{1}'.format(name, ext)
    fs = FileSystemStorage(location=location)
    filename = fs.save(alias, file)
    return alias


def created_port(id, limit=65353, default='50051'):
    return default[:-len(str(id))]+str(id)


def terminal_out(command):
    process = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode('utf-8')
    out = out.split('\n')
    for o in out:
        print(o)


def terminal(command):
    subprocess.run(command.split(' '))
