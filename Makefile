fill:
	python tools/fill_up.py
clear:
	python tools/clear_data.py
db_refresh: clear fill

serve:
	python app.py

web: db_refresh serve

test:
	py.test --tb=short tests --random

clean_pyc:
	find . -name '*.pyc' -delete

hooks:
	cp hooks/pre-commit .git/hooks/
