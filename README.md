# MusicBoxd

A simple Flask RESTful API that allows users to store, organize and review music (albums and songs)  
Each user sign up or login, and they have access to their own music 

## Commands to run the project

Clone or download the repository: git clone https://github.com/your-username/App-MusicBoxd.git 

Open the terminal: cd App-MusicBoxd

Create a virtual environment: python -m venv env

Activate the virtual environment: .\env\Scripts\activate or source env/bin/activate

Install the dependencies: pip install -r requirements.txt

Change the secret_key and database with your own password and database url: app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:secretkey@localhost/MusicBoxd"

Execute migrations: flask --app app/app.py db upgrade --directory app/models/migrations

Import seeders: flask --app app/app.py seed

Run the application: flask --app app/app.py run

Open in your browser: http://localhost:5000
