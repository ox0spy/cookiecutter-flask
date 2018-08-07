.PHONY: pip, lint, test, deploy, run-dev, run-prod, clean

pip:
	@pip install -U -r dev-requirements.txt

lint:
	pylint *.py {{cookiecutter.app_name}} tests

test:
	tox

deploy: clean
	@rsync -raPH -e ssh --delete --exclude .tox --exclude *.sqlite ./ gvm-wm:/data/web/{{cookiecutter.project_name}}

run-dev:
	@DEPLOY_ENV=dev python manage.py runserver

run-prod:
	@DEPLOY_ENV=prod gunicorn -D --worker-connections 65535 \
		--max-requests 2048 --keep-alive 30 -w 4 \
		-k 'meinheld.gmeinheld.MeinheldWorker' \
		-b localhost:12345 wsgi:app

clean:
	@echo "make clean ..."
	@find ./ -name '*.pyc' -exec rm -f {} +
	@find ./ -name '*.pyo' -exec rm -f {} +
	@find ./ -name '*.log' -exec rm -f {} +
	@find ./ -name '*~' -exec rm -f {} +
	@find ./ -name '__pycache__' -exec rm -rf {} +
	@find ./ -name 'instant_show.egg-info' -exec rm -rf {} +
	@find ./ -name '.pytest_cache' -exec rm -rf {} +
