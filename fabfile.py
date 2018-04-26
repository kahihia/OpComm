import datetime
import os
from contextlib import contextmanager
from io import StringIO

from fabric import operations
from fabric.api import *
from fabric.contrib.console import confirm
from pathlib import Path

env.user = "oc"
env.hosts = ["139.162.215.52"]
# Inside each task, env.host will be auto populated from the list above

env.project_name = "OpComm"
env.clone_url = "git@github.com:yaniv14/OpComm.git"
env.code_dir = f"/home/{env.user}/{env.project_name}"
env.static_path = f"{env.code_dir}/static/"
env.media_path = f"{env.code_dir}/uploads/"
env.pidfile = f'/home/{env.user}/{env.user}.pid'
env.port = 22

env.app_name = "oc"

env.venv_name = env.app_name
env.venvs = f"/home/{env.user}/.virtualenvs/"
env.venv_path = f"{env.venvs}{env.venv_name}/"
env.venv_command = f"source {env.venv_path}/bin/activate"

env.backup_dir = f"{env.code_dir}/backup/"

APT_PACKAGES = [
    # generic system related packages
    'unattended-upgrades',  # for auto updating your system
    'ntp',  # To keep time synchromized
    'fail2ban',  # to secure against SSH/other attacks

    # useful tools
    'git',
    'htop',
    'most',

    'python3',
    'virtualenvwrapper',  # for easily managing virtualenvs

    # required libraries for building some python packages
    'build-essential',
    'python3-dev',
    'libpq-dev',
    'libjpeg-dev',
    'libjpeg8',
    'zlib1g-dev',
    'libfreetype6',
    'libfreetype6-dev',
    'libgmp3-dev',
    'supervisor',

    # postgres database
    'postgresql',

    # nginx - a fast web server
    'nginx',

    'redis-server',
]


@task
def uptime():
    run("uptime")


@task
def uname():
    run("uname -a")


@task
def apt_upgrade():
    sudo("apt update", pty=False)
    sudo("apt upgrade -y", pty=False)
    sudo("apt autoremove -y", pty=False)


@task
def apt_install():
    # Set some configurations for postfix mail server
    cmd = '''debconf-set-selections <<< "postfix postfix/{} string {}"'''
    sudo(cmd.format('mailname', env.host))
    sudo(cmd.format('main_mailer_type', "'Internet Site'"))

    # install packages
    pkgs = " ".join(APT_PACKAGES)
    sudo(f"DEBIAN_FRONTEND=noninteractive apt-get install -y -q {pkgs}",
         pty=False)


# @task
# def setup_postfix():
#     sudo(f"DEBIAN_FRONTEND=noninteractive dpkg-reconfigure postfix", pty=False)


@task
def apt_install():
    pkgs = " ".join(APT_PACKAGES)
    sudo(f"DEBIAN_FRONTEND=noninteractive apt-get install -y -q {pkgs}",
         pty=False)


@task
def create_postgres_su():
    run("sudo -u postgres createuser -s sysop")
    run("createdb sysop")


@task
def clone_project():
    run(f"git clone {env.clone_url} {env.code_dir}", pty=False)


@task
def create_venv():
    run(f"mkdir -p {env.venvs}")
    run(
        f"virtualenv -p /usr/bin/python3 --prompt='({env.venv_name}) ' {env.venv_path}")


@contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.venv_command):
            yield


@task
def create_media_folder():
    with cd(env.code_dir):
        run('mkdir -p uploads')
        sudo('chown -R www-data uploads')


@task
def upgrade_pip():
    with virtualenv():
        run("pip install --upgrade pip", pty=False)


@task
def pip_install():
    with virtualenv():
        run("pip install -r requirements.txt", pty=False)


@task
def git_pull():
    with virtualenv():
        run("git pull", pty=False)


@task
def deploy():
    git_pull()
    pip_install()


@task
def m(cmd, pty=False):
    with virtualenv():
        run(f"./manage.py {cmd}", pty)


@task
def check():
    m('check')


@task
def send_test_mail():
    m('sendtestemail --admin')


@task
def migrate():
    m('migrate --noinput')


@task
def collect_static():
    m('collectstatic --noinput')


@task
def create_db():
    with virtualenv():
        run("./manage.py sqlcreate -D | psql", pty=False)


NGINX_CONF = """
server {{
    listen 80 default_server;
    return 410;
}}

server {{
    listen 80;
    server_name {host};
    charset     utf-8;

    location /static/ {{
        alias {env.static_path};
    }}

    location /uploads/ {{
        alias {env.media_path};
    }}

    location / {{
        uwsgi_pass  unix://{env.uwsgi_socket};
        include     uwsgi_params;
    }}
}}"""


@task
def create_nginx_conf():
    conf = NGINX_CONF.format(
        host=env.hosts[0],
        env=env,
    )
    filename = f"/etc/nginx/sites-available/{env.app_name}.conf"
    enabled = f"/etc/nginx/sites-enabled/{env.app_name}.conf"
    put(StringIO(conf), filename, use_sudo=True, )
    sudo(f"ln -sf {filename} {enabled}")

    sudo("rm -vf /etc/nginx/sites-enabled/default")

    sudo("nginx -t")

    sudo("service nginx reload")


@task
def nginx_log():
    sudo("tail /var/log/nginx/error.log")


@task
def reload_app():
    sudo('systemctl reload uwsgi.service')


@task
def kill_supervisor_pid():
    sudo(f"kill -HUP `cat {env.pidfile}`")


@task
def qa():
    env.instance = 'oc_qa'
    env.webuser = "oc_qa"
    env.user = "oc_qa"


@task
def sviva():
    env.instance = 'oc_sviva'
    env.webuser = "oc_sviva"
    env.user = "oc_sviva"


@task
def upgrade():
    git_pull()
    pip_install()
    migrate()
    collect_static()
    kill_supervisor_pid()


def make_backup():
    now = datetime.datetime.now()
    filename = now.strftime(
        "{}-%Y-%m-%d-%H-%M.sql.gz".format(env.project_name))
    run('mkdir -p {}'.format(env.backup_dir))
    fullpath = env.backup_dir + '/' + filename
    run('sudo -u postgres pg_dump --no-acl --no-owner {} | gzip > {}'.format(env.app_name,
                                                                             fullpath))
    return fullpath


@task
def remote_backup_db():
    path = make_backup()
    operations.get(path)
    run('ls -alh {}'.format(path))


@task
def backup_db():
    files = operations.get(make_backup())
    if len(files) != 1:
        print("no file downloaded!")
        return

    print(f"backup downloaded to: {files[0]}")
    latest = "latest.sql.gz"
    target = Path(files[0])
    local(f"cd {target.parent} && ln -fs {target} {latest}")
    print(f"link created to: {target.parent / latest}")
    return target


@task
def load_local_db_from_file(filename):
    if not os.path.isfile(filename):
        abort("Unknown file {}".format(filename))

    if not confirm(
            "DELETE local db and load from backup file {}?".format(filename)):
        abort("Aborted.")

    drop_command = "drop schema public cascade; create schema public;"
    local('''python3 -c "print('{}')" | python manage.py dbshell'''.format(
        drop_command, filename))

    cmd = "gunzip -c" if filename.endswith('.gz') else "cat"
    local('{} {} | python manage.py dbshell'.format(cmd, filename))


@task
def load_local_db_from_latest():
    filename = backup_db()
    load_local_db_from_file(str(filename))
