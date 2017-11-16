# IZP-glosowanie

Requirements:
* python 3.6.3
* django 1.11.6
* pip3

To start server with application on you local machine please execute following commands:
```
$ git clone https://github.com/czapiga/IZP-glosowanie.git
$ cd IZP-glosowanie/izp
$ pip3 install -r ../requirements.txt
$ python manage.py makemigrations polls
$ python manage.py migrate
$ python manage.py runserver
```
Django will inform you in terminal about server IP address and port.
After starting server you can go to [admin home page](http://127.0.0.1:8000/admin) and [list of active polls](http://127.0.0.1:8000/polls) to check if application actually started.
