from flask import Flask
from flask_scss import Scss

app = Flask(__name__)
Scss(app, static_dir='static', asset_dir='scss')

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
