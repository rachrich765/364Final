###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, IntegerField, PasswordField, BooleanField, SelectMultipleField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length, Email, Regexp, EqualTo # Here, too, 
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import re
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from werkzeug.security import generate_password_hash, check_password_hash
# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
## App setup code
app = Flask(__name__)
app.debug = True
basedir = os.path.abspath(os.path.dirname(__file__))

## All app.config values


## Statements for db setup (and manager setup if using Manager)
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:4Rocks32@localhost/rachjrFinalProject" # TODO: May need to change this, Windows users. Everyone will need to have created a db with exactly this name.
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# App addition setups
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager

##################
##### MODELS #####
##################
#association table b/w Personal Hashtag Collection Table and Confusing Hashtags Table
user_collection = db.Table('User_Collection',db.Column('ht_id',db.Integer, db.ForeignKey('confusing_hashtags.id')), db.Column('collection_id', db.Integer, db.ForeignKey('pc_ht.id'))) 

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

## DB load function
## Necessary for behind the scenes login manager that comes with flask_login capabilities! Won't run without this.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or Non

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

class Confusing_Hashtag(db.Model):
    __tablename__ = "confusing_hashtags"
    id = db.Column(db.Integer,primary_key=True)
    hashtag = db.Column(db.String(64))
    difficulty = db.Column(db.Integer)
    definition = db.Column(db.String(500))

    #1 to many relationship with ct 
    tweeter_id = db.Column(db.Integer,db.ForeignKey("ct.id"))
    
    def __repr__(self):
        return "{}".format(self.hashtag)

class PersonalHashtagCollection(db.Model):
    __tablename__ = "pc_ht"
    id = db.Column(db.Integer, primary_key=True)
    collection_title = db.Column(db.String(255))
    
    #many to many relationship with confusing_hashtags
    many_ht_pc = db.relationship('Confusing_Hashtag', secondary=user_collection, backref=db.backref('collection', lazy='dynamic'), lazy='dynamic') 
   
    # 1 to many relationship with users 
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))

    def __repr__(self):
        return "{}".format(self.collection_title)

class ConfusingTweeter(db.Model):
    __tablename__ = "ct"
    id = db.Column(db.Integer, primary_key=True)
    tweeter_name = db.Column(db.String(124))

    #1 to many realtionship with confusing_hashtags 
    confusing_hashtags = db.relationship('Confusing_Hashtag',backref='ConfusingTweeter')

    def __repr__(self):
        return "{} (ID: {})".format(self.tweeter_name, self.id)

###################
###### FORMS ######
###################

class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores!')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match!")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #custom validator 1 for Registration Form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    #custom validator 2 for Registration Form
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

#custom validator for Hashtag Form
def validate_hashtag(form,field):
    hashtag_as_string = str(field.data) 
    if not re.match("^[a-zA-Z0-9_]*$", hashtag_as_string):
        raise ValidationError('Hashtags cannot have special symbols or spaces!')

def validate_difficult(form,field):
    difficult_as_int = int(field.data)
    if difficult_as_int not in range(1,11):
        raise ValidationError('Difficulty can only be 1-10!')

class HashtagForm(FlaskForm):
    hashtag = StringField("Enter the hashtag that confused you (without special characters or spaces):", validators=[Required(), validate_hashtag])
    tweeter = StringField("Enter the name of the Twitter user who confused you with this hashtag:", validators=[Required()])
    difficulty = StringField("On a scale of 1-10 (1= I think I get it, 10 = I have no clue), how confusing is this hashtag?", validators = [Required(), validate_difficult])
    submit = SubmitField()

class CollectionCreateForm(FlaskForm):
    title = StringField('Collection Title',validators=[Required()])
    chosen_ht = SelectMultipleField(coerce=int)
    submit = SubmitField("Create Collection")

class UpdateButtonForm(FlaskForm):
    update = SubmitField('Update')

def validate_difficult(form,field):
    difficult_as_int = int(field.data)
    if difficult_as_int not in range(1,11):
        raise ValidationError('Difficulty can only be 1-10!')
class UpdateDifficultyForm(FlaskForm):
    newDifficulty = StringField("After seeing the definition, what is your new difficulty of this hashtag?", validators=[Required(), validate_difficult])
    update = SubmitField('Update')

class DeleteButtonForm(FlaskForm): 
    delete = SubmitField('Delete')

my_choices = [('1', "Heck Yeah I'm feeling lucky!"), ('2', "Not really feeling lucky today, but it's worth a shot!"), ('3', 'NOPE')]

class SecretSweepstakesForm(FlaskForm):
    lucky = SelectMultipleField('Are you feeling lucky today?',choices = my_choices, validators=[Required()])
    submit = SubmitField('Submit')
###################################
##### Error handling routes #####
###################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_error.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500_error.html'), 500

###################################
##### Helper functions #####
###################################
def get_hashtag_defs_from_API(hashtag):
    info = []
    definitons = ""
    base_url = 'https://tagdef.p.mashape.com/'
    url = base_url + str(hashtag) + '.json'
    response = requests.get(url, headers={"X-Mashape-Key": "VU8AUgehLmmshCMUdGEwWdA49txSp10aCeyjsnXi0WHAvPjz70","Accept": "application/json"})
    text=response.text
    python_obj = json.loads(text)
    for x in python_obj['defs']:
        info.append(x)
    for n in info:
        definitons = (n['def']['text'])
    return str(definitons)
        #return render_template('hashtag_results.html', objects = info, hashtag=hashtag)

def get_or_create_hashtag(hashtag, tweeter, difficulty, definition):
    h1 = db.session.query(Confusing_Hashtag).filter_by(hashtag=hashtag).first()
    if h1:
        return h1
    else:
        ht1 = Confusing_Hashtag(hashtag=hashtag, tweeter_id=tweeter, difficulty= difficulty, definition=definition)
        db.session.add(ht1)
        db.session.commit()
        return h1

def get_hashtag_by_id(id):
    ght = Confusing_Hashtag.query.filter_by(id=id).first()
    return ght

def get_or_create_collection(title, current_user, ht_list=[]):
    """Always returns a PersonalGifCollection instance"""
    pc = db.session.query(PersonalHashtagCollection).filter_by(collection_title=title,user_id=current_user.id).first()
    if pc:
        return pc
    else:
        pc = PersonalHashtagCollection(collection_title=title,user_id=current_user.id, many_ht_pc=[])
        for gl in ht_list:
            pc.many_ht_pc.append(gl)
        db.session.add(pc)
        db.session.commit()
    return pc

########################################
# Login/Logout Routes & View Functions #
########################################
## Login-related routes - provided
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now log in!')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

########################################
#### Other Routes & View Functions #####
########################################

#main page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = HashtagForm()
    if form.validate_on_submit() and request.method=='POST':
        ht = str(form.hashtag.data)
        t = form.tweeter.data
        d = form.difficulty.data
        ct = ConfusingTweeter.query.filter_by(tweeter_name=t).first()
        if ct:
            flash("Confusing Tweeter is already in the database!")
        if not ct:
            ct = ConfusingTweeter(tweeter_name=t)
            db.session.add(ct)
            db.session.commit()
            flash("Confusing Tweeter was added to the database!")
        defintion = get_hashtag_defs_from_API(ht)
        get_or_create_hashtag(hashtag=ht, tweeter = ct.id, difficulty = d, definition=defintion)
        flash('Hashtag information was successfully saved to the database! The definition of your hashtag is:' + " " + str(defintion))
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html',form=form)

#logged-in user can create collection of hashtags
@app.route('/create_collection',methods=["GET","POST"])
@login_required
def create_collection():
    collections = PersonalHashtagCollection.query.all()
    num_collections = len(collections)
    form = CollectionCreateForm()
    hashtags =Confusing_Hashtag.query.all()
    choices = [(g.id, g.hashtag) for g in hashtags]
    form.chosen_ht.choices = choices
    if form.validate_on_submit() and request.method == 'POST':
        hts_selected = form.chosen_ht.data 
        ht_objects = [get_hashtag_by_id(int(id)) for id in hts_selected]
        get_or_create_collection(title=form.title.data,current_user=current_user, ht_list=ht_objects)
        return redirect(url_for('all_collections'))
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('create_collection.html',num_collections=num_collections, form=form)

#shows all conllections of logged-in user
@app.route('/collections',methods=["GET","POST"])
@login_required
def all_collections():
    form = DeleteButtonForm()
    current_user_collection = db.session.query(PersonalHashtagCollection).filter_by(user_id=current_user.id)
    return render_template('personal_collection.html', collections=current_user_collection, form=form)

#displays contents (hashtags) of selected collections
@app.route('/collection/<title>', methods=["GET","POST"])
@login_required
def single_collection(title):
    title = str(title)
    form = UpdateButtonForm()
    collection = PersonalHashtagCollection.query.filter_by(collection_title=title).first()
    hashtags = collection.many_ht_pc.all()
    return render_template('collection_contents.html',collection=collection, hts=hashtags, form=form)

#deletes selected collection 
@app.route('/delete/<collection>',methods=["GET","POST"])
@login_required
def delete(collection):
    form = DeleteButtonForm()
    if form.validate_on_submit():
        cl = PersonalHashtagCollection.query.filter_by(collection_title = collection).first()
        db.session.delete(cl)
        db.session.commit()
        flash("Deleted collection" + " " + str(collection))
        return redirect(url_for('all_collections'))
    return redirect(url_for('delete', collection=collection))

#updates difficulty rating of hashtag
@app.route('/update/<hashtag>',methods=["GET","POST"])
@login_required
def update(hashtag):
    form = UpdateDifficultyForm()
    h2 = Confusing_Hashtag.query.filter_by(hashtag= hashtag).first()
    definition = h2.definition
    if form.validate_on_submit():
        new_difficulty = form.newDifficulty.data
        h2.difficulty = new_difficulty
        db.session.commit()
        flash("Updated difficulty rating of " + str(hashtag) +" to " + new_difficulty)
        return redirect(url_for('all_collections'))
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('update_hashtag.html', definition=definition,form=form)

@app.route('/all_confusing_tweeters', methods=['GET'])
def act_ht():
    all_ct2 = list()
    all_ct = ConfusingTweeter.query.all()
    num_ct = len(all_ct) 
    all_the_hashtags_and_ct = Confusing_Hashtag.query.all()
    for h in all_the_hashtags_and_ct:
        ct1 = ConfusingTweeter.query.filter_by(id=h.tweeter_id).first()
        all_ct2.append(ct1)
    return render_template('all_ct.html', num_ct= num_ct, all_ct=all_ct2)

if __name__ == '__main__':
    db.create_all() 
    app.run(use_reloader=True,debug=True) 