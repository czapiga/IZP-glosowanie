FROM python:3-onbuild

EXPOSE 8000

RUN python izp/manage.py makemigrations polls
RUN python izp/manage.py migrate

CMD ["python", "izp/manage.py", "runserver", "0.0.0.0:8000"]
