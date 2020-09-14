# django snippets
Some short snippets and notes about building sites with django

# Getting started with Django
Django is a web framework for building dynamic websites. It is based on the Model-Template-View pattern.

I you've never done something with Django, you can try it out in 2 Minutes:
Start with helloworld.py in this repo:
The smallest possible django project. If you want to see it in your browser, just do this:

1. Create new folder (e.g. ..../dev/django-sandbox)
2. Create new virtualenv: In a cmd shell, cd to your new folder and run `$ virtualenv .` (not necessary but recommended)
3. Make sure above virtual environment is activated and install django via pip: run: `$ pip install django`
4. Get the helloword.py and put it in your new folder 
5. Try it out with `$ python helloworld.py runserver`

Django is creating a simple server based on the socket python library for us.
The runserver command is there for running and testing our django webpage.
For deployment other tools will be needed.
