# IZP-glosowanie

Requirements:
* python 3.6.3
* django 1.11.6
* pip3 ( https://stackoverflow.com/questions/6587507/how-to-install-pip-with-python-3 )

To start server with application on you local machine please execute following commands:
```
$ git clone https://github.com/czapiga/IZP-glosowanie.git
$ cd IZP-glosowanie/izp
$ python manage.py makemigrations polls
$ python manage.py migrate
$ pip install -r requirements.txt
$ python manage.py runserver
```
Django will inform you in terminal about server IP address and port.
After starting server you can go to [admin home page](http://127.0.0.1:8000/admin) and [list of active polls](http://127.0.0.1:8000/polls) to check if application actually started.

How to create superuser

$ python3.5 manage.py createsuperuser

After create account and login you can go to :
page with code list -> http://127.0.0.1:8000/codesList/
download code list in pdf -> http://127.0.0.1:8000/codesList/codes.pdf
