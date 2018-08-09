from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, PostForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm
from app.models import User, Post
from app.email import send_password_reset_email
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

###############################
# Here lies the view functions#
###############################

#'@' are decorators, a unique feature of the Python language. A decorator modifies the function that follows it. 
#A common pattern with decorators is to use them to register functions as callbacks for certain events. 
#In this case, the @app.route decorator creates an association between the URL given as an argument and the function. 
#In this example there are two decorators, which associate the URLs / and /index to this function. 
#This means that when a web browser requests either of these two URLs, Flask is going to invoke this function and 
#pass the return value of it back to the browser as a response.
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])# I accept POST requests in both routes associated with the index view function in addition to GET requests                                          
@login_required # must be logged in to be here
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_prev else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='home', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: #if the user is logged in,
        return redirect(url_for('index')) #does not let them see log in page, redirects to index
    form = LoginForm() #displays log in from if user is not logged in
    if form.validate_on_submit(): #if form is valid
        user = User.query.filter_by(username=form.username.data).first() #query username, should return only 1 or 0 names so using first()
        if user is None or not user.check_password(form.password.data): #no username found or password is wrong
            flash('Invalid username or password') #error message
            return redirect(url_for('login')) #redirect to try again
        login_user(user, remember=form.remember_me.data) #method from flask_login (i think) to actually log in user
        next_page = request.args.get('next')#value of NEXT query string agument is obtained. 
                                            #Flask provides a REQUEST var that contains all the information that the 
                                            #client sent with the request. REQUEST.ARGS shows the contents in dictionary
                                            #format
        if not next_page or url_parse(next_page).netloc != ' ': #URL_PARSE() function and netloc are for security purposes.
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:#if logged in, redirect to index
        return redirect(url_for('index'))
    form = RegistrationForm() #instantiated an object from class 'RegistrationForm' called it 'form', passed it to template at the bottom
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data) #for sticking into db. username is the col in db, 
        user.set_password(form.password.data)                           #form.username.data is the data the user input in the from
        db.session.add(user)
        db.session.commit() #add and commit user into db
        flash('Congratulationsm you are now registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    #The form=form syntax may look odd, but is simply passing the form object created in the line above 
    #(and shown on the right side) to the template with the name form\

@app.route('/user/<username>') #This is a dynamic component. Flask will except any text between <>. will invoke the view function with the actual text as an argument
def user(username): #For example, if the client browser requests URL /user/susan, the view function is going to be called with the argument username set to 'susan'
    user = User.query.filter_by(username=username).first_or_404()#variant of first(), sends 1st result. if there is none, sends 404. Saves me from checking for no results 
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)#render new template, pass user object and list of posts

@app.before_request #register the decorated function to be executed right before the view function. 
#This is extremely useful because now I can insert code that I want to execute before any view function in the application, 
#and I can have it in a single place.
def before_request():
    if current_user.is_authenticated: #check if current user is logged in, if so store it in the db
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
######################################################################
# If you are wondering why there is no db.session.add() before the commit, 
# consider that when you reference current_user, 
# Flask-Login will invoke the user loader callback function, 
# which will run a database query that will put the target user in the database session. 
# So you can add the user again in this function, but it is not necessary because it is already there.
######################################################################

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved. Congrat')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
# If validate_on_submit() returns True I copy the data from the form into the user object and then write the object to the database. 
# But when validate_on_submit() returns False it can be due to two different reasons. First, it can be because the browser just sent a GET request, 
# which I need to respond to by providing an initial version of the form template. It can also be when the browser sends a POST request with form data, 
# but something in that data is invalid. For this form, I need to treat these two cases separately. 
# When the form is being requested for the first time with a GET request, I want to pre-populate the fields with the data that is stored in the database, 
# so I need to do the reverse of what I did on the submission case and move the data stored in the user fields to the form, 
# as this will ensure that those form fields have the current data stored for the user. 
# But in the case of a validation error I do not want to write anything to the form fields, because those were already populated by WTForms. 
# To distinguish between these two cases, I check request.method, which will be GET for the initial request, and POST for a submission that failed validation.
# 
# ^^^ basically this is a clever way to use the same form to create and update ^^^ 

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('lol, you cannot unfollow yourself')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int) # not sure about this. look up later
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)