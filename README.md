## Braavos

How To:

  1. postgresql 里创建数据库
  2. 配置local_config.py, 填写SQLALCHEMY_DATABASE_URI地址
  3. make web # 初始化数据库, 填充测试数据
  4. python app.py

### 啟動postgresql

1. initdb -D data
2. postmaster -D data
3. createdb braavos
