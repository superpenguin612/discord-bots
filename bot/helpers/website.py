from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello. I am alive!"

if __name__ == "__main__":
    app.run(threaded=True, port=5000)