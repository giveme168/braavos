from fabric.api import run, local, task, env, settings
import fabric_gunicorn as gunicorn

env.name = "braavos"
env.user = "inad"
env.path = "/home/inad/apps/braavos"
env.hosts = ['z.inad.com']

env.remote_workdir = "/home/inad/apps/braavos/releases/current"
env.gunicorn_pidpath = "/home/inad/apps/braavos/releases/current/gunicorn.pid"
env.virtualenv_dir = "/home/inad/.pyenv/versions/braavos"
env.gunicorn_wsgi_app = 'app:app --log-file=-'
env.gunicorn_bind = '0.0.0.0:8001'


@task
def test():
    gunicorn.set_env_defaults()
    print env.remote_workdir
    print env.gunicorn_pidpath
    print env.gunicorn_bind


def prepare_deploy():
    local("echo ------------------------")
    local("echo DEPLOYING Braavos TO PRODUCTION")
    local("echo ------------------------")


@task
def checkout_latest():
    """Pull the latest code into the git repo and copy to a timestamped release directory"""
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    run("cd %(path)s/repository; git pull origin master" % env)
    run('cp -R %(path)s/repository %(path)s/releases/%(release)s; rm -rf %(path)s/releases/%(release)s/.git*' % env)
    run('cd %(path)s/releases/%(release)s; cp %(path)s/conf/local_config.py local_config.py' % env)


def install_requirements():
    """Install the required packages using pip"""
    run('cd %(path)s/releases/%(release)s; pyenv shell braavos; pip install -r requirements.txt' % env)


def migrate():
    """Run our migrations"""
    run('cd %(path)s/releases/%(release)s; pyenv shell braavos; python manage.py db upgrade' % env)


def symlink_current_release():
    """Symlink our current release, uploads and settings file"""
    with settings(warn_only=True):
        run('cd %(path)s; rm releases/previous; mv releases/current releases/previous;' % env)
    run('cd %(path)s; ln -s %(release)s releases/current' % env)


@task
def restart_server():
    # run('pkill gunicorn')
    # run('cd %(path)s/releases/current; pyenv shell braavos; gunicorn --daemon --bind 0.0.0.0:8001 app:app;' % env)
    run('cd /home/inad/apps/braavos; bash gunicorn_restart_server')

@task
def deploy():
    prepare_deploy()
    checkout_latest()
    install_requirements()
    migrate()
    symlink_current_release()
    # restart_server()


@task
def export():
    run('bash /home/inad/apps/braavos/start_export')


@task
def import_delivery():
    run('bash /home/inad/apps/braavos/start_import')


@task
def pg_dump():
    """dump database"""
    run('bash /home/inad/apps/braavos/start_dump')
