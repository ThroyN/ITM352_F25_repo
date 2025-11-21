from flask import Flask, render_template, request

app = Flask(__name__)

# Hardcoded users dictionary
USERS = {
    "Throy": "YMCAWarrior",
    "Lebron": "goat"
}

@app.route("/")
def home():
    # this looks in /templates/index.html
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # check user + password
        if USERS.get(username) == password:
            # directly render success page with username
            return render_template("success.html", user=username)
        else:
            error = "Invalid username or password."

    # for GET, or failed POST, show login page (maybe with error)
    return render_template("login.html", error=error)


@app.route("/success")
def success():
    # this route is optional now, only needed if you want to hit /success directly
    return render_template("success.html", user="Guest")


if __name__ == "__main__":
    app.run(debug=True)
