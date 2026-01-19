from flask import Flask, render_template, session, redirect, url_for, g, request
from forms import RegistrationFrom, AddNewItem, LoginFrom, DeleteItem, UpdateItem, Update2, DeleteCartForm, AddCartForm, SearchForm
from forms import ChangePasswordForm, ChangeEmailForm, SuggestForm, SaleForm
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
from functools import wraps
import datetime
import os

"""
There are two accounts, one that is a client and one that is an admin, 
the client has a username: njds1 and a password: nathan0303
the admin has a username: admin and a password: 12345678
"""



app = Flask(__name__)
app.config["SECRET_KEY"] = 'this-is-the-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.teardown_appcontext(close_db)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
@app.before_request
def load_logged_in_user():
    g.user_id = session.get("user_id", None)

@app.before_request
def is_admin():
    if g.user_id == "admin":
        g.is_admin = True


sale = []
def check_sale():
    inFile = open("sale.txt", "r")
    for line in inFile:
        line = line.strip()
        sale.append(line + ", ")
    inFile.close()
check_sale()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user_id is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/")
def index():
    return render_template("index.html", title="Home", sale=sale)


#___________________________________________________________________________________________#
#User login#
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationFrom()
    if form.validate_on_submit():
        db = get_db()
        user_id = form.user_id.data
        password = form.password.data
        email_address = form.email_address.data

        clash = db.execute("""SELECT *
                           FROM users
                           WHERE user_id = ?""", (user_id, )).fetchone()
        if clash is not None:
            form.user_id.errors.append("The id is already in use")
        else:
            db.execute("""INSERT INTO users (user_id, password, email_address)
                       VALUES (?, ?, ?)""", (user_id, generate_password_hash(password), email_address))
            db.commit()
            return redirect(url_for("login"))
    return render_template("registration.html", title="Registration", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginFrom()
    if form.validate_on_submit():
        db = get_db()
        user_id = form.user_id.data
        password = form.password.data
        user_id_check = db.execute("""SELECT *
                                   FROM users
                                   WHERE user_id = ?""", (user_id, )).fetchone()
        if user_id_check is None:
            form.user_id.errors.append("User Id not registered")
        elif not check_password_hash( user_id_check["password"], password):
            form.password.errors.append("The password is incorrect")
        else:
            session.clear()
            session["user_id"] = user_id
            session.modified = True
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login.html", form=form, title="Login")

@app.route("/logout")
def logout():
    session.clear()
    session.modified = True
    return redirect( url_for("index") )


#________________________________________________________________________________________#
@app.route("/admin_account")
@login_required
def admin_account():
    num_purchases_per_day = None
    suggestions = None
    users = None
    db = get_db()
    num_purchases_per_day = db.execute("""SELECT COUNT(*) AS 'Total Purchases', time
                            FROM prev_purchases
                            WHERE time >= DATE('now', '-7 days')
                            GROUP BY time
                            ORDER BY time DESC
                            LIMIT 7;""").fetchall()
    #https://www.sqlite.org/lang_datefunc.html and https://stackoverflow.com/questions/17717515/how-to-query-for-todays-date-and-7-days-before-data to get the dates for the week
    
    most_popular_items = db.execute("""SELECT SUM(num_of_items) AS 'total_number_purchased', name
                                    FROM prev_purchases
                                    GROUP BY name
                                    ORDER BY total_number_purchased DESC
                                    LIMIT 20;""").fetchall()
    suggestions = db.execute("""SELECT *
                             FROM suggestions;""").fetchall()
    
    
    users = db.execute("""SELECT *
                       FROM users
                       WHERE user_id <> "admin";""").fetchall()
    return render_template("admin_acc.html", title="Admin Account", num_purchases_per_day=num_purchases_per_day, suggestions=suggestions, users=users, most_popular_items=most_popular_items)

@app.route("/remove_user/<user_id>")
def remove_user(user_id):
    db = get_db()
    db.execute("""DELETE
               FROM users
               WHERE user_id = ?""", (user_id, ))
    db.commit()
    return redirect(url_for('admin_account'))

@app.route("/account")
@login_required
def account():
    prev_purchases = None
    change_password_form = ChangePasswordForm()
    change_email_form = ChangeEmailForm()
    db= get_db()
    prev_purchases = db.execute("""SELECT *
                                FROM prev_purchases
                                WHERE user_id = ?
                                ORDER BY time DESC;""", (g.user_id, )).fetchall()
    return render_template("user_acc.html", title="User Account", form=change_password_form, form2=change_email_form, prev_purchases=prev_purchases)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    db = get_db()
    prev_purchases = None
    prev_purchases = get_prev_purchases_user(g.user_id)
    if form.validate_on_submit():
        check_password = form.check_password.data
        new_password = form.new_password.data

        check = db.execute("""SELECT password
                           FROM users
                           WHERE user_id = ?;""", (g.user_id, )).fetchone()
        
        if not check_password_hash( check["password"], check_password):
            form.check_password.errors.append("Incorrect Password")
            return render_template("user_acc.html", title="User Account", form=form, form2=ChangeEmailForm(), prev_purchases=prev_purchases)
        else:
            db.execute("""UPDATE users
                       SET password = ?
                       WHERE user_id = ?;""", (generate_password_hash(new_password), g.user_id))
            db.commit()   
        return redirect( url_for("account"))
    return render_template("user_acc.html", title="User Account", form=form, form2=ChangeEmailForm(), prev_purchases=prev_purchases)

@app.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email():
    db=get_db()
    form = ChangeEmailForm()
    prev_purchases = None
    prev_purchases = get_prev_purchases_user(g.user_id)
    if form.validate_on_submit():

        check_email = form.change_email.data
        db.execute("""UPDATE users
                   SET email_address = ?
                   WHERE user_id = ?;""", (check_email, g.user_id))
        db.commit()
        return redirect( url_for("account"))
    return render_template("user_acc.html", title="User Account", form=ChangePasswordForm(), form2=form, prev_purchases=prev_purchases)

def get_prev_purchases_user(user_id):
    db = get_db()
    return db.execute("""SELECT *
                      FROM prev_purchases
                      WHERE user_id = ?
                      ORDER BY time DESC;""", (user_id, )).fetchall()



@app.route("/suggestion", methods=["GET", "POST"])
@login_required
def suggestion():
    form = SuggestForm()
    message = ""
    if form.validate_on_submit():
        suggestion = form.suggestion.data
        db = get_db()
        db.execute("""INSERT INTO suggestions
                   VALUES (?, ?);""", (g.user_id, suggestion))
        db.commit()
        message = "Successfully Submitted"
    return render_template("suggestion.html", title="Suggestion", form=form, message=message)

@app.route("/remove_suggestion/<suggestion>")
def remove_suggestion(suggestion):
    db=get_db()
    db.execute("""DELETE 
               FROM suggestions
               WHERE suggestion = ?;""", (suggestion, ))
    db.commit()
    return redirect(url_for("admin_account"))

#___________________________________________________________________________________________#


#___________________________________________________________________________________________#
#Website Maintenance#


@app.route("/insert_item", methods=["GET", "POST"])
def insert_item():
    form = AddNewItem()
    message = ""
    global sale
    if form.validate_on_submit():

        db = get_db()
        name = form.name.data
        desc = form.desc.data
        num_available = form.num_available.data
        price = form.price.data  
        price = float(price)
        file = form.file.data

        
        clash = db.execute("""SELECT * 
                           FROM stock 
                           WHERE name = ?;""", (name,)).fetchone()
        if clash:
            message = "Item is already in the stock"
        else:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)


            db.execute("""INSERT INTO stock (name, desc, num_available, price, image_filename) 
                        VALUES (?, ?, ?, ?, ?);""", (name, desc, num_available, price, filename))
            db.commit()
            file.save(filepath)
            message = "Successfully Inputted Item and File"

            #file storing form https://stackoverflow.com/questions/79035327/how-to-use-images-uploaded-from-a-html-web-page-using-python-flask

        return render_template("insert_item.html", title="Insert New Item", form=form, message=message, sale=sale)

    return render_template("insert_item.html", title="Insert New Item", form=form,message=message, sale=sale)
             



@app.route("/update_item", methods=["GET", "POST"])
def update_item():
    global sale
    form = UpdateItem()
    form2 = Update2()
    check = False
    prod_id_check = None
    message = ""
    name_check = False
    desc_check = False
    num_available_check = False
    price_check = False
    prod_id = None
    db= get_db()
    items = db.execute("""SELECT *
                       FROM stock""").fetchall()
    if form.validate_on_submit():
        prod_id = form.prod_id.data
        prod_id_check = db.execute("""SELECT *
                    FROM stock
                    WHERE prod_id = ?;""", (prod_id, )).fetchone()
        if prod_id_check is None:
            form.prod_id.errors.append("Product Id is not avalible")
        else:
            name_check = form.name_check.data
            desc_check = form.desc_check.data
            num_available_check = form.num_available_check.data
            price_check = form.price_check.data  
            check = True

            if (not name_check and not desc_check and not num_available_check and not price_check):
                check = False
                message = "At least one item is needed"
    return render_template("update_item.html", title="Update item", prod_id=prod_id, check=check, name_check=name_check, desc_check=desc_check, num_available_check=num_available_check,
                        price_check=price_check, form=form, form2=form2, message=message, items=items, sale=sale)

@app.route("/update2/<int:prod_id>", methods=["POST"])
def update2(prod_id):
    db = get_db()
    form2 = Update2()

    if form2.validate_on_submit():
        name = form2.name.data
        desc = form2.desc.data
        num_available = form2.num_available.data
        price = form2.price.data
        if price is not None:
            price = float(price)  
        #-----------------------------------------------------------#
        if name and desc and num_available and price: 
            db.execute("""UPDATE stock
                        SET name = ?, desc = ?, num_available = ?, price = ? 
                        WHERE prod_id = ?;""", (name, desc, num_available, price, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif name and desc and num_available and not price:
            db.execute("""UPDATE stock
                        SET name = ?, desc = ?, num_available = ? 
                        WHERE prod_id = ?;""", (name, desc, num_available, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif name and desc and not num_available and price:
            db.execute("""UPDATE stock
                        SET name = ?, price = ?, num_available=?
                        WHERE prod_id = ?;""", (name, price, num_available, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif name and desc and not num_available and not price:
            db.execute("""UPDATE stock
                        SET name = ?, desc = ?
                        WHERE prod_id = ?;""", (name, desc, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif name and not desc and num_available and price:
            db.execute("""UPDATE stock
                        SET name = ?, num_available = ?, price = ?
                        WHERE prod_id = ?;""", (name, num_available, price, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif name and not desc and num_available and not price:
            db.execute("""UPDATE stock
                        SET name = ?, num_available = ?
                        WHERE prod_id = ?;""", (name, num_available, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif name and not desc and not num_available and price:
            db.execute("""UPDATE stock
                        SET name = ?, price = ?
                        WHERE prod_id = ?;""", (name, price, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif name and not desc and not num_available and not price:
            db.execute("""UPDATE stock
                        SET name = ?
                        WHERE prod_id = ?;""", (name, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif not name and  desc  and num_available and  price:
            db.execute("""UPDATE stock
                        SET desc = ?, num_available = ?, price = ?
                        WHERE prod_id = ?;""", (desc, num_available, price, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif not name and desc and num_available and not price:
            db.execute("""UPDATE stock
                        SET desc = ?, num_available = ?
                        WHERE prod_id = ?;""", (desc, num_available, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif not name and desc and not num_available and price:
            db.execute("""UPDATE stock
                        SET desc = ?, price = ?
                        WHERE prod_id = ?;""", (desc, price, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif not name and desc and not num_available and not price:
            db.execute("""UPDATE stock
                        SET desc = ?
                        WHERE prod_id = ?;""", (desc, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif not name and not desc and num_available and price:
            db.execute("""UPDATE stock
                        SET price = ?, num_available = ?
                        WHERE prod_id = ?;""", (price, num_available, prod_id))
            db.commit()
        #----------------------------------------------------------#
        elif not name and not desc and num_available and not price:
            db.execute("""UPDATE stock
                        SET num_available = ?
                        WHERE prod_id = ?;""", (num_available, prod_id))
            db.commit()
        #----------------------------------------------------------#
        else:
            db.execute("""UPDATE stock
                        SET price = ?
                        WHERE prod_id = ?;""", (price, prod_id))
            db.commit()
    return redirect(url_for('update_item'))
            



@app.route("/delete_item", methods=["GET", "POST"])
def delete():
    global sale
    form = DeleteItem()
    message = ""
    if form.validate_on_submit():
        db = get_db()
        prod_id = form.prod_id.data
        is_in = db.execute("""SELECT *
                        FROM stock
                        WHERE prod_id = ?;""", (prod_id, )).fetchone()
        if is_in is None:
            form.prod_id.errors.append("Item is not on the database")
        else:
            db.execute("""DELETE 
                    FROM stock
                    WHERE prod_id = ?;""", (prod_id, ))
            db.commit()
            message = "Deleted"
            for item in sale:
                if item == is_in["prod_id"]:
                    sale.remove(prod_id)
                sale = []
                check_sale()
    db= get_db()
    items = db.execute("""SELECT *
                       FROM stock;""").fetchall()
    return render_template("delete_item.html", message=message, form=form, items=items, sale=sale)

@app.route("/insert_sale", methods=["GET", "POST"])
def insert_sale():
    form = SaleForm()
    global sale
    message = ""
    items=None
    if form.validate_on_submit():
        global sale
        prod_id = form.prod_id.data
        sale_percent = form.sale_percent.data
        if sale_percent > 100 or sale_percent < 1:
            form.sale_percent.errors.append("\n sale percent must be between 1 and 100")
        else:
            db= get_db()
            check = db.execute("""SELECT *
                               FROM stock
                               WHERE prod_id = ?;""", (prod_id, )).fetchone()
            if check is not None:
                price_check = db.execute("""SELECT price
                                   FROM stock 
                                   WHERE prod_id = ?""", (prod_id, )).fetchone()
                price = float(price_check["price"])
                price = round(price, 2)
                sale_price = price-((sale_percent/100)*price)
                sale_price = round(sale_price, 2)
                db.execute("""UPDATE stock
                           SET price = ?
                           WHERE prod_id = ?""", (sale_price, prod_id))
                db.commit()
                for sale_item in sale:
                    if check["name"] in sale_item:
                        sale.remove(sale_item)
                sale.append(f"{check['name']} is on sale for {sale_percent}%")
                outFile= open("sale.txt", "w")
                for sale_item in sale:
                    outFile.write(sale_item + "\n")
                outFile.close()
                message = "Sale Successfully Implemented"
                sale = []
                check_sale()
            else:
                form.prod_id.errors.append("Prod Id is not in the database")
    db=get_db()
    items = db.execute("""SELECT *
                        FROM stock;""").fetchall()
    return render_template("sale.html", form=form, message=message, title="Sale", items=items, sale=sale)



#___________________________________________________________________________________________#
#User Functions#
@app.route("/checkout")
@login_required
def checkout():
    db = get_db()
    names = {}
    prices = {}
    message = ""
    items_to_delete = []
    items_available = True  

 
    for prod_id in session["cart"].keys(): 
        item = db.execute("""SELECT * FROM stock WHERE prod_id = ?;""", (prod_id,)).fetchone()

        names[prod_id] = item["name"]  
        num_available = item["num_available"]
        quantity_in_cart = session["cart"][prod_id]
        prices[prod_id] = round(float(item["price"]), 2)
        total_price = calc_total_price(prices)

        if num_available < quantity_in_cart:
            message += f"Not enough items in stock for: {names[prod_id]},"
            items_available = False
            continue 


        time = datetime.datetime.now()
        db.execute("""INSERT INTO prev_purchases (user_id, time, name, num_of_items) 
                      VALUES (?, ?, ?, ?);""", 
                    (g.user_id, time.strftime("%Y-%m-%d"), names[prod_id], quantity_in_cart))
        db.commit()

        db.execute("""UPDATE stock
                      SET num_available = num_available - ?
                      WHERE prod_id = ?;""", (quantity_in_cart, prod_id))
        db.commit()
        items_to_delete.append(prod_id)

        check_item_still_ava(prod_id)
    
    for prod_id in items_to_delete:
        del session["cart"][prod_id]
    session.modified = True

    if not items_available:
        wishlist = db.execute("""SELECT name, w.prod_id
                                 FROM wishlist AS w JOIN stock AS s
                                 ON w.prod_id = s.prod_id
                                 WHERE w.user_id = ?;""", (g.user_id, )).fetchall()
        return render_template("cart.html", title="Your Cart", message=message, cart=session["cart"], names=names, prices=prices, form=DeleteCartForm(), wishlist=wishlist, total_price=total_price)
    
    return redirect(url_for('account'))

def check_item_still_ava(prod_id):
    global sale
    db = get_db()
    check = db.execute("""SELECT *
                      FROM stock
                      WHERE prod_id = ? and num_available = 0;""", (prod_id, )).fetchone()
    if check is not None:
        db.execute("""DELETE 
                   FROM stock 
                   WHERE prod_id = ?;""", (prod_id, ))
        db.commit()
        for sale_item in sale:
            if sale_item == check['prod_id']:
                sale.remove(sale_item)
            sale = []   
            check_sale()




@app.route("/cart")
@login_required
def cart():
    message = ""
    form = DeleteCartForm()
    if "cart" not in session:
        session["cart"] = {}
        session.modified = True

    names = {}
    prices = {}
    total_price = 0
    db = get_db()
    wishlist = db.execute("""SELECT name, w.prod_id
                FROM wishlist AS w JOIN stock AS s
                    ON w.prod_id = s.prod_id
                WHERE w.user_id = ?;""", (g.user_id, )).fetchall()
    for prod_id in session["cart"]:
        
        item = db.execute("""SELECT *
                          FROM stock
                          WHERE prod_id = ?""", (prod_id, )).fetchone()
        if item:
            name = item["name"]
            names[prod_id] = name
            price = round(float(item["price"]), 2) 
            prices[prod_id] = price
        else:
            names[prod_id] = "Item Not Found"
            prices[prod_id] = 0
            return render_template("cart.html", cart = session["cart"], names=names, wishlist=wishlist, form=form, message=message, prices=prices, total_price=total_price)
        if prices:
            total_price = calc_total_price(prices)
    return render_template("cart.html", cart = session["cart"], names=names, wishlist=wishlist, form=form, message=message, prices=prices, total_price=total_price)

    
def calc_total_price(prices):
    total_price = 0
    for prod_id in prices:
        total_price += prices[prod_id]*session["cart"][prod_id]
    total_price = round(total_price, 2)
    return(total_price)


        
#-------------------------------------------------------#
@app.route("/delete_form_cart/<int:prod_id>", methods=["POST"])
def delete_from_cart(prod_id):
    form = DeleteCartForm()

    if form.validate_on_submit():
        num_of_items = form.num_of_items.data
        if "cart" not in session:
            session["cart"] = {}
        if session["cart"][prod_id] <= num_of_items:
            del session["cart"][prod_id]
        else:
            session["cart"][prod_id] > num_of_items
            session["cart"][prod_id] -= num_of_items
        
        session.modified=True
        return redirect( url_for("cart"))
    
@app.route("/add_to_cart/<int:prod_id>", methods=["GET", "POST"])
@login_required
def add_to_cart(prod_id):
    global sale
    db = get_db()
    items = db.execute("""SELECT * 
                       FROM stock""").fetchall()
    form = SearchForm()
    form2 = AddCartForm()
    error = {}
    error[prod_id] = []

    if form2.validate_on_submit():
        num_of_items = form2.num_of_items.data


        if "cart" not in session:
            session["cart"] = {}
        if prod_id not in session["cart"]:
            session["cart"][prod_id] = num_of_items
        else:
            session["cart"][prod_id] += num_of_items
        session.modified = True
        return redirect(url_for('cart'))

            
    else:
        if not form2.num_of_items.data:
            error[prod_id].append("Input Required")
    if form.validate_on_submit():
        searchValue = form.searchValue.data
        items = search(searchValue)

    wishlist_items = db.execute("SELECT prod_id FROM wishlist WHERE user_id = ?", (g.user_id,)).fetchall()
    wishlist_prod_ids = [item['prod_id'] for item in wishlist_items]
    return render_template("store.html", title="Store", form2=form2, form=form, sale=sale, items=items, error=error, wishlist_prod_ids=wishlist_prod_ids)

@app.route("/store", methods=["GET", "POST"])
def store():
    global sale
    form = SearchForm()
    form2 = AddCartForm()
    db = get_db()
    items = db.execute("""SELECT * 
                       FROM stock;""").fetchall()
    if form.validate_on_submit():
        searchValue = form.searchValue.data
        items = search(searchValue)
    wishlist_items = db.execute("SELECT prod_id FROM wishlist WHERE user_id = ?", (g.user_id,)).fetchall()
    wishlist_prod_ids = [item['prod_id'] for item in wishlist_items]
    return render_template("store.html", title="Store", items=items, form=form, form2 = form2, wishlist_prod_ids=wishlist_prod_ids, sale=sale, error=[])

def search(searchValue):
    db = get_db()
    items = db.execute("""SELECT *
                           FROM stock
                           WHERE name LIKE ?;""", ("%"+searchValue+"%", )).fetchall()
    return items
#-----------------------------------------------------
@app.route("/add_to_wishlist/<int:prod_id>")
@login_required
def add_to_wishlist(prod_id):
    db = get_db()
    db.execute("""INSERT INTO wishlist(user_id, prod_id)
               VALUES (?, ?);""", (g.user_id, prod_id))
    db.commit()
    return redirect(url_for("cart"))


@app.route("/delete_form_wishlist/<int:prod_id>")
@login_required
def delete_form_wishlist(prod_id):
    db=get_db()
    db.execute("""DELETE
               FROM wishlist
               WHERE user_id = ? and prod_id = ?;""", (g.user_id, prod_id))
    db.commit()
    return redirect(url_for("cart"))
#___________________________________________________________________________________________#



#___________________________________________________________________________________________#
#error#
@app.errorhandler(404)
def error(error):
    return render_template("error.html", title="404 Error"), 404
#___________________________________________________________________________________________#
