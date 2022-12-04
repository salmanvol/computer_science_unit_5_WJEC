from django.http import HttpResponseRedirect
from django.shortcuts import render

# third party plugins
from base.database import open_database_link,close_database_link, get_image_url,genre_options, get_pretty_genre_value, add_months
import datetime

# Create your views here.

# * for tags, use SELECT * FROM books WHERE tags IN ('Germany', 'UK')
# & actually probably don't need this

search_constructor = (
    ('title','BookTitle'),
    ('author','BookAuthor'),
    ('release_date','BookYear'),
    ('genre','BookGenre')
)



def navigation_button_url(full_url,page_num, change_increment):
    return full_url.replace("search/"+ str(page_num), "search/" + str(page_num+(change_increment)))



# ? Views
def search(request, page_num=1):
    results_parsed = []
    page_num = int(page_num) 
    # get the upper and lower bounds of what range of books we will have
    lower_bound, upper_bound = (page_num -1) * 8, page_num * 8
    try:
        print(request.GET)
        title = request.GET['title']
        conn, c = open_database_link()
        filter_query = "SELECT * FROM Book WHERE BookIsRequest=0"
        for column in search_constructor:
            print(column)
            if request.GET[column[0]] != "":
                filter_query = filter_query +" AND " +  f"{column[1]} LIKE '%{request.GET[column[0]]}%'"
        print(filter_query)
        c.execute(filter_query)
        results = c.fetchall()
        close_database_link(conn)
        books_len = len(results) # get the total number of books
        max_num_page = int(books_len / 8) + (books_len / 8 % 1 > 0) if books_len > 8 else 1
        # if lower_bound > books_len:
        #     print('resetting URL')
        #     return HttpResponseRedirect(reverse('catalogue:search',kwargs={'page_num':1,}))
        results = results[lower_bound:upper_bound]

        # send back all the form GET values
        title,author,release_date,genre,tags = request.GET['title'],request.GET['author'],request.GET['release_date'],request.GET['genre'],request.GET['tags']
    except Exception as e:
        print('error in search filtering:',e)
        conn, c = open_database_link()
        c.execute(f"SELECT * FROM Book WHERE BookIsRequest=0")
        results = c.fetchall()
        close_database_link(conn)
        books_len = len(results) # get the total number of books
        max_num_page = int(books_len / 8) + (books_len / 8 % 1 > 0) if books_len > 8 else 1
        results = results[lower_bound:upper_bound]
        title,author,release_date,genre,tags = ['','','','','']
    
    context_dict = {'title':title, 'author': author, 'release_date':release_date,'genre':genre,'tags':tags}

    for book in results:
        id,title,author,image_name = book[0],book[1], book[2], book[5]
        image_url = get_image_url(image_name)
        if len(title) > 20:
            title = title[0:20] + '...'
        results_parsed.append((id,title,author,image_url))


    # * get the page number to dispaly in the front end and prepare context_dict
    full_url = request.build_absolute_uri()
    prev_page, next_page = navigation_button_url(full_url,page_num, -1) if page_num > 1 else (full_url), navigation_button_url(full_url,page_num,+1)


    context_dict.update({'current_page': page_num, 'total_pages':max_num_page, 'prev_page': prev_page, 'next_page': next_page, 'results':results_parsed, 'genre_options':genre_options}) 
    return render(request, "catalogue/search.html", context_dict)

def detail(request, book_num):
    conn, c = open_database_link()
    c.execute(f"SELECT * FROM Book WHERE BookID={book_num}")
    book = c.fetchone()
    close_database_link(conn)

    id, title, author, release_date, genre, image_name, availability, location, is_request = book
    image_url = get_image_url(image_name)
    genre_pretty_value = get_pretty_genre_value(genre_slug=genre)

    borrow_button_enabled__css= "True"
    if 'In Shelf' in availability: availability = availability + ': ' + location
    else: borrow_button_enabled__css = "btn--link--inactive"

    availability_css = ('in-shelf' if 'In Shelf' in availability else 'borrowed' if 'Borrowed' in availability else 'overdue' if 'Overdue' in availability else 'unavailable')
    context_dict = {
        'id':id,
        'title':title,
        'author':author,
        'release_date': release_date,
        'genre': genre_pretty_value,
        'availability':availability,
        'availability_css':availability_css,
        'image_url': image_url,
        'borrow_button_enabled__css': borrow_button_enabled__css
    }

    return render(request, "catalogue/detail.html", context_dict)


def borrow_post(request, book_id):
    user_id = 1
    conn, c = open_database_link()
    c.execute(f"SELECT BookAvailability FROM Book WHERE BookID={book_id}")
    availability = c.fetchone()[0]
    if availability == 'In Shelf':
        borrow_date = datetime.datetime.strftime(datetime.datetime.now(), "%d/%m/%Y")
        return_date = datetime.datetime.strftime(add_months(datetime.datetime.now().date(),1), "%d/%m/%Y")
        print(return_date)
        c.execute(f"INSERT INTO Borrow VALUES (NULL, {user_id}, {book_id}, '{borrow_date}', '{return_date}')")
        c.execute(f"UPDATE Book SET BookAvailability='Borrrowed' WHERE BookID={book_id}")
        close_database_link(conn)
        return HttpResponseRedirect(f"/profiles/{user_id}")
    return HttpResponseRedirect(f"/catalogue/detail/{book_id}")
