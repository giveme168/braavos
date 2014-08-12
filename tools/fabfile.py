from fabric.api import *

env.user = "inad"
env.directory = "/home/inad/apps/braavos/"
env.hosts = ['z.inad.com']


def prepare_deploy():
    local("echo ------------------------")
    local("echo DEPLOYING Braavos TO PRODUCTION")
    local("echo ------------------------")


def restart_service():
    run("sudo supervisorctl restart braavos")


def deploy():
    prepare_deploy()
    with cd(env.directory):
        run("git pull origin master")
    restart_service()
