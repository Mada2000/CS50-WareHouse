from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
import os
from flask_session import Session
from werkzeug.utils import secure_filename


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# the source code for uploading the image ("https://tutorial101.blogspot.com/2021/04/python-flask-upload-and-display-image.html")
UPLOAD_FOLDER = 'static/uploads/'
db = SQL("sqlite:///products.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
Session(app)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

@app.route("/")
def index():

    #check if user is logged in
    if not session.get("name"):
        return redirect("login")

    # load the database into a dictionary and pass it
    products = db.execute("SELECT * FROM product")
    return render_template("index.html", products=products)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget user
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        admin = "admin"
        # Ensure username was submitted
        if request.form.get("name") != "admin":
            return render_template("fail.html")

        # Ensure password was submitted
        elif request.form.get("password") != "admin":
            return render_template("fail.html")

        # Remember that user has logged in
        session["name"] = admin

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

#check the file format
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/add", methods=["GET", "POST"])
def add():

    # if not logged in redirect to login page
    if not session.get("name"):
        return redirect("login")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure info was submitted
        if not request.form.get("n") or not request.form.get("q") or not request.form.get("p"):
            return render_template("fail.html")

        file = request.files['file']

        #check if file is submitted
        if file.filename == '':
            return render_template("fail.html")

        #if file in allowed format and submitted insert to database and upload it to the server
        if file and allowed_file(file.filename):
            db.execute("INSERT INTO product (img, name, price, quantity) VALUES(?, ?, ?, ?)", "/static/uploads/" + file.filename, request.form.get("n"), request.form.get("p"), request.form.get("q"))
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect("/")

        # Redirect user to home page
        return redirect("/")

     # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add.html")


@app.route("/delete", methods=["POST"])

def delete():

    # get the id of the product in the database
    id = request.form.get("id")

    # delete the product from the database
    if id:
        db.execute("DELETE FROM product WHERE id = ?", id)

    return redirect("/")

@app.route("/edit", methods=["GET", "POST"])

def edit():

    #get the id of the product
    id = request.args.get("id")

    #check if form is submitted
    if request.method == "POST":

        #check for errors
        if not request.form.get("n") or not request.form.get("q") or not request.form.get("p"):
            return render_template("fail.html")

        # update database with the new data
        db.execute("UPDATE product SET name = ?,  price = ?,  quantity = ? WHERE  id = ?", request.form.get("n"), request.form.get("p"), request.form.get("q"), request.form.get("id"))
        return redirect("/")

    else:
        #get the product data to be a placeholder
        product = db.execute("SELECT * FROM product WHERE id = ?", id)
        return render_template("edit.html", product=product)


@app.route("/logout")

def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

