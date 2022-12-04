from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotFound

from base.database import open_database_link,close_database_link, slug_image_name,get_image_url, convert_date, add_months
from base.database import genre_options,genders,reg_classes
from base.settings import STATIC_DIR

import datetime

# Create your views here.

def order_list(request):
    conn, c = open_database_link()
    c.execute(f"SELECT Book.BookTitle, Book.BookAuthor, Book.BookImage, Request.RequestDate, Request.RequestStatus FROM Request INNER JOIN Book ON Request.BookID=Book.BookID WHERE Request.RequestStatus='Accepted'")
    request_list = c.fetchall()
    context_dict = {'request_list': request_list}
    close_database_link(conn)
    return render(request, 'request/list_order.html', context_dict)

def create_order(request):
    conn, c = open_database_link()

    if request.method == 'POST':
        # NEED to add in the image when I upload.
        user_id = 1
        title, author, year, genre = request.POST['title'], request.POST['author'], request.POST['year'], request.POST['genre']
        c.execute(f"INSERT INTO Book VALUES (NULL, '{title}', '{author}', {year}, '{genre}', '{slug_image_name(title)}', NULL, NULL, 1)")
        
        book_id = c.lastrowid
        today_date = datetime.datetime.now().strftime('%d/%m/%Y')
        print(today_date)
        c.execute(f"INSERT INTO Request VALUES (NULL, {user_id}, {book_id}, '{today_date}', NULL, 'Pending Confirmation')")
        close_database_link(conn)
        return HttpResponseRedirect(f"/profiles/{user_id}")

    context_dict = {'genre_options': genre_options}



    close_database_link(conn)
    return render(request, 'request/create_order.html', context_dict)

def list_order_teacher(request):
    conn, c = open_database_link()
    c.execute(f"SELECT Request.RequestID, Book.BookTitle, Book.BookAuthor, Book.BookImage, Request.RequestDate, Request.RequestStatus FROM Request INNER JOIN Book ON Request.BookID=Book.BookID WHERE Request.RequestStatus IN ('Accepted', 'Pending Confirmation', 'Rejected') ORDER BY CASE Request.RequestStatus WHEN 'Accepted' THEN 1 WHEN 'Pending Confirmation' THEN 2 WHEN 'Rejected' THEN 3 END ")
    request_list = c.fetchall()

    context_dict = {'request_list':request_list}
    close_database_link(conn)
    return render(request, "request/list_order_teacher.html", context_dict)

def update_order(request, order_id):
    user_id = 1
    print(request.POST, request.FILES)
    conn, c = open_database_link()
    c.execute(f"SELECT Request.StudentID, Request.RequestStatus, Book.BookTitle, Book.BookAuthor, Book.BookYear, Book.BookGenre, Book.BookImage FROM Request INNER JOIN Book ON Request.BookID=Book.BookID WHERE RequestID={order_id}")
    student_id, request_status, title,author,year,genre,image_name = c.fetchone()
    print(c.fetchone())
    if request_status != 'Accepted':
        return HttpResponseRedirect(f'/profiles/{student_id}')

    # ! NEED TO UPDATE THE SQL REQUEST WHEN ON BIG PC, make sure I manually set Availibility, also update the book itself to BookIsRequest=0
    # if request.method == 'POST':
    #     name,author,year,genre = request.POST['name'],request.POST['author'],request.POST['year'], request.POST['genre']
    #     image_url = get_image_url(name)
    #     try:
    #         upload = request.FILES['image_name']
    #         image = Image.open(upload)
    #         # for PNG images discarding the alpha channel and fill it with some color
    #         if image.mode in ('RGBA', 'LA'):
    #             background = Image.new(image.mode[:-1], image.size, '#fff')
    #             background.paste(image, image.split()[-1])
    #             image = background
    #         rgb_im = image.convert("RGB")
    #         rgb_im.save(STATIC_DIR + image_url)
    #     except MultiValueDictKeyError:
    #         pass

        # c.execute(f"UPDATE Request SET BookName='{name}', BookAuthor='{author}', BookYear={year}, BookGenre='{genre}', BookImage='{image_name}' WHERE RequestID={request_id}")
        # close_database_link(conn)
        # return HttpResponseRedirect(f'/profiles/{student_id}')


        # fss = FileSystemStorage()
        # file = fss.save(name, rgb_im)
        # file_url = fss.url(file)
    close_database_link(conn)
    context_dict = {'title':title, 'author': author, 'year':year,'genre':genre,'image_name':image_name, 'genre_options':genre_options, 'reg_classes':reg_classes}
    return render(request, "request/update_order.html", context_dict)


def approve_order(request, order_id):
    conn, c = open_database_link()
    c.execute(f"SELECT RequestStatus FROM Request WHERE RequestID={order_id}")
    request_status = c.fetchone()[0]
    if request_status in ('Pending Confirmation', 'Accepted', 'Rejected'):
        c.execute(f"UPDATE Request SET RequestStatus='Accepted' WHERE RequestID={order_id}")
    else:
        return HttpResponseNotFound('<h1>Cannot perform action on this Order Request</h1>')
    close_database_link(conn)
    return HttpResponseRedirect(f"/request/list_order_teacher")

def reject_order(request, order_id):
    conn, c = open_database_link()
    c.execute(f"SELECT RequestStatus FROM Request WHERE RequestID={order_id}")
    request_status = c.fetchone()[0]
    if request_status in ('Pending Confirmation', 'Accepted', 'Rejected'):
        c.execute(f"UPDATE Request SET RequestStatus='Rejected' WHERE RequestID={order_id}")
    else:
        return HttpResponseNotFound('<h1>Cannot perform action on this Order Request</h1>')
    close_database_link(conn)
    return HttpResponseRedirect(f"/request/list_order_teacher")