from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote_plus
import os

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/rave'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    __tablename__ = 'users'  # Table name as per your database schema

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Plain text password

    def check_password(self, password):
        # Compare plain text password with stored password
        return self.password == password

# Define RecipeRecommender class
class RecipeRecommender:
    def __init__(self, data_path, feedback_path):
        self.data_path = data_path
        self.feedback_path = feedback_path
        self.recipes = None
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.recipe_indices = None
        self.user_feedback = pd.DataFrame(columns=['id', 'recipe_index', 'feedback'])

    def load_data(self):
        self.recipes = pd.read_csv(self.data_path)
        if os.path.exists(self.feedback_path):
            self.user_feedback = pd.read_csv(self.feedback_path)

    def preprocess_data(self):
        self.recipes.fillna('', inplace=True)
        self.tfidf_matrix = self.tfidf.fit_transform(self.recipes['title'])
        self.recipe_indices = pd.Series(self.recipes.index, index=self.recipes['title']).drop_duplicates()

    def recommend_recipes(self, user_input, id, num_recommendations=5):
        user_tfidf = self.tfidf.transform([user_input])
        cosine_similarities = cosine_similarity(user_tfidf, self.tfidf_matrix).flatten()
        similar_recipe_indices = cosine_similarities.argsort()[:-num_recommendations-1:-1]

        recommended_recipes = []
        for index in similar_recipe_indices:
            feedback = self.user_feedback[(self.user_feedback['recipe_index'] == index) & (self.user_feedback['id'] == id)]['feedback'].values
            feedback_text = 'You liked it before' if 'like' in feedback else 'You disliked it before' if 'dislike' in feedback else ''
            recipe = {
                'index': index,
                'title': self.recipes.loc[index, 'title'],
                'calories': self.recipes.loc[index, 'calories'],
                'fat': self.recipes.loc[index, 'fat'],
                'cosine_similarity': cosine_similarities[index],
                'youtube_link': f"https://www.youtube.com/results?search_query={quote_plus(self.recipes.loc[index, 'title'])}",
                'feedback_text': feedback_text
            }
            recommended_recipes.append(recipe)

        return recommended_recipes[:num_recommendations]

    def get_recipe_ingredients(self, recipe_index):
        ingredients = self.recipes.columns[self.recipes.iloc[recipe_index] == 1].tolist()
        return ingredients

# Initialize RecipeRecommender
data_path = 'data/epicurious_recipes.csv'
feedback_path = 'D:\\Content-based--Recipe-with-Ingredients-Recommendation-System-main - Copy\\data\\user_feedback.csv'
recommender = RecipeRecommender(data_path, feedback_path)
recommender.load_data()
recommender.preprocess_data()

# Forms
class RecipeForm(FlaskForm):
    dish_feeling = StringField('Let\'s create the magic!', validators=[DataRequired()])
    submit = SubmitField('RAVE Magical Recommendations')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=1)])  # Adjusted for plain text
    submit = SubmitField('Login')

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'id' not in session:
        return redirect(url_for('login'))

    form = RecipeForm()
    if form.validate_on_submit():
        user_input = form.dish_feeling.data
        id = session['id']
        recommendations = recommender.recommend_recipes(user_input, id)
        return render_template('recommend.html', recommendations=recommendations)

    return render_template('index.html', form=form)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/give_feedback', methods=['POST'])
def give_feedback():
    if 'id' not in session:
        return redirect(url_for('login'))

    id = session['id']
    recipe_index = int(request.form['recipe_index'])
    feedback = request.form['feedback']
    if feedback in ['like', 'dislike']:
        new_feedback = pd.DataFrame({'id': [id], 'recipe_index': [recipe_index], 'feedback': [feedback]})
        recommender.user_feedback = pd.concat([recommender.user_feedback, new_feedback], ignore_index=True)
        try:
            recommender.user_feedback.to_csv(recommender.feedback_path, index=False)
        except PermissionError as e:
            flash(f'Error saving feedback: {e}', 'danger')
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/recipe/<int:recipe_index>', methods=['GET'])
def recipe_details(recipe_index):
    ingredients = recommender.get_recipe_ingredients(recipe_index)
    return render_template('recipe_details.html', ingredients=ingredients)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
