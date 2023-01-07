import pandas as pd
import sqlite3
from base.database import open_database_link, close_database_link

# from celery import Celery
# from celery.schedules import crontab

# app = Celery()
# print('hi')

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls test('hello') every 10 seconds.
#     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

#     # Calls test('world') every 30 seconds
#     sender.add_periodic_task(30.0, test.s('world'), expires=10)

#     # Executes every Monday morning at 7:30 a.m.
#     sender.add_periodic_task(
#         crontab(hour=17, minute=48, day_of_week=4),
#         test.s('Happy Mondays!'),
#     )
#     print(sender)

# @app.task
# def test(arg):
#     print(arg)

# @app.task
# def add(x, y):
#     z = x + y
#     print(z)


# * Content based Recommendations
class ContentRecommendation():
    def __init__(self) -> None:
        self.vectorize_books()
    
    def vectorize_books(self):
        conn, c = open_database_link()
        df = pd.read_sql_query('SELECT BookID,BookTitle,BookAuthor,BookGenre FROM Book',conn)

        df = df.drop_duplicates(subset=['BookTitle'])
        df = df.dropna(axis=0)
        def clean_text(author):
            result = str(author).lower()
            return(result.replace(' ',''))

        df['BookAuthor'] = df['BookAuthor'].apply(clean_text)
        df['BookTitle'] = df['BookTitle'].str.lower()
        df2 = df
        df2['data'] = df2[df2.columns[1:]].apply(
            lambda x: ' '.join(x.dropna().astype(str)),
            axis=1
        )
        from sklearn.feature_extraction.text import CountVectorizer
        vectorizer = CountVectorizer()
        vectorized = vectorizer.fit_transform(df2['data'])

        from sklearn.metrics.pairwise import cosine_similarity

        similarities = cosine_similarity(vectorized)
        self.df3 = pd.DataFrame(similarities, columns=df2['BookTitle'], index=df2['BookID']).reset_index()

        close_database_link(conn)

    def get_recommendations(self, input_book):
        recommendations = pd.DataFrame(self.df3.nlargest(11,input_book))
        # for some reason, this command only works half the time, so will simply cut off the first one
        # recommendations = recommendations[recommendations[input_book]!=1]
        recommendations = recommendations[1:]
        return recommendations


class UserRecommndation():

    def __init__(self) -> None:
        self.data_processing()


    def data_processing(self):
        conn, c = open_database_link()    
        books = pd.read_sql_query("SELECT BookID,BookTitle FROM Book",conn)
        borrows = pd.read_sql_query("SELECT StudentID, BookID FROM Borrow", conn)
        close_database_link(conn)

        df = borrows.merge(books, on="BookID")
        df['borrowed'] = 1
        matrix = df.pivot_table(index='StudentID', columns='BookTitle', values='borrowed')

        from sklearn.metrics.pairwise import cosine_similarity
        user_similarity = cosine_similarity(matrix.fillna(0))
        user_similarity = pd.DataFrame(user_similarity, columns = matrix.index.tolist())

        try:
            user_similarity = user_similarity.drop(index=0)
        except:
            pass
        self.user_similarity, self.matrix = user_similarity, matrix

    
    def get_user_recommendations(self, picked_studentid):
        # Remove picked student ID from the candidate list
        try:
            user_similarity = self.user_similarity.drop(index=picked_studentid)
        except:
            print('picked_studentid has already been removed')

        # Number of similar users
        n = 10
        # User similarity threashold
        user_similarity_threshold = 0.3
        # Get top n similar users
        similar_users = user_similarity[user_similarity[picked_studentid]>user_similarity_threshold][picked_studentid].sort_values(ascending=False)[:n]
        
        # Print out top n similar users
        print(f'The similar users for user {picked_studentid} are\n', similar_users)

        matrix = self.matrix
        # * Books that the target user has read
        picked_userid_borrowed = matrix[matrix.index == picked_studentid].dropna(axis=1, how='all')
        # * Books that similar users have borrowed. Remove books that none of the similar users have read

        similar_user_books = matrix[matrix.index.isin(similar_users.index)].dropna(axis=1, how='all')

        item_score = {}

        # Loop through items
        for i in similar_user_books.columns:
            # Get the ratings for book i
            book_rating = similar_user_books[i]
            # create a variable to store the score
            total = 0
            # create a variable to store the number of scores
            count = 0
            # Loop through similar users
            for u in similar_users.index:
                # if the book has rating
                if not pd.isna(book_rating[u]):
                    # Score is the sum of user similarity score mutiply by the book rating
                    score = similar_users[u] * book_rating[u]
                    # Add the score to the total score for the book so far
                    total += score
                    # Add 1 to the count
                    count += 1
                    
            item_score[i] = total / count
            
        # Convert dictionary to pandas dataframe
        item_score = pd.DataFrame(item_score.items(), columns=['book', 'book_score'])
            
        # Sort the books by score
        ranked_item_score = item_score.sort_values(by='book_score', ascending=False)
        # Select top m books
        m = 20
        return ranked_item_score.head(m)



    

