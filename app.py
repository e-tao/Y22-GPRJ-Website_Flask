from flask import Flask, render_template, redirect, request, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

# replace the user name and password in the statement below
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/bluescafe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/bluescafe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# page = db.Table('page', db.metadata, autoload=True, autoload_with=db.engine)

Base = automap_base()
Base.prepare(db.engine, reflect=True)
Page = Base.classes.page
FoodMenu = Base.classes.menu
User = Base.classes.user


@ app.route('/')
@ app.route('/index')
def index():
    # new_page = Page(title="NewPage", name="new", content="this is the new page")
    # db.session.add(new_page)
    # db.session.commit()
    foodMenu = db.session.query(FoodMenu).order_by(
        FoodMenu.day.desc()).limit(6)
    foodMenu = foodMenu[::-1]
    # menus = db.session.query(Page.name).order_by(Page.order.asc())
    # pages = db.session.query(Page.content).order_by(Page.order.asc())
    pages = db.session.query(Page).order_by(Page.order.asc())
    return render_template('index.html', pages=pages, foodMenu=foodMenu)


@ app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        pwd = request.form["password"]
        pwd_hash = db.session.query(
            User.passHash).filter_by(username=username.lower().strip())
        if (bcrypt.check_password_hash(pwd_hash[0][0], pwd)):
            resp = make_response(redirect("/addmenuitem"))
            resp.set_cookie('user', username, max_age=60*60*24)
            return resp
        else:
            return render_template('error.html', message="wrong password")
    else:
        return render_template('login.html')


@ app.route('/addmenuitem', methods=["GET", "POST"])
def addMenuItem():
    if request.cookies.get('user'):
        if request.method == "POST":
            items = request.form.getlist('item')
            entrees = request.form.getlist('entree')
            dates = request.form.getlist('date')

            for i in range(len(items)):
                if(items[i] != ""  and entrees[i] !="" and dates[i] != ""):
                   new_item = FoodMenu(item=items[i], entree=entrees[i], day=dates[i])
                   db.session.add(new_item)
                else:
                    return render_template('error.html', message="input error", back=request.referrer)

            db.session.commit()
            return redirect("/")
        else:
            return render_template("addmenuitem.html")
    else:
        return redirect("/login")


if __name__ == '__main__':
    app.run(debug=True)
