from contextlib import contextmanager
import datetime
from fabric import operations
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import upload_template, append
import os.path
import posixpath

PROJ_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONF_DIR = os.path.abspath(os.path.join(PROJ_DIR, 'conf'))

env.user = "oc"
env.gunicorn_port = 9000
env.code_dir = '~/OpenCommunity/'
env.venv_command = '. bin/activate'
env.log_dir = '/var/log/opencommunity/'
env.clone_url = "https://github.com/hasadna/OpenCommunity.git"
env.backup_dir = '~/backups'
env.pip_version = "1.5.4"


@contextmanager
def virtualenv(path):
    with cd(path):
        with prefix(env.venv_command):
            yield


@task
def qa_old():
    env.user = "udi"
    env.hosts = ['oc-dev.modelarity.com']
    env.log_dir = '%slogs/' % env.code_dir
    env.pidfile = '/home/udi/OpenCommunity/run/masterpid'


def qa():
    env.vhost = '%s.qa.opencommunity.org.il' % env.user
    env.redirect_host = 'www.%s' % env.vhost
    env.hosts = ['qa.opencommunity.org.il']
    env.ocuser = "oc_" + env.user
    env.code_dir = '/home/%s/OpenCommunity/' % env.user
    env.log_dir = '%slogs/' % env.code_dir
    env.clone_url = "https://github.com/%s/OpenCommunity.git" % env.github_user
    env.venv_command = '. venv/bin/activate'
    env.venv_dir = '%svenv/' % env.code_dir
    env.pidfile = '/home/%s/opencommunity.pid' % env.ocuser


@task
def udi():
    env.gunicorn_port = 9010
    env.user = 'udi'
    env.github_user = 'nonZero'
    qa()


@task
def amir():
    env.gunicorn_port = 9011
    env.user = 'amir'
    env.github_user = 'amir99'
    qa()


@task
def yaniv():
    env.gunicorn_port = 9012
    env.user = 'yaniv'
    env.github_user = 'yaniv14'
    qa()


@task
def paul():
    env.gunicorn_port = 9013
    env.user = 'paul'
    env.github_user = 'pwalsh'
    qa()


@task
def prod():
    env.hosts = ['oc@ny1.opencommunity.org.il']
    env.redirect_host = 'opencommunity.org.il'
    env.venv_command = '. ~/.virtualenvs/oc/bin/activate'
    env.pidfile = '/home/oc/OpenCommunity/src/masterpid'
    env.ocuser = "oc"
    env.code_dir = '/home/%s/OpenCommunity/' % env.user
    env.venv_dir = '%svenv/' % env.code_dir


@task
def enprod():
    env.user = "en"

    env.code_dir = '/home/%s/OpenCommunity/' % env.user
    env.venv_dir = '%svenv/' % env.code_dir
    env.venv_command = '. venv/bin/activate'
    env.log_dir = '%slogs/' % env.code_dir

    env.vhost = 'en.demos.org.il'
    env.redirect_host = 'www.%s' % env.vhost
    env.hosts = [env.vhost]

    env.ocuser = "weben"
    env.pidfile = '/home/%s/web.pid' % env.ocuser

    env.gunicorn_port = 9001


@task
def host_type():
    run('uname -s')


@task
def git_log():
    with virtualenv(env.code_dir):
        run("git log -n 1")


@task
def freeze():
    with virtualenv(env.code_dir):
        run("pip freeze")


@task
def reload_app():
    with virtualenv(env.code_dir):
        run("cd src && sudo kill -HUP `cat %s`" % env.pidfile)


@task
def upgrade_pip():
    with virtualenv(env.code_dir):
        run("pip install pip=={}".format(env.pip_version))


@task
def deploy(restart=True):
    upgrade_pip()
    with virtualenv(env.code_dir):
        run("git pull")
        run("pip install -r requirements.txt")
        run("pip install -r deploy-requirements.txt")
        run("cd src && python manage.py syncdb --noinput")
        run("cd src && python manage.py migrate --merge --noinput")
        run("cd src && python manage.py collectstatic --noinput")
        run("git log -n 1 --format=\"%ai %h\" > static/version.txt")
        run("git log -n 1 > static/version-full.txt")
    if restart:
        reload_app()


@task
def hard_reload():
    run("sudo supervisorctl restart opencommunity")


@task
def very_hard_reload():
    run("sudo service supervisor stop")
    run("sudo service supervisor start")


@task
def log():
    run("tail %s*" % env.log_dir)


APT_PACKAGES = [
    'postgresql',
    'nginx',
    'supervisor',
    'python',
    'virtualenvwrapper',
    'git',
    'python-dev',
    'libpq-dev',
    'libjpeg-dev',
    'libjpeg8',
    'zlib1g-dev',
    'libfreetype6',
    'libfreetype6-dev',
    'postfix',
    'redis-server',
]


@task
def server_setup():
    run("sudo apt-get update")
    run("sudo apt-get upgrade -y")
    run("sudo apt-get install -y %s" % " ".join(APT_PACKAGES))


@task
def create_ocuser_and_db():
    run("sudo adduser %s --gecos '' --disabled-password" % env.ocuser)
    run("sudo -iu postgres createuser %s -S -D -R" % env.ocuser)
    run("sudo -iu postgres createdb %s -O %s" % (env.ocuser, env.ocuser))
    run("sudo -iu postgres psql -c \"alter user %s with password '%s';\"" % (
        env.ocuser, env.ocuser))


@task
def clone_project():
    run("git clone %s %s" % (env.clone_url, env.code_dir))
    with cd(env.code_dir):
        run("virtualenv venv --prompt='(%s) '" % env.ocuser)


@task
def create_local_settings():
    with cd(env.code_dir):
        upload_template('ocd/local_settings.template',
                        env.code_dir + 'src/ocd/local_settings.py',
                        {'ocuser': env.ocuser, 'host': env.vhost},
                        use_jinja=True)


@task
def nginx_setup():
    with cd(env.code_dir):
        upload_template('nginx.conf.template',
                        env.code_dir + 'conf/nginx.conf',
                        {
                            'host': env.vhost,
                            'redirect_host': env.redirect_host,
                            'dir': env.code_dir,
                            'port': env.gunicorn_port,
                        }, use_jinja=True, template_dir=CONF_DIR)
        nginx_conf1 = '/etc/nginx/sites-available/%s.conf' % env.ocuser
        nginx_conf2 = '/etc/nginx/sites-enabled/%s.conf' % env.ocuser

        #       FIXME
        #       uncomment('/etc/nginx/nginx.conf',
        #                 'server_names_hash_bucket_size\s+64',
        #                 use_sudo=True)

        run('sudo ln -fs %sconf/nginx.conf %s' % (env.code_dir, nginx_conf1))
        run('sudo ln -fs %s %s' % (nginx_conf1, nginx_conf2))
        run('sudo service nginx configtest')
        run('sudo service nginx start')
        run('sudo service nginx reload')


@task
def gunicorn_setup():
    with cd(env.code_dir):
        upload_template('server.sh.template',
                        env.code_dir + 'server.sh',
                        {
                            'venv': env.venv_dir,
                            'port': env.gunicorn_port,
                            'pidfile': env.pidfile,
                        }, mode=0777, use_jinja=True, template_dir=PROJ_DIR)


@task
def supervisor_setup():
    with cd(env.code_dir):
        upload_template('supervisor.conf.template',
                        env.code_dir + 'conf/supervisor.conf',
                        {
                            'dir': env.code_dir,
                            'ocuser': env.ocuser,
                            'logdir': env.log_dir,
                            'venv_dir': env.venv_dir,
                        }, mode=0777, use_jinja=True, template_dir=CONF_DIR)

        run(
            'sudo ln -fs %sconf/supervisor.conf /etc/supervisor/conf.d/%s.conf'
            % (env.code_dir, env.ocuser))
        run("sudo supervisorctl reread")
        run("sudo supervisorctl update")
        run("sudo supervisorctl start %s" % env.ocuser)


@task
def project_setup():
    with cd(env.code_dir):
        run('mkdir -p uploads')
        run('sudo chown %s uploads' % env.ocuser)
        run('mkdir -p %s' % env.log_dir)
    create_local_settings()
    deploy(restart=False)
    gunicorn_setup()
    supervisor_setup()
    nginx_setup()


@task
def initial_project_setup():
    create_ocuser_and_db()
    clone_project()
    project_setup()


@task
def createsuperuser():
    """ Creates a Django superuser for the project """
    with virtualenv(env.code_dir):
        run("cd src && python manage.py createsuperuser")


@task
def supervisor_status():
    """ Show server's supoervisord status """
    run("sudo supervisorctl status")


@task
def branch():
    """ Shows current (and all) branchs """
    with cd(env.code_dir):
        run('git branch')


@task
def switch(branch):
    """ fetches all branchs, and checkouts the specified git branch """
    with cd(env.code_dir):
        run('git fetch origin')
        run('git checkout {}'.format(branch))
        deploy()


@task
def showkeys():
    """ Displays authorized public ssh keys for user """
    with hide('stdout'):
        keys = run('cat .ssh/authorized_keys')
    print keys


@task
def push_key(key_file):
    """ Appends an ssh public key file from the specified file
    """
    with open(key_file) as f:
        key_text = f.read()
    append('~/.ssh/authorized_keys', key_text)


@task
def rebuild_index():
    """Rebuilds haystack search indexes for project"""
    with virtualenv(env.code_dir):
        run("cd src && python manage.py rebuild_index --noinput")
        run("sudo chown -v {} whoosh_index whoosh_index/*".format(env.ocuser))


@task
def backup_db():
    now = datetime.datetime.now()
    filename = now.strftime("ocd-%Y-%m-%d-%H-%M.sql.gz")
    fullpath = posixpath.join(env.backup_dir, filename)
    run('sudo -u postgres pg_dump {} | gzip > {}'.format(
        env.ocuser, fullpath))
    operations.get(fullpath)


@task
def load_local_db_from_file(filename):
    if not os.path.isfile(filename):
        abort("Unknown file {}".format(filename))

    if not confirm(
            "DELETE local db and load from backup file {}?".format(filename)):
        abort("Aborted.")

    drop_command = "drop schema public cascade; create schema public;"
    local('''python -c "print '{}'" | python manage.py dbshell'''.format(
        drop_command, filename))

    cmd = "gunzip -c" if filename.endswith('.gz') else "cat"
    local('{} {} | python manage.py dbshell'.format(cmd, filename))
