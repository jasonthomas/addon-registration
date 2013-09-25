build:
	virtualenv -p python2.7 .
	bin/pip install -r requirements/test.txt
	bin/python setup.py develop

test:
	flake8 addonreg && bin/nosetests --with-coverage --cover-erase --cover-package addonreg addonreg

clean:
	rm -rf bin lib local include man

doc:
	bin/pip install -r docs/requirements.txt
	cd docs && make html

serve:
	bin/pserve development.ini

