from flask import Flask
from os import getenv
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
import routes

app.secret_key = getenv("SECRET_KEY")


if __name__ == '__main__':
    app.run()
