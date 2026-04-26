from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.secret_key = "pKcXxKlaHtVm7u2Urhlz58SD"

# To run
# source .venv/bin/activate
# flask run or flask run --port [port name, for e.g. 8000]

@app.route("/")
def index():
    return render_template('admin.html')

@app.route("/course")
def course():
    return render_template("coursepg.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("RAW FORM DATA:", request.form)

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if email == "admin@uwa.edu.au" and password == "1234":
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))

        flash("Signup submitted.", "success")
        return redirect(url_for("signup"))

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)