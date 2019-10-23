all: clean pyflakes

setup:
	pip install -r requirements.txt

run:
	python manage.py runserver

pyflakes:
	find -L . -name "*.py" | grep -v __init__ | xargs pyflakes

migrate:
	./manage.py makemigrations
	./manage.py migrate

test:
	./manage.py test

clean:
	sh cleanup.sh

upgrade_pip:
	pip install -U pip
	cat requirements.txt | awk -F '=' '{print $$1}' | xargs pip install -U
