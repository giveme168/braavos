fill:
	python tools/fill_users.py

db_init:
	python manage.py db init
db_migrate:
	python manage.py db migrate
db_upgrade:
	python manage.py db upgrade

syncdb: db_init db_migrate db_upgrade

web: syncdb fill serve
