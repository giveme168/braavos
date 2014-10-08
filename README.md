[![Build Status](http://ci.inad.com/github.com/borngods/braavos/status.svg?branch=master)](http://ci.inad.com/github.com/borngods/braavos)

## Braavos

### Develop Dependence

- 1. postgresql
- 2. [pyenv](https://github.com/yyuu/pyenv) + [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv)
  - pyenv virtualenv braavos

### How To Start:

- 1. create database on postgresql #[PostgreSQL新手入门](http://www.ruanyifeng.com/blog/2013/12/getting_started_with_postgresql.html)
  - createdb braavos
- 2. edit local_config.py, SQLALCHEMY_DATABASE_URI is required
  - cp local_config.py.sample local_config.py
  - edit local_config.py
- 3. pip install -r requirements.txt  # in your virtual env
- 4. make hook  # init git hooks
- 5. make web  # = make clear + make fill + make serve
- 6. use Account0: test0@inad.com Password: default_password to login


### Filled Data When make fill

- Account: test0@inad.com Password: pwd123  Role: Admin
- Account: test1@inad.com Password: pwd123  Role: Leader
- Account: test2@inad.com Password: pwd123  Role: Saler


### 开发流程

- 1.Fork & Clone
- 2.git remote add upstream https://github.com/borngods/braavos.git
    git pull upstream
- 3.创建您的特性分支 (git checkout -b my-new-feature)
- 4.提交您的改动 (git commit -am 'Added some feature')
- 5.将您的修改记录提交到远程 git 仓库 (git push origin my-new-feature)
- 6.然后到 github 网站的该 git 远程仓库的 my-new-feature 分支下发起 Pull Request


### Test

    make test

### Deploy Dependence

- 1. nginx
- 2. supervisor
- 3. [pyenv](https://github.com/yyuu/pyenv) + [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv)
- 4. gunicorn

### Deploy

- 1. install fabric
- 2. add your id_rsa.pub to /home/inad/.ssh/authorized_keys on our server
- 3. fab deploy # read the tool/fabfile.py
