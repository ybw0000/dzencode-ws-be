clean-code:
	isort .
	black .

test:
	coverage run manage.py test
	coverage html
	coverage report -m
