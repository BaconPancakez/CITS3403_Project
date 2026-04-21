from flask import Flask

app = Flask(__name__)

# To run
# source .venv/bin/activate
# flask run or flask run --port [port name, for e.g. 8000]

@app.route("/")
def index():
    return '<!DOCTYPE html><html lang="en"><head><title>hello</title></head><body>hello, isit working' \
    '</body></html>'
