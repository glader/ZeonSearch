# coding: utf-8

from datetime import date

from fabric.api import *
from fabric.contrib.files import exists, append, upload_template, sed

from fab_settings import *

env.directory = '/home/%s/projects/zeonsearch' % SSH_USER
env.manage_dir = env.directory
env.user = SSH_USER
env.activate = 'source %s/ENV/bin/activate' % env.directory
env.www_ssh_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAIEAlgcYVZYvzu1GX4Td+RLt9BIqUr33gkTz6MW2MHvWS/+9eKueA6+N7Bei2NqTBNg2HLUY0uOyG1NBmzoWZglht70iChcGLMVkvciQ1/QQfr5bvIbfgpPHuZMwn4ElFiiabhnZe9wALp+jjg0TnolWxbAfwJUmv2UDXXSiYDrfBes= glader hosting rsa-key-20150528'
env.forward_agent = True

if not env.hosts:
    env.hosts = ['82.196.9.202']


def virtualenv(command):
    with cd(env.directory):
        run(env.activate + ' && ' + command)


def init():
    with settings(user='root'):
        append('/etc/apt/sources.list', 'deb-src http://archive.ubuntu.com/ubuntu precise main')
        append('/etc/apt/sources.list', 'deb-src http://archive.ubuntu.com/ubuntu precise-updates main')

#        run('apt-get update')
#        run('apt-get upgrade -y')
#        run('apt-get install -y mc nginx mysql-client python-setuptools python-dev python-pip rrdtool sendmail memcached fail2ban')
#        run('apt-get build-dep -y python-mysqldb')
#        run('pip install --upgrade virtualenv')
#        run('apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev')  # Pillow dependencies

        if not exists('/home/%s' % SSH_USER):
            run('yes | adduser --disabled-password %s' % SSH_USER)
            run('mkdir /home/%s/.ssh' % SSH_USER)
            run('echo "%s" >> /home/%s/.ssh/authorized_keys' % (env.www_ssh_key, SSH_USER))

        if not exists('/var/log/projects/zeonsearch'):
            run('mkdir -p /var/log/projects/zeonsearch')
            run('chmod 777 /var/log/projects/zeonsearch')

        if exists('/etc/nginx/sites-enabled/default'):
            run('rm /etc/nginx/sites-enabled/default')

        if not exists('/etc/nginx/listen'):
            put('etc/nginx/listen', '/etc/nginx/listen', use_sudo=True)

        if not exists('/etc/nginx/sites-available/90-zeonsearch.conf'):
            run('touch /etc/nginx/sites-available/90-zeonsearch.conf')
            run('chown %s /etc/nginx/sites-available/90-zeonsearch.conf' % SSH_USER)
        if not exists('/etc/nginx/sites-enabled/90-zeonsearch.conf'):
            run('ln -s /etc/nginx/sites-available/90-zeonsearch.conf /etc/nginx/sites-enabled/90-zeonsearch.conf', shell=False)

        if not exists('/etc/init/zeonsearch.conf'):
            run('touch /etc/init/zeonsearch.conf')
            run('chown %s /etc/init/zeonsearch.conf' % SSH_USER)

        append('/etc/sudoers', '%s ALL=(ALL) NOPASSWD:/sbin/restart zeonsearch,/sbin/restart zeonsearch_celery' % SSH_USER)

        run('mkdir -p /home/%s/projects/zeonsearch' % SSH_USER)
        run('chown -R %(user)s:%(user)s /home/%(user)s' % {'user': SSH_USER})


def init_mysql():
    with settings(host_string='82.196.15.15', user='root'):
        run('apt-get update')
        run('apt-get upgrade -y')
        run('apt-get install -y fail2ban mc')
        run('DEBIAN_FRONTEND=noninteractive apt-get -q -y install mysql-server')
        run('mysqladmin -u root password mysecretpasswordgoeshere111')

        sed('/etc/mysql/my.cnf', 'bind-address.+$', 'bind-address = ::')
        run('/etc/init.d/mysql restart')


def production(mode=''):
    upload()
    environment()
    local_settings()
    nginx()
    upstart()
    migrate()
#    collect_static()
    restart()


def upload():
    with settings(user=SSH_USER):
        local('git archive HEAD | gzip > archive.tar.gz')
        put('archive.tar.gz', env.directory + '/archive.tar.gz')
        with cd(env.directory):
            run('tar -zxf archive.tar.gz')
            run('rm archive.tar.gz')
        local('del archive.tar.gz')


def environment():
    with cd(env.directory):
        with settings(warn_only=True):
            run('virtualenv ENV')
        virtualenv('pip install -r etc/deps/requirements.txt')


def local_settings():
    with settings(user=SSH_USER):
        with cd(env.manage_dir):
            upload_template(
                'zeonsearch/local_settings.py.sample',
                'zeonsearch/local_settings.py',
                globals(),
                backup=False
            )


def nginx():
    run('cp %(directory)s/etc/nginx/90-zeonsearch.conf /etc/nginx/sites-available/90-zeonsearch.conf' % env, shell=False)
    #sudo('/etc/init.d/nginx reload', shell=False)


def upstart():
    run('cp %(directory)s/etc/upstart/zeonsearch.conf /etc/init/zeonsearch.conf' % env, shell=False)


def manage_py(command):
    virtualenv('cd %s && python manage.py %s' % (env.manage_dir, command))


def migrate():
    with settings(user=SSH_USER):
        manage_py('migrate')


def collect_static():
    with settings(user=SSH_USER):
        run('mkdir -p /home/www/projects/zeonsearch/static')
        manage_py('collectstatic -c --noinput')


def restart():
    run('sudo restart zeonsearch')


def remote(args=''):
    manage_py(args)

# -----------------------------------------------------------------------

def run_local():
    local('ENV\\Scripts\\python manage.py runserver 0.0.0.0:8000')


def local_env():
    with settings(warn_only=True):
        local('virtualenv.exe ENV --system-site-packages')
    local('ENV\\Scripts\\pip install -r etc\\deps\\requirements_test.txt ')


def enter(args=''):
    local('ENV\\Scripts\\python manage.py %s' % args)


def local_migrate():
    with settings(warn_only=True):
        local('ENV\\Scripts\\python manage.py makemigrations core')
    local('ENV\\Scripts\\python manage.py migrate')


def update_local_db():
    run('mysqldump -u %(DATABASE_USER)s -p%(DATABASE_PASSWORD)s -h %(DATABASE_HOST)s %(DATABASE_DB)s |gzip > zeonsearch.sql.gz' % globals())
    get('zeonsearch.sql.gz', 'zeonsearch.sql.gz')
    run('rm zeonsearch.sql.gz')
    local('gzip -d zeonsearch.sql.gz')
    local('mysql -uroot %(DATABASE_DB)s < zeonsearch.sql' % globals())
    local('del zeonsearch.sql')


def local_static():
    local('cd src && ..\\ENV\\scripts\\python manage.py collectstatic -c --noinput --verbosity=0')
