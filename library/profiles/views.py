from multiprocessing import context
from time import strptime
from django.shortcuts import render

from django.http import HttpResponseRedirect

# third party plugins
from base.database import open_database_link,close_database_link, get_image_url, convert_date, add_months
from base.database import genre_options,genders,reg_classes

import datetime

# Create your views here.


def profile(request, profile_num):
    conn, c = open_database_link()

    # profile
    c.execute(f"SELECT * FROM Student WHERE StudentID={profile_num}")
    profile = c.fetchone()
    student_id, user_id, first_name,surname,email,dob,gender,reg_class = profile
    context_dict = {'student_id':student_id,'name':f'{first_name} {surname}', 'email':email, 'dob':dob, 'gender':gender, 'reg_class':reg_class }

    # books borrowed
    c.execute(f"SELECT books.BookTitle, books.BookAuthor, books.BookImage, Borrow.BorrowID, Borrow.BorrowDate, Borrow.ReturnDate FROM Borrow INNER JOIN books ON Borrow.BookID=books.BookID WHERE StudentID={profile_num}")
    borrow_list = c.fetchall()
    context_dict.update({'borrow_list': borrow_list})

    # books requested
    c.execute(f"SELECT BookName, BookAuthor, BookImage, RequestDate, RequestStatus FROM Request WHERE StudentID={profile_num}")
    request_list = c.fetchall()
    for request_book_num in range(len(request_list)):
        request_book = list(request_list[request_book_num])
        print(request_book[-1])
        if request_book[-1] == 'Ready': request_book.append('ready')
        elif request_book[-1] == 'Accepted': request_book.append('accepted')
        elif request_book[-1] == 'Rejected': request_book.append('rejected')
        else: request_book.append('pending')
        request_list[request_book_num] = request_book

    context_dict.update({'request_list': request_list})


    close_database_link(conn)

    return render(request, "profiles/profile.html", context_dict)

def return_book(request,borrow_id):
    conn,c = open_database_link()
    c.execute(f"SELECT BookID FROM borrow where BorrowID={borrow_id}")
    book_id = c.fetchone()[0]
    c.execute(f"SELECT BookTitle FROM books where BookID={book_id}")
    book_title = c.fetchone()[0]

    context_dict = {'borrow_id':borrow_id,'book_id':book_id,'book_title':book_title}
    return render(request, "profiles/confirm_return_book.html", context_dict)

def return_book_post(request,borrow_id):
    conn,c = open_database_link()
    c.execute(f"SELECT StudentID, BookID FROM borrow WHERE BorrowID={borrow_id}")
    student_id, book_id = c.fetchone()
    c.execute(f"Update books SET BookAvailability='In Shelf' where BookID={book_id}")
    c.execute(f"DELETE FROM borrow WHERE BorrowID={borrow_id}")
    close_database_link(conn)
    context_dict = {'borrow_id':borrow_id}
    return HttpResponseRedirect(f'/profiles/{student_id}')


def edit_account(request, student_id):
    conn, c = open_database_link()
    if request.method == 'POST':
        name,surname,email,dob,gender,reg = request.POST['name'],request.POST['surname'],request.POST['email'],request.POST['dob'],request.POST['gender'],request.POST['reg_class']
        c.execute(f"UPDATE Student SET StudentName='{name}', StudentSurname='{surname}', StudentEmail='{email}', \
        StudentDOB='{convert_date(dob)}', StudentGender='{gender}', StudentReg='{reg}' WHERE StudentID={student_id}")
        close_database_link(conn)
        return HttpResponseRedirect(f'/profiles/{student_id}')



    c.execute(f"SELECT * FROM Student WHERE StudentID={student_id}")
    student = c.fetchone()
    close_database_link(conn)
    student = list(student) + [convert_date(student[5])]
    context_dict = {'student':student, 'genders':genders, 'reg_classes':reg_classes}
    return render(request, 'profiles/edit_account.html', context_dict)





def extend_borrow(request,borrow_id):
    conn, c = open_database_link()
    c.execute(f"SELECT StudentID, BorrowDate, ReturnDate FROM Borrow WHERE BorrowID={borrow_id}")
    student_id,borrow_date, return_date = c.fetchone()
    return_date = add_months(datetime.datetime.strptime(return_date, "%d/%m/%Y"),1)
    print((return_date - datetime.datetime.strptime(borrow_date, "%d/%m/%Y")).days)
    # c.execute(f"UPDATE Borrow SET ReturnDate='5/12/2022' WHERE BorrowID={borrow_id}")

    if (return_date - datetime.datetime.strptime(borrow_date, "%d/%m/%Y")).days < 62:
        return_date = datetime.datetime.strftime(return_date, "%d/%m/%Y")
        c.execute(f"UPDATE Borrow SET ReturnDate='{return_date}' WHERE BorrowID={borrow_id}")

    close_database_link(conn)

    return HttpResponseRedirect(f'/profiles/{student_id}')



def update_request(request,request_id):
    conn, c = open_database_link()
    c.execute(f"SELECT BookName,BookAuthor,BookYear,BookGenre FROM Request WHERE RequestID={request_id}")
    request_book = c.fetchone()
    print(request_book)
    context_dict = {}
    return render(request, "profiles/update_request.html", context_dict)


# setup return page
# make return page work
# setup edit account details page, and make it update the DB
# setup the cancel and extend buttons
#