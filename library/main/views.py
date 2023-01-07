from django.shortcuts import render
from main.algorithim import ContentRecommendation, UserRecommndation
from base.database import open_database_link, close_database_link, slug_image_name

# third party
import random

# Create your views here.
content_recommendation_algorithim = ContentRecommendation()
user_recommendation_algorithim = UserRecommndation()



def index(request):
    user_id=3
    conn, c = open_database_link()


    """ Content BASED RECOMMENDATION """
    c.execute(f"SELECT Book.BookTitle FROM Borrow INNER JOIN Book ON Borrow.BookID=Book.BookID WHERE Borrow.StudentID={user_id}")
    borrowed_books = c.fetchall()
    random_book = random.choice(borrowed_books)[0]
    print(random_book)

    random_book_lower = random_book.lower()

    content_recommendations = content_recommendation_algorithim.get_recommendations(random_book_lower)
    indexes = [] # needs to be a list here so we can append new items
    for index,row in content_recommendations.iterrows():
        indexes.append(row[0])
    indexes = tuple(indexes) # needed to match the formatting of SQL statement automatically, as it uses () not []
    search_statement = f"SELECT BookTitle,BookAuthor,BookImage, BookID FROM Book WHERE BookID IN {indexes} ORDER BY CASE BookID"
    for index in range(len(indexes)):
        search_statement = search_statement + f" WHEN {indexes[index]} THEN {index}"
    search_statement = search_statement + " END, BookID"
    print(search_statement)
    c.execute(search_statement)
    results_content = c.fetchall()[:4] # * need to check what is the total length of this field
    print(results_content)


    """User Based Recommendation"""
    user_recommendations = user_recommendation_algorithim.get_user_recommendations(picked_studentid=user_id)
    titles = [] # needs to be a list here so we can append new items
    for index,row in user_recommendations.iterrows():
        titles.append(row[0])
    titles = tuple(titles) # needed to match the formatting of SQL statement automatically, as it uses () not []
    search_statement = f"SELECT BookTitle,BookAuthor,BookImage, BookID FROM Book WHERE BookTitle IN {titles} ORDER BY CASE BookTitle"
    for index in range(len(titles)):
        search_statement = search_statement + f' WHEN "{titles[index]}" THEN {index}'
    search_statement = search_statement + " END, BookID"
    print(search_statement)
    c.execute(search_statement)
    results_user = c.fetchall() # * need to check what is the total length of this field
    results_user = random.sample(results_user, 4)
    print()
    print(results_user)

    close_database_link(conn)

    context_dict = {'random_book': random_book,'content_recommendations': results_content, 'user_recommendations':results_user}
    return render(request, 'main/index.html', context_dict)