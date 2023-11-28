import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import keras.models
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def find_similar_users(user_ratings, ratings):
    # Filter train data for the specified books in user_ratings
    selected_books = user_ratings['book_id'].values
    train_subset = ratings[ratings['book_id'].isin(selected_books)]

    # Pivot the train_subset to have users as rows and books as columns
    user_book_matrix = train_subset.pivot_table(index='user_id', columns='book_id', values='rating', fill_value=0)

    # Create a user-book matrix for the target user
    target_user_ratings = pd.Series(user_ratings['rating'].values, index=user_ratings['book_id'])
    target_user_matrix = pd.DataFrame(target_user_ratings).transpose()

    # Calculate cosine similarity between the target user and all other users
    similarity_scores = cosine_similarity(target_user_matrix, user_book_matrix)

    # Get the top 3 most similar users
    similar_users_indices = similarity_scores.argsort()[0, ::-1][1:4]
    similar_users = user_book_matrix.index[similar_users_indices]

    return list(similar_users)


def recommend_books_user_based(user_ratings, model, ratings):
    
    similar_users = find_similar_users(user_ratings, ratings)
    
    # Get the list of all books
    all_books = ratings['book_id'].unique()
    
    predict_data = pd.DataFrame([(similar_user, book_id) for similar_user in similar_users for book_id in all_books if book_id not in user_ratings['book_id']],
                                columns=['user_id', 'book_id'])

    # Use the model to predict ratings
    predictions = model.predict([np.array(predict_data['user_id']), np.array(predict_data['book_id'])])

    predict_data['predicted_rating'] = predictions

    top_books = predict_data.groupby('book_id')['predicted_rating'].mean().reset_index()

    return top_books[['book_id', 'predicted_rating']]


def recommend_books_content_based(user_ratings, cosine_sim, ratings):
    # Get the list of all books
    all_books = ratings['book_id'].unique()

    predict_data = pd.DataFrame([book_id for book_id in all_books
                                 if book_id not in user_ratings['book_id']],
                                columns=['book_id'])

    # Use the cosine similarity to predict ratings
    for i, book_id in enumerate(predict_data['book_id']):
        
        similarity_scores = cosine_sim[book_id-1]
        
        weighted_sum = 0
        similarity_sum = 0

        for _, rated_book in user_ratings.iterrows():
            similarity = similarity_scores[rated_book['book_id'] - 1]
            weighted_sum += similarity * rated_book['rating']
            similarity_sum += abs(similarity)

        if similarity_sum != 0:
            similarity_sum = max(0.7, similarity_sum)
            predict_data.at[i, 'predicted_rating'] = weighted_sum / similarity_sum
            
        else:
            predict_data.at[i, 'predicted_rating'] = 1
            
    predict_data = predict_data[~predict_data['book_id'].isin(user_ratings['book_id'])]

    return predict_data[['book_id', 'predicted_rating']]


def hybrid_model(user_ratings, model, cosine_sim, ratings):
    
    user_based_predict = recommend_books_user_based(user_ratings, model, ratings)
    content_based_predict = recommend_books_content_based(user_ratings, cosine_sim, ratings)
    
    # Merge the two DataFrames on 'book_id'
    merged_df = pd.merge(user_based_predict, content_based_predict, on='book_id', suffixes=('_user', '_content'))

    # Calculate the overall rating using the specified formula
    merged_df['predicted_rating'] = merged_df['predicted_rating_user'] * 0.6 + merged_df['predicted_rating_content'] * 0.4
    
    return merged_df[['book_id', 'predicted_rating']]


def top_recommend_books(user_ratings, model, cosine_sim, ratings, books_information, num_recommendations=5):
    
    predict_data = hybrid_model(user_ratings, model, cosine_sim, ratings)
    
    top_recommendations = predict_data.sort_values(by='predicted_rating', ascending=False).head(num_recommendations)
    
    recommended_book_ids = top_recommendations['book']
    
    return books_information[books_information['book_id'].isin(recommended_book_ids)]


def data_loading():

    ratings = pd.read_csv('https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/ratings.csv')

    model = keras.models.load_model('./models/user_based_model.keras')

    books_information = pd.read_csv('./data/interim/books_information.csv')

    features = ['average_rating', 'original_publication_year', 'authors']

    books_information['text_features'] = books_information[features].astype(str).agg(' '.join, axis=1)

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')

    tfidf_matrix = tfidf_vectorizer.fit_transform(books_information['text_features'])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    return ratings, books_information, model, cosine_sim 


def run_model(user_ratings):

    ratings, books_information, model, cosine_sim = data_loading()

    book_id = [item[0] for item in user_ratings]
    book_ratings = [item[1] for item in user_ratings]

    user_ratings = pd.DataFrame({  
        'book_id': book_id,
        'rating': book_ratings
    })

    result = top_recommend_books(user_ratings, model, cosine_sim, ratings, books_information)

    return result.values.tolist()
