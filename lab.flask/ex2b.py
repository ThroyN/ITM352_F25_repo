from flask import Flask, render_template, request

app = Flask(__name__)

# Hard-coded users
USERS = {
    "Throy": "YMC4Warrior",
    "Lebron": "goat"
}

@app.route("/")
def home():
    # loads templates/index.html
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in USERS and USERS[username] == password:
            return render_template("success.html", user=username)
        else:
            return render_template("login.html", error="Invalid username or password")

    # GET request
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
