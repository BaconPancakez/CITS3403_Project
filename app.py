from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# To run
# source .venv/bin/activate
# flask run or flask run --port [port name, for e.g. 8000]

@app.route("/")
def index():
    return render_template('admin.html')

@app.route("/course")
def course():
    return render_template("coursepg.html")

if __name__ == "__main__":
    app.run(debug=True)