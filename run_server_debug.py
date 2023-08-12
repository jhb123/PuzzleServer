from flaskr import EmailManager, CloudStorage, PuzzleDatabase, UserDatabase
from flaskr import create_app

email_manager = EmailManager()
cloud_storage = CloudStorage()
database = PuzzleDatabase()
user_database = UserDatabase()

app = create_app(email_manager, cloud_storage, database, user_database)

if __name__ == "__main__":
    # use this to start it in debug mode
    app.run(host="0.0.0.0", port="5000", debug=True)
