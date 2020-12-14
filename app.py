from flask import (
    Flask,
    render_template,
    url_for,
    redirect,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
    g,
)
from datetime import date
from functools import wraps
from forms import *
from db import *
import os
import random
from werkzeug.utils import secure_filename
import stripe

EMAIL_ID = ""
PINCODE = 0
SOCIETY_EMAIL = ""
SOCIETY_ID = ""
AUTH_ID = ""
PROD_NAME = ""
loggedin_farmer = False
loggedin_society = False
loggedin_auth = False
CART_ID = 0
FARM_ID = ""


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if EMAIL_ID:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("loginpage"))

    return wrap


def login_farmer(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if loggedin_farmer:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("loginpage"))

    return wrap


def login_society(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if loggedin_society:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("loginpage"))

    return wrap


app = Flask(__name__)
app.config["SECRET_KEY"] = "hehhhGWGg"
app.config["UPLOAD_FOLDER"] = "C:\\Users\\asus\\Desktop\\DBD_LAB\\Code\\static\\images"

stripe_keys = {
    "secret_key": "sk_test_51Hqfz1KJ4q9b4uiM1C0dfM2JhW8SkYLJC5rfYpR9MRtwlXmkzmY8F4Wiv03GI5hIIV2t7Xbwt9iKofXwharBMOLp008DdItVO4",
    "publishable_key": "pk_test_51Hqfz1KJ4q9b4uiMjJY1fl9PLecNSeQK4ysJVanRfEKiCi97jTpTvgY3tyGZJXu08DP4Y1z7YZYdiYkkifeeWXNi00rBtMesxj",
}

stripe.api_key = stripe_keys["secret_key"]


@app.route("/logout")
def logout():
    global SOCIETY_EMAIL, SOCIETY_ID, AUTH_ID, EMAIL_ID, loggedin_society, loggedin_farmer, loggedin_auth
    if loggedin_auth:
        EMAIL_ID = ""
        loggedin_auth = False
        flash("logged out succesfully ")
    if loggedin_farmer:
        EMAIL_ID = ""
        loggedin_farmer = False
        flash("logged out succesfully ")
    if loggedin_society:
        EMAIL_ID = ""
        SOCIETY_EMAIL = ""
        loggedin_society = False
        flash("logged out succesfully ")
    return redirect(url_for("loginpage"))


@app.route("/", methods=["GET", "POST"])
def loginpage():
    form = loginForm()
    flag = False
    if form.validate_on_submit():
        print("validated")
        email = form.email.data
        password = form.password.data
        print(email, password)

        # check if farmer
        cur.execute("select email from farmer")
        farmers = [row[0] for row in cur.fetchall()]
        # print(farmers)

        # check if society person
        cur.execute("select email from society")
        society = [row[0] for row in cur.fetchall()]
        print(society)

        # check if govt auth
        cur.execute("select email from govt_authority")
        govt = [row[0] for row in cur.fetchall()]
        global EMAIL_ID, SOCIETY_EMAIL, loggedin_auth, loggedin_farmer, loggedin_society

        if email in farmers:
            flag = True
            cur.execute("select password from farmer where email=%s", (email))
            farm_password = [row[0] for row in cur.fetchall()]
            print(str(farm_password[0]))
            print("he is farmer")
            if password == str(farm_password[0]):
                # global EMAIL_ID, loggedin_farmer
                EMAIL_ID = email
                loggedin_farmer = True
                flash("logged in as " + email)
                return redirect(url_for("farmer"))

        if email in society:
            flag = True
            cur.execute("select password from society where email=%s", (email))
            soc_password = [row[0] for row in cur.fetchall()]
            print("society person password:" + str(soc_password[0]))
            if password == str(soc_password[0]):
                # global SOCIETY_EMAIL, loggedin_society, EMAIL_ID
                EMAIL_ID = email
                SOCIETY_EMAIL = email
                loggedin_society = True
                flash("logged in as " + email)
                return redirect(url_for("society"))

        if email in govt:
            flag = True
            cur.execute("select password from govt_authority where email=%s", (email))
            farm_password = [row[0] for row in cur.fetchall()]
            if password == str(farm_password[0]):
                # global EMAIL_ID, loggedin_auth
                EMAIL_ID = email
                loggedin_auth = True
                flash("logged in as " + email)
                return "<h1> verified govt authority</h1>"

        cur.execute("select email from waiting where email=%s", (email))
        waiting_farm = [row[0] for row in cur.fetchall()]
        if email in waiting_farm:
            cur.execute("select password from waiting where email=%s", (email))
            waiting_pass = [row[0] for row in cur.fetchall()]
            if password == str(waiting_pass[0]):
                cur.execute("select * from waiting where email=%s", (email))
                waiting = cur.fetchall()
                flash("We informed about you to the society just wait.Thank you!!!!!!")
                return render_template("waiting.html", waiting=waiting)

        if flag:
            flash("Wrong password.Try again")
        else:
            flash("Wrong Email and password .Try signing in.")

        return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = signinForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        mob = form.mobile.data
        aadhar = form.aadhar.data
        password = form.password.data
        flag = False
        try:
            print(name, email, mob, password, aadhar)
            global SOCIETY_ID

            cur.execute(
                "insert into waiting(name,email,password,mobile,aadhar,wait,society_id) values(%s,%s,%s,%s,%s,%s,%s)",
                (name, email, password, mob, aadhar, 1, SOCIETY_ID),
            )
            flag = True
        except:
            print("error 121")
            flag = False
        if flag:
            flash("signin succesfull")
            return redirect(url_for("loginpage"))
        else:
            flash("failed to login")
            return render_template("signin.html", form=form)

    return render_template("signin.html", form=form)


@app.route("/fetchSocietyId", methods=["GET", "POST"])
def fetchid():
    if request.method == "POST":
        # print("1111111111111111;fetching id")
        id = request.form["id"]
        global SOCIETY_ID
        SOCIETY_ID = id
        print("s :" + SOCIETY_ID)
        return redirect(url_for("signin"))
    return redirect(url_for("loginpage"))


@app.route("/choosepin", methods=["GET", "POST"])
def choosepin():
    form = pin()
    if form.validate_on_submit():
        print("1")
        pincode = form.pincode.data
        PINCODE = pincode
        cur.execute("select * from society_address where pincode=%s", (pincode))
        societies = cur.fetchall()
        return render_template("choosepin.html", societies=societies, form=form)

    return render_template("choosepin.html", form=form)


# @app.route("/societies",method=['GET','POST'])
# def societies():
#     if request.method=='POST':


@app.route("/society/", methods=["POST", "GET"])
@login_society
def society():
    return render_template("society.html")


@app.route("/farmer/")
@login_farmer
def farmer():
    return render_template("farmer.html")


@app.route("/society/addproduct/", methods=["GET", "POST"])
@login_society
def addproduct():
    # global loggedin_society
    # print(loggedin_society)
    if request.method == "POST":
        try:
            name = request.form["prodname"]
            quantity = request.form["quantity"]
            cost = request.form["cost"]
            prod_type = request.form["prodtype"]
            f = request.files["img"]
            f.save(
                os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename))
            )
            global SOCIETY_EMAIL, SOCIETY_ID
            print("society email:" + SOCIETY_EMAIL)
            cur.execute(
                "select society_id from society where email=%s", (SOCIETY_EMAIL)
            )
            society_id = [row[0] for row in cur.fetchall()]
            SOCIETY_ID = society_id
            print(society_id)
            cur.execute(
                "select auth_id from society_govtauthority where society_id=%s",
                (society_id),
            )
            auth_id = [row[0] for row in cur.fetchall()]
            print(society_id, auth_id)

            cur.execute(
                "insert into products(quantity_avail,cost,product_type,society_id,auth_id,img_path,prod_name) values(%s,%s,%s,%s,%s,%s,%s)",
                (
                    quantity,
                    cost,
                    prod_type,
                    society_id,
                    auth_id,
                    secure_filename(f.filename),
                    name,
                ),
            )
            flash("product " + name + " added succesfully")
            return redirect(url_for("society"))
        except:
            flash("failed to add product! Try again")
            return redirect(url_for("society"))

    return render_template("addprod.html")


@app.route("/society/removeproduct/", methods=["GET", "POST"])
@login_society
def removeprod():
    global SOCIETY_EMAIL
    print("society email:" + SOCIETY_EMAIL)
    cur.execute("select society_id from society where email=%s", (SOCIETY_EMAIL))
    society_id = [row[0] for row in cur.fetchall()]
    global SOCIETY_ID
    SOCIETY_ID = society_id

    cur.execute("select prod_name from products where society_id=%s ", (SOCIETY_ID))
    products = [row[0] for row in cur.fetchall()]
    if request.method == "POST":
        prod_name = request.form["prodtype"]
        cur.execute("delete from products where prod_name=%s ", (prod_name))
        flash("product removed succesfully")
        return redirect(url_for("removeprod"))
    return render_template("removeprod.html", products=products)


@app.route("/society/updateproduct/", methods=["GET", "POST"])
@login_society
def updateproduct():
    global SOCIETY_EMAIL
    print("society email:" + SOCIETY_EMAIL)
    cur.execute("select society_id from society where email=%s", (SOCIETY_EMAIL))
    society_id = [row[0] for row in cur.fetchall()]
    global SOCIETY_ID
    SOCIETY_ID = society_id

    cur.execute("select prod_name from products where society_id=%s ", (SOCIETY_ID))
    products = [row[0] for row in cur.fetchall()]
    if request.method == "POST":
        prod_name = request.form["prodtype"]
        cur.execute("select * from products where prod_name=%s ", (prod_name))
        prod = cur.fetchall()
        global PROD_NAME
        PROD_NAME = prod_name
        return render_template("update.html", products=prod)
    return render_template("selectprod.html", products=products)


@app.route("/society/updateprod/", methods=["GET", "POST"])
@login_society
def updateprod():
    if request.method == "POST":
        try:
            name = request.form["prodname"]
            quantity = request.form["quantity"]
            cost = request.form["cost"]
            prod_type = request.form["prodtype"]
            f = request.files["img"]
            f.save(
                os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename))
            )
            global SOCIETY_EMAIL, SOCIETY_ID
            print("society email:" + SOCIETY_EMAIL)
            cur.execute(
                "select society_id from society where email=%s", (SOCIETY_EMAIL)
            )
            society_id = [row[0] for row in cur.fetchall()]
            SOCIETY_ID = society_id
            print(society_id)
            cur.execute(
                "select auth_id from society_govtauthority where society_id=%s",
                (society_id),
            )
            auth_id = [row[0] for row in cur.fetchall()]
            print(society_id, auth_id)

            cur.execute(
                "update products set quantity_avail=%s,cost=%s,product_type=%s,society_id=%s,auth_id=%s,img_path=%s,prod_name=%s where prod_name=%s",
                (
                    quantity,
                    cost,
                    prod_type,
                    society_id,
                    auth_id,
                    secure_filename(f.filename),
                    name,
                    PROD_NAME,
                ),
            )
            flash("product " + name + " updated succesfully")
            return redirect(url_for("society"))
        except:
            flash("failed to update product! Try again")
            return redirect(url_for("society"))

    return render_template("addprod.html")


@app.route("/society/requests/", methods=["POST", "GET"])
@login_society
def requests():
    global SOCIETY_EMAIL
    cur.execute("select society_id from society where email=%s", (SOCIETY_EMAIL))
    society_id = [row[0] for row in cur.fetchall()]
    global SOCIETY_ID
    SOCIETY_ID = society_id

    cur.execute(
        "select * from waiting where society_id=%s and wait=%s", (society_id, "1")
    )
    persons = cur.fetchall()
    if request.method == "POST":
        aadhar = request.form["aadhar"]
        print("aadhar:" + aadhar)
        cur.execute("select * from waiting where aadhar=%s", (aadhar))
        person = cur.fetchone()
        print(person)
        cur.execute(
            "insert into farmer(name,email,password,mobile,aadhar) values(%s,%s,%s,%s,%s) ",
            (person[1], person[2], person[3], person[4], person[5]),
        )
        flash("verified ")
        cur.execute("update waiting set wait=%s where aadhar=%s", (0, aadhar))
        cur.execute("insert into cart value(%s)", (person[0]))

        cur.execute("select farmer_id from farmer where email=%s", (person[2]))
        farmer_id = [row[0] for row in cur.fetchall()]
        # insert into farm_cart
        cur.execute("insert into farmer_cart values(%s,%s) ", (farmer_id, person[0]))
        return redirect(url_for("society"))

    return render_template("request.html", persons=persons)


@app.route("/society/viewproduct/", methods=["POST", "GET"])
@login_society
def viewprod():
    global SOCIETY_EMAIL, SOCIETY_ID
    print("society email:" + SOCIETY_EMAIL)
    cur.execute("select society_id from society where email=%s", (SOCIETY_EMAIL))
    society_id = [row[0] for row in cur.fetchall()]
    SOCIETY_ID = society_id
    print(society_id)
    cur.execute(
        "select auth_id from society_govtauthority where society_id=%s",
        (society_id),
    )
    auth_id = [row[0] for row in cur.fetchall()]
    # fetch all products
    cur.execute("select * from products where society_id=%s", (society_id))
    products = cur.fetchall()
    return render_template("viewSocietyprod.html", products=products)


@app.route("/farmer/products/", methods=["GET", "POST"])
@login_farmer
def products():
    global SOCIETY_EMAIL, EMAIL_ID, SOCIETY_ID
    # society_id to farmer_id mapping only in waiting
    cur.execute(
        "select society_id from waiting where email=%s and wait=%s", (EMAIL_ID, 0)
    )
    society_id = [row[0] for row in cur.fetchall()]
    SOCIETY_ID = society_id
    # fetch all products
    cur.execute("select * from products where society_id=%s", (society_id))
    products = cur.fetchall()
    return render_template("viewfarmerprod.html", products=products)


@app.route("/farmer/viewprofile/", methods=["GET", "POST"])
@login_farmer
def viewprofile():
    global EMAIL_ID
    cur.execute("select * from farmer where email=%s", (EMAIL_ID))
    farmers = cur.fetchall()
    return render_template("viewprofile.html", farmers=farmers)


@app.route("/farmer/updateprofile/", methods=["GET", "POST"])
@login_farmer
def updateprofile():
    global EMAIL_ID
    cur.execute("select * from farmer where email=%s", (EMAIL_ID))
    farmers = cur.fetchall()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        mob = request.form["mobile"]
        try:
            cur.execute(
                "update farmer set name=%s,email=%s,mobile=%s where email=%s",
                (name, email, mob, EMAIL_ID),
            )
            global SOCIETY_ID
            cur.execute(
                "update waiting set name=%s,email=%s,mobile=%s where email=%s",
                (name, email, mob, EMAIL_ID),
            )
            EMAIL_ID = email
            flash("updated succesfully")
        except:
            flash("failed to update. Try again!!!")
        finally:
            return redirect(url_for("farmer"))
    return render_template("updateprofile.html", farmers=farmers)


@app.route("/farmer/addtocart", methods=["GET", "POST"])
@login_farmer
def addtocart():
    global EMAIL_ID
    # get farmer id
    cur.execute("select farmer_id from farmer where email=%s", (EMAIL_ID))
    farmer_id = [row[0] for row in cur.fetchall()]
    # get cart_id from farm_cart
    cur.execute("select cart_id from farmer_cart where farmer_id=%s", (farmer_id))
    cart_id = [row[0] for row in cur.fetchall()]
    if request.method == "POST":
        prod_id = request.form["id"]
        purchased = 0
        quantity = request.form["reqqnt"]
        date_added = date.today()
        cartid = cart_id
        cur.execute(
            "insert into cart_items( purchased, quantity, date_added, cart_id, prod_id) values(%s,%s,%s,%s,%s)",
            (purchased, quantity, date_added, cartid, prod_id),
        )
        flash("product added to cart succesfully")
        global CART_ID
        CART_ID = cartid
        return redirect(url_for("cart"))


@app.route("/farmer/cart/")
@login_farmer
def cart():
    global CART_ID
    # cart_id = CART_ID
    global EMAIL_ID
    # get farmer id
    cur.execute("select farmer_id from farmer where email=%s", (EMAIL_ID))
    farmer_id = [row[0] for row in cur.fetchall()]
    global FARM_ID
    FARM_ID = farmer_id
    # get cart_id from farm_cart
    cur.execute("select cart_id from farmer_cart where farmer_id=%s", (farmer_id))
    cart_id = [row[0] for row in cur.fetchall()]
    CART_ID = cart_id

    # cur.execute(
    #     "select prod_id from cart_items where cart_id=%s and purchased=%s", (cart_id, 0)
    # )
    # prod_id=[row[0] for row in cur.fetchall()]
    # cur.execute(
    #     "select * from cart_items where cart_id=%s and purchased=%s", (cart_id, 0)
    # )
    # join cart_items and products
    cur.execute(
        "select * from products p,cart_items c where p.product_id=c.prod_id and c.cart_id=%s and c.purchased=%s group by p.product_id",
        (cart_id, 0),
    )
    cart_products = cur.fetchall()
    # print(cart_id)
    # for product in cart_products:
    #     print(products)
    cur.execute(
        "select count(*) from products p,cart_items c where p.product_id=c.prod_id and c.cart_id=%s and c.purchased=%s group by p.product_id",
        (cart_id, 0),
    )
    prod_quantity = [row[0] for row in cur.fetchall()]
    return render_template("cart.html", products=cart_products, quantity=prod_quantity)


AMOUNT = 0
QUANTITY = 0
PRODUCT_ID = 0


@app.route("/farmer/payment/", methods=["GET", "POST"])
@login_farmer
def payment():
    if request.method == "POST":
        global AMOUNT, QUANTITY, PRODUCT_ID
        id = request.form["id"]
        name = request.form["name"]
        qnt = request.form["qnt"]
        cost = request.form["cost"]
        type = request.form["type"]
        total_cost = int(qnt) * int(cost)
        AMOUNT = total_cost
        QUANTITY = qnt
        PRODUCT_ID = id
        return render_template("payment_index.html", totalcost=total_cost)


@app.route("/farmer/checkout", methods=["GET", "POST"])
@login_farmer
def checkout():
    global AMOUNT, FARM_ID, CART_ID, QUANTITY, PRODUCT_ID, EMAIL_ID
    amount = AMOUNT

    cur.execute(
        "insert into payment(pay_date,amount,farm_id,cart_id) values(%s,%s,%s,%s)",
        (date.today(), AMOUNT, FARM_ID, CART_ID),
    )

    cur.execute(
        "update products set quantity_avail=quantity_avail-%s where product_id=%s ",
        (QUANTITY, PRODUCT_ID),
    )
    cur.execute("update cart_items set purchased=%s where prod_id=%s", (1, PRODUCT_ID))
    flash("payment succesfull")
    return render_template("checkout.html", amount=amount)


@app.route("/farmer/history/", methods=["GET", "POST"])
@login_farmer
def farmer_history():
    global CART_ID
    # cart_id = CART_ID
    global EMAIL_ID
    # get farmer id
    cur.execute("select farmer_id from farmer where email=%s", (EMAIL_ID))
    farmer_id = [row[0] for row in cur.fetchall()]
    global FARM_ID
    FARM_ID = farmer_id
    # get cart_id from farm_cart
    cur.execute("select cart_id from farmer_cart where farmer_id=%s", (farmer_id))
    cart_id = [row[0] for row in cur.fetchall()]
    CART_ID = cart_id

    # join cart_items and products
    cur.execute(
        "select * from products p,cart_items c where p.product_id=c.prod_id and c.cart_id=%s and c.purchased=%s group by p.product_id",
        (cart_id, 1),
    )
    cart_products = cur.fetchall()
    # print(cart_id)
    # for product in cart_products:
    #     print(products)
    cur.execute(
        "select count(*) from products p,cart_items c where p.product_id=c.prod_id and c.cart_id=%s and c.purchased=%s group by p.product_id",
        (cart_id, 1),
    )
    prod_quantity = [row[0] for row in cur.fetchall()]
    return render_template(
        "history.html", products=cart_products, quantity=prod_quantity
    )


# society 1 case
# delete user account


# govt_auth 3 cases
# view product
# society members
# sales report

# analytics in Home page


if __name__ == "__main__":
    app.run(debug=True)
