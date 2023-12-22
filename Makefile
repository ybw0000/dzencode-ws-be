clean-code:
	isort .
	black .
	flake8
	flake8 --radon-max-cc 10
	mypy .
test:
	coverage run manage.py test
	coverage html
	coverage report -m
