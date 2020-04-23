import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask import jsonify
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Ensure environment variable is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_stocks_list = db.execute("SELECT stock FROM transactions WHERE id = :current_id", current_id=session["user_id"])
    user_stocks = []
    for stock in user_stocks_list:
        if stock['stock'] not in user_stocks:
            user_stocks.append(stock['stock'])

    stock_portfolio = []

    for possible_stock in user_stocks:
        bought_shares_list = db.execute("SELECT SUM(units) FROM transactions WHERE (id = :current_id AND stock = :stock AND type = :t)",
                                        current_id=session["user_id"], stock=possible_stock, t='B')
        bought_shares = 0
        bought_shares = bought_shares_list[0]["SUM(units)"]
        sold_shares_list = db.execute("SELECT SUM(units) FROM transactions WHERE (id = :current_id AND stock = :stock AND type = :t)",
                                      current_id=session["user_id"], stock=possible_stock, t='S')
        sold_shares = 0
        sold_shares = sold_shares_list[0]["SUM(units)"]
        if sold_shares == None:
            sold_shares = 0

        available_shares = 0
        if bought_shares != None and (bought_shares - sold_shares) > 0:
            available_shares = bought_shares - sold_shares
            current_price = int(lookup(possible_stock)["price"])
            market_value = current_price * available_shares
            dict_stock = {}
            dict_stock['name_stock'] = possible_stock
            dict_stock['shares_quantity'] = available_shares
            dict_stock['current_price'] = current_price
            dict_stock['market_value'] = market_value
            stock_portfolio.append(dict_stock)
        else:
            pass

    available_money_list = db.execute("SELECT cash FROM users WHERE id = :current_id", current_id=session["user_id"])
    available_money = usd(available_money_list[0]['cash'])

    username_list = db.execute("SELECT username FROM users WHERE id = :current_id", current_id=session["user_id"])
    username = username_list[0]["username"]

    sum_market_values = 0
    for collection in stock_portfolio:
        sum_market_values += int(collection['market_value'])

    total_value = usd(available_money_list[0]['cash'] + sum_market_values)

    return render_template("index.html", stock_portfolio=stock_portfolio, user_stocks=user_stocks, money=available_money, name=username, total_value=total_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        if not request.form.get("shares"):
            return apology("gimme share", 400)
        if not lookup(request.form.get("symbol")):
            return apology("not correct stock", 400)
        if not request.form.get("shares").isdigit():
            return apology("sorry bro", 400)

        quote = lookup(request.form.get("symbol"))

        money_list = db.execute("SELECT cash FROM users WHERE id = :current_id", current_id=session["user_id"])
        available_money = money_list[0]["cash"]

        total_price = int(request.form.get("shares")) * float(quote["price"])

        if available_money < total_price:
            return apology("no money bro", 400)

        insertion = db.execute("INSERT INTO transactions (id, stock, units, price, time, type) VALUES (:current_id, :stock, :units, :price, :now, :type)",
                               current_id=session["user_id"], stock=request.form.get("symbol"), units=request.form.get("shares"), price=float(quote["price"]), now=datetime.datetime.now(), type="B")
        updating = db.execute("UPDATE users SET cash = cash - :upd_price WHERE id = :current_id",
                              upd_price=total_price, current_id=session["user_id"])

        money_upd_list = db.execute("SELECT cash FROM users WHERE id = :current_id", current_id=session["user_id"])
        available_money_upd = money_upd_list[0]["cash"]

        return render_template("buy_result.html",
                               shares=request.form.get("shares"),
                               symbol=request.form.get("symbol"),
                               price=usd(total_price),
                               cash=usd(available_money_upd))
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions_list = db.execute("SELECT stock, units, price, time, type FROM transactions WHERE id = :current_id",
                                   current_id=session["user_id"])

    return render_template("history.html", transactions=transactions_list)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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

# Andrey Tymofeiuk: Implemented by me
@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if request.method == "POST":

        if not request.form.get("new_password"):
            return apology("must provide password", 400)

        elif not request.form.get("new_password_confirmation"):
            return apology("must confirm new password", 400)

        elif request.form.get("new_password_confirmation") != request.form.get("new_password"):
            return apology("give proper new password please", 400)

        hashedNewPassword = generate_password_hash(request.form.get("new_password"))

        update = db.execute("UPDATE users SET hash = :new_hash WHERE id = :current_id",
                            new_hash=hashedNewPassword, current_id=session["user_id"])

        return render_template("change_password_result.html")
    else:
        return render_template("change_password.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("must provide stock", 400)

        quote = lookup(request.form.get("symbol"))
        if not lookup(request.form.get("symbol")):
            return apology("not correct stock", 400)

        return render_template("quote_result.html", stock=quote["symbol"], price=usd(quote["price"]))

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("give proper password please", 400)

        existingUsers = db.execute("SELECT username FROM users")
        for element in existingUsers:
            if request.form.get("username") in element["username"]:
                return apology("user exists", 400)

        hashedPassword = generate_password_hash(request.form.get("password"))

        insertion = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                               username=request.form.get("username"), hash=hashedPassword)

        selection = db.execute("SELECT * FROM users WHERE username == :checkUser", checkUser=request.form.get("username"))

        session["user_id"] = selection[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        if not request.form.get("shares"):
            return apology("gimme share", 400)
        if not lookup(request.form.get("symbol")):
            return apology("not correct stock", 400)
        if not request.form.get("shares").isdigit():
            return apology("sorry bro", 400)

        quote = lookup(request.form.get("symbol"))

        money_list = db.execute("SELECT cash FROM users WHERE id = :current_id", current_id=session["user_id"])
        available_money = money_list[0]["cash"]

        total_price = int(request.form.get("shares")) * float(quote["price"])

        units_list = db.execute("SELECT SUM(units) FROM transactions WHERE id = :current_id AND stock = :stock_code",
                                current_id=session["user_id"], stock_code=request.form.get("symbol"))
        available_units = units_list[0]["SUM(units)"]

        if available_units < int(request.form.get("shares")):
            return apology("no units bro", 400)

        new_cash = available_money + total_price

        updating = db.execute("UPDATE users SET cash = :upd_cash WHERE id = :current_id",
                              upd_cash=new_cash, current_id=session["user_id"])
        insertion = db.execute("INSERT INTO transactions (id, stock, units, price, time, type) VALUES (:current_id, :stock, :units, :price, :now, :type)",
                               current_id=session["user_id"], stock=request.form.get("symbol"), units=request.form.get("shares"), price=float(quote["price"]), now=datetime.datetime.now(), type="S")

        money_upd_list = db.execute("SELECT cash FROM users WHERE id = :current_id", current_id=session["user_id"])
        available_money_upd = money_upd_list[0]["cash"]

        return render_template("sell_result.html", shares=request.form.get("shares"),
                               symbol=request.form.get("symbol"),
                               price=usd(total_price),
                               cash=usd(new_cash))
    else:
        available_stocks_info = db.execute("SELECT stock FROM transactions WHERE id = :current_id", current_id=session["user_id"])
        available_stocks_list = []
        for element in available_stocks_info:
            if element["stock"] not in available_stocks_list:
                available_stocks_list.append(element["stock"])

        return render_template("sell.html", available_stocks=available_stocks_list)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)