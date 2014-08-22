test:
	python setup.py test

release:
	python setup.py sdist --format=zip,bztar,gztar register upload

flake8:
	flake8 --ignore=E501,W292 --max-complexity 12 onpay

coverage:
	coverage run --include=onpay/* setup.py test
	coverage html

coveralls:
	coveralls --config_file=coverage.rc


clean:
	rm -rf *.egg *.egg-info
	rm -rf htmlcov
	rm -f .coverage
	find . -name "*.pyc" -exec rm -rf {} \;


