from datetime import datetime
from app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
from time import time
import jwt

followers = db.Table('followers', #association table
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))    
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #^that is initialized with db.relationship. This is not an actual database field, but a high-level view of the relationship between users and posts, 
    # and for that reason it isn't in the database diagram. For a one-to-many relationship, a db.relationship field is normally defined on the "one" side, 
    # and is used as a convenient way to get access to the "many". So for example, if I have a user stored in u, the expression u.posts will run a database query
    #  that returns all the posts written by that user. The first argument to db.relationship is the model class that represents the "many" side of the relationship.
    #  This argument can be provided as a string with the class name if the model is defined later in the module. The backref argument defines the name of a field 
    # that will be added to the objects of the "many" class that points back at the "one" object. This will add a post.author expression that will return the user 
    # given a post. The lazy argument defines how the database query for the relationship will be issued
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship( # I'm defining the relationship as seen from the left side user with the name followed, 
                                # because when I query this relationship from the left side I will get the list of followed users (i.e those on the right side).
        'User', secondary=followers, #right side entity of relationship (left side is the parent class), "secondary" configures the association table
        primaryjoin=(followers.c.follower_id == id), # indicates condition to link the left side to the association table. 
        secondaryjoin=(followers.c.followed_id == id), # indicates the condition to link the right side
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic' # backref defines how the relationship will be accessed from the right side
        # right side are followers, left side are followed.
        # dynamic sets up the query to not run until specifically requested   
    )
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password): #method that hashes password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): #function that checks hashed password
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):#method that returns an avatar
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        #lower() = make email address all lowercase (required by gravatar)
        #encode() = makes it bytes, I think. because of python
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user): #checks to make sure following relationship exists
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
        
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter( # The first argument is the followers association table, and the second argument is the join condition.
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc()) # own posts and followed posts combined by union
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8') #token as string
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return #catch error if token can't be validated or is expired
        return User.query.get(id) # returns user if the token is valid


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    language = db.Column(db.String(5))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #The user_id field was initialized as a foreign key to user.id, which means that it references an id value from the users table. 
    # In this reference the user part is the name of the database table for the model. It is an unfortunate inconsistency that in some 
    # instances such as in a db.relationship() call, the model is referenced by the model class, which typically starts with an uppercase character, 
    # while in other cases such as this db.ForeignKey() declaration, a model is given by its database table name, for which SQLAlchemy automatically 
    # uses lowercase characters and, for multi-word model names, snake case.

    def __repr__(self):
        return '<post {}>' .format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))