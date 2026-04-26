from flask import Flask, render_template, request

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # placeholder logic
        flash("Login submitted.", "info")
        return redirect(url_for("login"))

    return render_template("signin.html")


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