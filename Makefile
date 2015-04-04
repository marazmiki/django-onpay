test:
	python setup.py test

release:
	python setup.py sdist --format=zip,bztar,gztar register upload
	python setup.py bdist_wheel register upload

flake8:
	flake8 onpay

coverage:
	coverage run --rcfile=.coveragerc --include=onpay/* setup.py test
	coverage html

coveralls:
	coveralls --config_file=coverage.rc


clean:
	rm -rf *.egg *.egg-info
	rm -rf htmlcov
	rm -f .coverage
	find . -name "*.pyc" -exec rm -rf {} \;


