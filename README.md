# bettingSite
Django Project

##Requirements
- Python 3.6
- Django 2.0
- Postgress Database

##Setup / Installation
Clone the project then go inside the `autobetting` directory. 

Create the environment for the project by using [virtualenv](https://virtualenv.pypa.io/en/stable/) or [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest).
Activate the virtual environment and run the following commands for setup/installation the project:-

- Upgrade the pip by using `pip install --upgrade pip`.
- Install all requirements by using `pip install  -r requirements.txt`.
- Update DATABASES setting the `setting.py` file.
- Run the migration commands
  - `python manage makemigrations`
  - `python manage migrate`


### Logging
Create the following folders for logging:-

- `logs` in project root
- `logs/debug`
- `logs/errors` 

