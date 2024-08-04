import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RecipeRecommender:
    def __init__(self, data_path):
        self.data_path = data_path
        self.recipes = None
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.recipe_indices = None

    def load_data(self):
        self.recipes = pd.read_csv(self.data_path)

    def preprocess_data(self):
        # Handle missing values if any (though this should have been done in data_processing.py)
        self.recipes.fillna('', inplace=True)

        # Fit the TF-IDF Vectorizer on the recipe titles
        self.tfidf_matrix = self.tfidf.fit_transform(self.recipes['title'])

        # Store the indices of the recipes
        self.recipe_indices = pd.Series(self.recipes.index, index=self.recipes['title']).drop_duplicates()

    def recommend_recipes(self, user_input, num_recommendations=5):
        # Transform user input into TF-IDF vector
        user_tfidf = self.tfidf.transform([user_input])

        # Compute cosine similarities between user input and all recipes
        cosine_similarities = cosine_similarity(user_tfidf, self.tfidf_matrix).flatten()

        # Get indices of top similar recipes
        similar_recipe_indices = cosine_similarities.argsort()[:-num_recommendations-1:-1]

        # Get titles of recommended recipes
        recommended_recipes = self.recipes.loc[similar_recipe_indices, 'title'].values.tolist()

        return recommended_recipes

if __name__ == "__main__":
    # Example usage:
    data_path = 'D:\\jugaad\\data\\epicurious_recipes.csv'  # Adjust the path as per your project structure
    recommender = RecipeRecommender(data_path)
    recommender.load_data()
    recommender.preprocess_data()

    # Example user input for recommendation
    user_input = "Paneer Butter Masala"
    recommendations = recommender.recommend_recipes(user_input)

    print(f"Recommended Recipes for '{user_input}':")
    for i, recipe in enumerate(recommendations, start=1):
        print(f"{i}. {recipe}")
