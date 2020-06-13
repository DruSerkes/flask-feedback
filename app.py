from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from helpers import generate_user_data, generate_login_data, generate_feedback_data


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
    # Check if user logged in first
    if 'username' in session:
        username = session['username']
        return redirect(f'/users/{username}')
    
    form = RegisterForm()
    if form.validate_on_submit():
        user_data = generate_user_data(form)
        new_user = User.register(user_data)

        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username

        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ 
    User Login  
    """
    # Check if user logged in first
    if 'username' in session:
        username = session['username']
        return redirect(f'/users/{username}')

    form = LoginForm()
    if form.validate_on_submit():
        login_data = generate_login_data(form)
        user = User.authenticate(login_data)
        if user:
            flash(f'Welcome back {user.username}')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors.append('Invalid login')
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def show_secret_page(username):
    """ Display secret page """
    if 'username' in session:
        user = User.query.filter_by(username=username).first()
        return render_template('secret.html', user=user)

    else:
        return redirect('/login')


@app.route('/logout')
def logout_user():
    """ Removes user from session and redirect home """
    session.pop('username')
    return redirect('/login')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """ Delete a user and remove all feedback """
    if 'username' in session and session['username'] == username:
        User.query.filter_by(username=username).delete()
        db.session.commit()
        session.pop('username')
        return redirect('/')


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """ Add feedback for a user """
    if 'username' in session:
        form = FeedbackForm()
        if form.validate_on_submit():
            feedback_data = generate_feedback_data(form, username)
            new_feedback = Feedback.make_feedback(feedback_data)
            db.session.add(new_feedback)
            db.session.commit()
            flash('Feedback added', 'success')
            return redirect(f'/users/{username}')
        return render_template('add_feedback.html', form=form)
    flash("You must be logged in to do that!")
    return redirect('/login')


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    """ Edit feedback """
    if 'username' in session:
        feedback = Feedback.query.get_or_404(feedback_id)
        form = FeedbackForm(obj=feedback)    
        if form.validate_on_submit():
            feedback.title = form.title.data 
            feedback.content = form.content.data 
            db.session.commit()
            flash('Feedback edited', 'success')
            return redirect(f'/users/{feedback.username}')
        return render_template('edit_feedback.html', form=form)
    flash("You must be logged in to do that!")
    return redirect('/login')

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """ Delete feedback and return to user page """ 
    if 'username' in session:
        # Get username 
        username = session['username']

        # Remove feedback 
        Feedback.query.filter_by(id=feedback_id).delete()
        db.session.commit()
        flash('Feedback Deleted!', 'success')
        return redirect(f'/users/{username}')
    else:
        flash("You must be logged in to do that!", 'danger')
        return redirect('/login')

# CUSTOM 404 PAGE 
@app.errorhandler(404)
def display_404(error):
    """ Displays a custom error page when returning a 404 error """
    return render_template('/error.html'), 404