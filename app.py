from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm
from helpers import generate_user_data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres:///flask-feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    """ Home redirects to /register """
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Register a user """
    form = RegisterForm()
    if form.validate_on_submit():
        # username = form.username.data
        # password = form.password.data
        # email = form.email.data
        # first_name = form.first_name.data
        # last_name = form.last_name.data
        user_data = generate_user_data(form)
        new_user = User.register(user_data)

        db.session.add(new_user)
        db.session.commit()
        return redirect('/secret')

    return render_template('register.html', form=form)

