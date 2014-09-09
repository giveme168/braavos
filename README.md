[![Build Status](http://ci.inad.com/github.com/borngods/braavos/status.svg?branch=master)](http://ci.inad.com/github.com/borngods/braavos)

## Braavos

### Develop Dependence

- 1. postgresql or sqllite
- 2. [pyenv](https://github.com/yyuu/pyenv) + [pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv)

### How To Start:

  1. 创建数据库
  2. 配置local_config.py, 填写SQLALCHEMY_DATABASE_URI地址
  3. make hook  # 初始化 git hooks
  4. make web  # 初始化数据库, 填充测试数据, 启动server 

### 啟動postgresql

1. initdb -D data
2. postmaster -D data
3. createdb braavos


### Test

    make test

### Deploy Dependence

- 1. nginx
- 2. supervisor
- 3. gunicorn

### Deploy

  1. install fabric
  2. add your id_rsa.pub to /home/inad/.ssh/authorized_keys
  3. fab deploy # 参考tool/fabfile.py
