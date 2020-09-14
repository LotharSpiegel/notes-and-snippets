To release a new version of your python library on the [PyPi Python Package Index](https://pypi.org/), follow these steps: 

* Delete files in dist folder (in case there is a dist folder in the root dir of the project and it contains files) 
* Update version number (as you see fit) in setup.py and possibly commit this update as 'update version' or sth.
* Run 
```
$ setup.py sdist
``` 
on the cmd line in your project root. This will create (or fill) the dist folder (creating a tar.gz archive)
* Run
```
$ twine upload dist/*
```
on the cmd line in your project root. This will upload the archive created in the previous step to you pypi package repository
(and thus making the new release available through pip install <pypi_repo_name>


To create a new repo: tba
