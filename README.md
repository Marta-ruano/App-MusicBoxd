MusicBoxd

A simple Flask RESTful API that allows users to store, organize and review music (albums and songs)  
Each user sign up or login, and they have access to their own music 

Commands to run the project

Clone the repository: git clone https://github.com/your-username/App-MusicBoxd.git and then cd App-MusicBoxd

Create a virtual environment: python -m venv env

Activate the virtual environment: .\env\Scripts\activate or source env/bin/activate

Install the dependencies: pip install -r requirements.txt

Create a .env file in the project folder and add your configuration (for example database credentials and secret key):
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url

Run the application: flask --app app/app.py run

Open in your browser or API client (Postman): http://localhost:5000
