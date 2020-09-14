
## Ingredients
+ **Digital Ocean**: The infrastructure provider
+ **Droplet with Ubuntu 18.04**: A droplet with Ubuntu installed on it.
+ **Gunicorn**: the application server serving the Django app (which is a Wsgi application) (handles dynamic requests between Django and webserver)
+ **Nginx**: A http webserver which reverse proxies Gunicorn and serves the static files.
+ **Supervisor**: 
+ **Virtualenv** and **Pip**: Of course, it is out of question that we not use a virtual environment for our project as well as the python package manager Pip.

## Server setup

### Get started: Your server Ip address and Ssh key

To generate a public/private key pair, one can use ssh-keygen (locally on your machine!)
For window users I recommend using PuTTy as client with which one can ssh into the cloud server instance.
The authorized keys are to be found in ~/.ssh/authorized-key

(rsync..)

### Settings for PuTTy
Connection Type: SSH. Enter the Ip adress of the droplet (Host Name)
Go to Connection, SSH and make sure, SSH protocol version 2 is selected. Then go to subpoint *Auth* and browse for your private key file. When loading the session, you are prompted for your key passphrase.

### Connect as root user, create new user and grant him administrative privileges
Is is advisable to create a new user since it is easy to do damage with root access. As root, do:

```console
root@ubuntu:~$ adduser django

```

#### Our new home
The home directory of this new user is `home/django/` and this is where we will do most of the work.
To learn to know our new home, cd into it. Then type `ls -la` to list all directories and files in a verbose manner. One file of interest is `.bashrc`. It is a bash script that is run whenever Bash is started interactively. It holds initialization command. Since our home is so empty, we create the directories *bin* (here will live the gunicorn start script), *logs* and *run* (here will live the unix socket file)

Next, we give this new user root privileges, i.e. allow this user to `sudo`. We do this by adding the user to the sudo-group.
```console
root@ubuntu:~$ usermod -aG sudo django
```

!From now on, everything we do, we will do with non-root user *django*.

Ubuntu refresher: to check which user you *are* currently, you can type ```whoami``` into the shell.
To change user, i.e. to newly created django, type ``` su - django```.

### Install needed tools
```console
django@ubuntu:~$ sudo apt update
django@ubuntu:~$ sudo apt install python3-pip, python3-dev libpq-dev postgresql postgresql-contrib nginx curl supervisor
```

### Create a PostgreSQL database and user
PostgreSQL comes with an operation system user *postgres* for administrative database tasks. To start a *psql* session, we use sudo and pass this user (`-u postgres`).
```console
$ sudo -u postgres psql
```

Note: every Postgres statement must end with a semi-colon. Let us create a database called *db_name* (please replace it by a name of your choice, or not^^) and a user called *admin*, set some defaults and grant this user administrative access to the newly created database.
```psql
postgres=# CREATE DATABASE light;
postgres=# CREATE USER admin WITH PASSWORD 'password';
postgres=# ALTER ROLE admin SET client_encoding TO 'utf8';
postgres=# ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE admin SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE [db_name] TO admin;
postgres=# \q
```

!Actually with the database in particular, it is very much recommended to use a very STRONG password.

### Create a python virtual environment
#### Install virtualenv
If not already installed, install *virtualenv* now.
```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv virtualenvwrapper
```
I like to use *virtualenvwrapper* but it is not needed.

#### Configure shell to work with virtualenvwrapper
Create a directory, e.g. ```/home/django/Env``` in your home folder. This will be the place where virtualenvwrapper stores all virtual environment you create with it.
Open `/home/django/.bashrc` into a text editor (`nano <file>` or `vim <file>`), go to the end of the file and insert
```bash
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=~/Env
source /usr/local/bin/virtualenvwrapper.sh
```
save the changes and close the editor.

Remark: To be able to use these environment variables in the current session, type
```source ~ /.bashrc```

### Create a virtual environment for the project and install Django
Cd into `home/django/`, create a new directory - the root directory of our project - we call it for now abstractly [project-dir].
With virtualenvwrapper, the command
```mkvirtualenv [venv-name]```
will create a new virtual environment name *[venv-name]*. Its lives at `home/django/Env/[venv-name]`.
Or you use plain virtualenv, cd into the [project-dir] and type
```virtualenv [venv-name]```

### Start a new Django project or clone a repo

Now, we could either
+ start a new Django project
+ or copy a local project repo or a repo from the cloud into this new directory.

In the first case, start a new project with
```
django-admin startproject name [directory]
```
where *name* is the name of the django project and directory where we want the base template be created in.
It will create a folder *name* inside *directory* and inside the folder *name*, you will find `manage.py` as well as the django project package whose folder has the same name as *name*. So from outer to inner, we have three folders (and they could very well at this moment all have the same name...):
- the project root folder which we will call [project-dir] (this directory, if locally on your machine, is the one you would source-control with *Git*) and for this reason is kind of the same as a cloud repo directory.
- the Django source code folder (many rename it into *src* , probably because otherwise there are to many folders with the same name - for the sake of this guide we will do so here too) and later it will live side-by-side with folders like *bin*, *docs*, *tests*, ... We call this folder from now on either [base-dir] or simply *src*
- and next to `manage.py`, the django project folder (lets call it [django-project-dir]) containing the all important project scripts `settings.py`, `urls.py` and `wsgi.py`

More usually you will clone an existing project. Cd into `home/django/` and type
```
git clone https://github.com/YourGithubProfile/YourRepo.git [directory]
```
Note: if you leave out the optional [directory], the repo will install into a folder with the same name as the repo.

If it comes with a requirements file, immediately install the dependencies via `pip install -r requirements.txt`.
(If you are intend of using PostgreSQL for your django project, make also sure psycopg2 is installed).

### Prepare your django project
I recommend the following setup for the settings of the django project.
In `production.py`, set `ALLOWED_HOSTS = ['ip', ..]`
where *ip* should be replaced by the actual ip-adress of the Droplet.
The next important settings are for the database. Put the following also in `production.py`
```python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DB_NAME'),
    'USER': os.getenv('DB_USER'),
    'PASSWORD': os.getenv('DB_PASSWORD'),
    'HOST': os.getenv('DB_HOST'),
    'PORT': os.getenv('DB_PORT'),
   }
}
```
following best practice where you put these things in environment variables. (I recommend using dotenv)
Now you could migrate (create the database tables).

In the files `manage.py` and `wsgi.py`, make sure we have
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')
```
The environment variable `DJANGO_SETTINGS_MODULE` controls which settings are used. To test out if your django project is able to run, do
```console
workon [env_name]
export PYTHONPATH=$PYTHONPATH:/home/django/[project_dir]/src
export DJANGO_SETTINGS_MODULE=settings.development
python3 manage.py runserver 0.0.0.0:8000
```
You can now serve to the ip adress:8000 and should see the homepage. 

### Enable and start Supervisor
```
sudo systemctl enable supervisor
sudo systemctl start supervisor
```

### Install Gunicorn
*Gunicorn* is the application server which we will put behind a proxy http server: *Nginx*. To monitor and control gunicorn, we will use *supervisor*. We start by installing Gunicorn into the virtual environment: `pip install gunicorn`. 

To quickly test if gunicorn is working properly, we write a simple hello world wsgi app (`src/test_wsgi.py`):
```python
def app(environ, start_response):
    data = b"Hello World!\n"
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
        ])
    return iter([data])
```
To run it,
```console
gunicorn -w 3 -b 0.0.0.0:8000 test_wsgi:app
```

### Gunicorn coniguration file

We create now a configuration file (`home/django/bin/gunicorn_start`) for our django app:
```console
touch bin/gunicorn_start
vim bin/gunicorn_start
```
and fill it like that:

```bash
#!/bin/bash

NAME="[project_name]"
BASE_DIR=/home/django/[project_dir]/src/    # the Django base dir
USER=django                                         
GROUP=django
WORKERS=3
SOCK_FILE=/home/django/run/gunicorn.sock     # unix socket
DJANGO_SETTINGS_MODULE=[django-project-dir].settings.production
DJANGO_WSGI_MODULE=[django-project-dir].wsgi
LOG_LEVEL=error                             # or use =debug

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $BASE_DIR
source /home/django/Env/[venv-name]/bin/activate

# set the used django settings (production or development) as env var
# so wsgi.py can read it
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
# add BASE_DIR to the python path
export PYTHONPATH=$BASE_DIR:$PYTHONPATH

# if the directory containing the socket file doesn't exists yet, create it
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Execute Gunicorn
exec ../bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$SOCK_FILE \
  --log-level=$LOG_LEVEL \
  --log-file=-
```

Next, make this config file executable:
```console
chmod u+x bin/gunicorn_start
```

### Configure supervisor
Supervisor will run for us the gunicorn server. Create
```
touch /home/django/logs/gunicorn-error.log
```
and a new supervisor config file
```
sudo nano /etc/supervisor/conf.d/[project-name].conf
```
Note: In /etc/supervisor/supervisord.conf, general configurations for supervisor
are contained. At the end of that file there are the lines
```
[include]
files = /etc/supervisor/conf.d/*.conf
```
stating that all `.conf` files in the folder `conf.d` will be considered as config files
for processes, supervisor should take care of.

In our config file, we put:
```config
[program:[project_name]]
command=/home/django/bin/gunicorn_start
directory=/home/django/[project_dir]
user=django
group=django
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/django/logs/gunicorn-error.log
```

Every time we change these config files we run
```
sudo supervisorctl reread
sudo supervisorctl update
```

To check if our gunicorn process is running,
```
sudo supervisorctl status [project_name]
```

### Configure Nginx
To check if Nginx is working, 
```sudo service nginx restart```, surf to your server's ip and you should
see nginx' default page.

For Nginx, we also add a configuration file:
```sudo vim /etc/nginx/sites-available/[project_name]```
and fill it like:
```nginx
upstream app_server {
    server unix:/home/django/run/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;

    # add here the ip address of your server
    # or a domain pointing to that ip
    server_name xxx.xxx.xx.xxx;

    keepalive_timeout 5;
    client_max_body_size 4G;

    access_log /home/django/logs/nginx-access.log;
    error_log /home/django/logs/nginx-error.log;

    location /static/ {
        alias /home/django/[project_dir]/static_cdn/;
    }

    # checks for static file, if not found proxy to app
    location / {
        try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_redirect off;
      proxy_pass http://app_server;
    }
}
```
Create a symbolic link:
```
sudo ln -s /etc/nginx/sites-available/[project_name]
```
and remove the default website (of nginx).


### Deploy iteration
```console
workon [venv-name]
cd /home/django/[project_dir]
sudo git pull origin master
python manage.py collectstatic
python manage.py migrate
sudo supervisorctl restart [project_name]
exit
