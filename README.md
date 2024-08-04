## Your Personal Recipe Recommendation System- With your preferences!

This project is a Flask-based web application that recommends recipes to users based on their input. Users can log in, enter their dish preferences, and receive personalized recipe recommendations. The application uses TF-IDF vectorization and cosine similarity to generate recommendations. User feedback on recipes is also taken into account for future recommendations.

## Features

- User authentication (login/logout)
- Recipe recommendations based on user input
- Feedback system to improve future recommendations
- Ingredient details for each recipe

## Requirements

- Python 3.7+
- Flask
- Flask-WTF
- Flask-SQLAlchemy
- Pandas
- Scikit-learn
- MySQL
- SQLAlchemy
- pymysql

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/recipe-recommender.git
    cd recipe-recommender
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the MySQL database and create the necessary tables (see #rave.sql in data folder for details).

5. Update the database configuration in `app.py`:
    ```python
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/rave'
    ```

6. Run the application:
    ```bash
    flask run
    ```

## Usage

1. Navigate to `http://localhost:5000` in your web browser.
2. Log in using your username and password.
3. Enter your dish preferences to receive recipe recommendations.
4. Provide feedback on the recommended recipes to improve future recommendations.

## Database Schema

Run the following SQL commands to create the necessary tables:
CREATE DATABASE rave;

USE rave;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL
);
