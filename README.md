# Udacity Item Catalog

A simple Restaurant Menu web application that provides a list of courses within a variety of items and integrate third party user registration and authentication from Google and Facebook. Authenticated users have the ability to post, edit, and delete their own items only.


## Database Setup

The database file ```catalog.db``` is provided with the code with testing data, but you can delete this file and run ```python database_setup.py``` to create new empty database file, and run ```python db_data.py``` to insert the testing data.


## Usage

Launch the Vagrant VM from inside the *vagrant* folder with:
```sh
$ vagrant up
```
Then access the shell with:
```sh
$ vagrant ssh
```
Then move inside the catalog folder:
```sh
$ cd /vagrant/catalog
```
Then run the application:
```sh
$ python application.py
```
After the last command you are able to browse the application at this URL: [http://localhost:5000/](http://localhost:5000/)


## REST End-Points
The below JSON rest points are available in the application:
1) Get list of all courses http://localhost:5000/course/JSON
2) Get list of all courses items with details `http://localhost:5000/course/<int:course_id>/JSON`
   e.g. [http://localhost:5000/course/1/JSON](http://localhost:5000/course/1/JSON)
