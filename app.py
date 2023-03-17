import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
#    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    id = session["user_id"]
    shares = db.execute("SELECT * FROM shares WHERE user_id=?", id)
    cash = db.execute("SELECT cash FROM users WHERE id=?", id)

    return render_template("index.html", shares=shares, cash=cash[0])



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        sharesamount = request.form.get("shares")
        if not sharesamount.isnumeric():
            return apology("Invalid Shares amount", 400)

        symbolname = request.form.get("symbol")
        sharesamount = float(sharesamount)
        symboldict = lookup(symbolname)

        if not symboldict:
            return apology("Invalid Symbol", 400)

        if sharesamount<=0:
            return apology("Invalid Shares amount", 400)

        if not (sharesamount - int(sharesamount) == 0):
            return apology("Invalid Shares amount", 400)


        name = symboldict["name"]
        price = symboldict["price"]
        symbol = symboldict["symbol"]
        id = session["user_id"]

        cash = db.execute("SELECT cash FROM users WHERE id=?", id)

        check = db.execute("SELECT * FROM shares WHERE symbol =? AND user_id=?", symbol, id)
        newcash = cash[0]["cash"] - (sharesamount*float(price))

        if newcash < 0:
            return apology("Insufficient funds to buy shares", 403)

        if not check:
            db.execute("UPDATE users SET cash=? WHERE id=?", newcash, id)
            db.execute("INSERT INTO shares (user_id,name,price,symbol,amount) VALUES (?,?,?,?,?)",id, name, price, symbol, sharesamount)
        else:
            db.execute("UPDATE users SET cash=? WHERE id=?", newcash, id)
            oldshares = db.execute("SELECT amount FROM shares WHERE symbol=? AND user_id=?", symbol, id)
            totalshares = sharesamount + oldshares[0]["amount"]
            db.execute("UPDATE shares SET amount=? WHERE symbol=? AND user_id=?", totalshares, symbol, id)

        return redirect("/")

    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    id = session["user_id"]
    shares = db.execute("SELECT * FROM shares WHERE user_id=?", id)

    return render_template("history.html", shares=shares)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbolname = request.form.get("symbol")
        symbol = lookup(symbolname)

        if symbol:
            price = usd(symbol["price"])
            return render_template("quoted.html", symbol = symbol, price = price)
        else:
            return apology("Invalid Symbol", 400)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        session.clear()
        usernamecheck = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if not request.form.get("username"):
            return apology("Must provide username", 400)
        elif len(usernamecheck) > 0:
            return apology("Username already taken", 400)
        elif (request.form.get("confirmation") != request.form.get("password")) or (not request.form.get("password")):
            return apology("Passwords do not match or invalid blank password", 400)


        #Password security check

        password = request.form.get("password")

        if len(password)<8:
            return apology("Password length must be atleast 8 characters long", 400)

        special_characters = "!@#$%^&*()-+?_=,<>/"
        d=0
        a=0
        s=0
        for i in range(len(password)):
            if password[i].isdigit():
                d=d+1

            elif password[i].isalpha():
                a=a+1

            elif any(c in special_characters for c in password[i]):
                s=s+1

        if d==0 or a==0 or s==0:
            return apology("Password must include a number and a special character", 403)

        #Password security check


        passwordhash = generate_password_hash(request.form.get("password"))
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), passwordhash )
        usernamerow = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = usernamerow[0]["id"]
        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    id = session["user_id"]

    if request.method == "POST":
        symbol = request.form.get("symbol")
        sharesamount = int(request.form.get("shares"))

        if not symbol:
            return apology("Please select a stock", 403)

        checksymbol = db.execute("SELECT symbol FROM shares WHERE symbol =? AND user_id=?", symbol, id)
        if not checksymbol:
            return apology("You do not own that stock", 403)

        if sharesamount<0:
            return apology("Invalid amount of shares", 400)

        checkamount = db.execute("SELECT amount FROM shares WHERE symbol =? AND user_id=?", symbol, id)
        amountowned = checkamount[0]["amount"]
        if amountowned<sharesamount:
            return apology("You don't own that many shares", 400)
        else:
            newamount = amountowned - sharesamount
            symboldict = lookup(symbol)
            price = float(symboldict["price"])
            addedcash = price*sharesamount

            x = db.execute("SELECT cash FROM users WHERE id=?", id)
            oldcash = x[0]["cash"]
            newcash = oldcash + addedcash

            db.execute("UPDATE users SET cash=? WHERE id=?", newcash, id)
            db.execute("UPDATE shares SET amount=? WHERE symbol=? AND user_id=?", newamount, symbol, id)

        return redirect("/")

    else:
        symbols = db.execute("SELECT symbol FROM shares WHERE user_id=?", id)
        return render_template("sell.html", symbols=symbols)


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """Change user pass"""
    if request.method == "POST":

        newpass = request.form.get("password")
        confirm = request.form.get("confirmation")
        id = session["user_id"]

        if (confirm != newpass) or (not request.form.get("password")):
            return apology("Passwords do not match or invalid blank password", 400)

        #Password security check

        if len(newpass)<8:
            return apology("Password length must be atleast 8 characters long", 400)

        special_characters = "!@#$%^&*()-+?_=,<>/"
        d=0
        a=0
        s=0
        for i in range(len(newpass)):
            if newpass[i].isdigit():
                d=d+1

            elif newpass[i].isalpha():
                a=a+1

            elif any(c in special_characters for c in newpass[i]):
                s=s+1

        if d==0 or a==0 or s==0:
            return apology("Password must include a number and a special character", 403)

        #Password security check

        passwordhash = generate_password_hash(request.form.get("password"))
        db.execute("UPDATE users SET hash=? WHERE id=?", passwordhash, id)

        return redirect("/")

    else:
        return render_template("changepass.html")