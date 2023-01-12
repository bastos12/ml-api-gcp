# Reglage de la version de Python utilisée
FROM python:3.8.10

ENV PYTHONUNBUFFERED True

# Environement
ENV APP_HOME /api
WORKDIR $APP_HOME
COPY . ./

# Dependances
RUN pip install -r requirements.txt

# Web server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 api:app