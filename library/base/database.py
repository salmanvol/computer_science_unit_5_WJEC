from ast import Raise
from email.mime import image
from logging import raiseExceptions
import sqlite3
import hashlib
# for add_months function
import datetime,calendar

genre_options = (
    ('Action And Adventure', 'action_and_adventure'),
    ('Classics','classics'),
    ('Comic Book','comic_book'),
    ('Detective and Mystery','detective_and_mystery'),
    ('Fantasy','fantasy'),
    ('Historical Fiction','historical_fiction'),
    ('Horror','horror'),
    ('Literary Fiction','literary_fiction'),
    ('Romance','romance'),
    ('Science Fiction','science_fiction'),
    ('Short Stories','short_stories'),
    ('Suspense and Thrillers','suspense_and_thrillers'),
    ('Women Fiction','women_fiction'),
    ('Biography','biography'),
    ('Cookbooks','cookbooks'),
    ('History','history'),
    ('Memoir','memoir'),
    ('Poetry','poetry'),
    ('Self-Help','self_help'),
    ('True Crime','true_crime'),
    ('Children','children'),
    ('Non-Fiction','non_fiction'),
    ('Fiction','fiction'),

    )

genders = (
    ('Male','male'),
    ('Female','female'),
)

reg_classes = ('7A','7B','7C','8A','8B','8C','9A','9B','9C','10A','10B','10C','11A','11B','11C','12A','12B','12C',)

def open_database_link():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    return conn, c

def close_database_link(conn):
    conn.commit()
    conn.close()

# ? Functions

def slug_image_name(image_name: str):
    image_name_slug = image_name.lower().replace(' ','_')
    return image_name_slug

def get_image_url(image_name: str):
    image_url = '/media/images/' + f'{slug_image_name(image_name)}.jpg'
    return image_url

def convert_date(date):
    if '/' in date:
        date = date.split('/')
        return f"{date[2]}-{date[1]}-{date[0]}"
    elif '-' in date:
        date = date.split('-')
        return f"{date[2]}/{date[1]}/{date[0]}"
    raise('not a valid entry')


def get_pretty_genre_value(genre_slug):
    for genre_display, genre_value in genre_options:
        if genre_value == genre_slug:
            return genre_display
    raise KeyError(f'{genre_slug} does not match any of the options')

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.datetime(year, month, day)



#function to fetch password
def password_fetch(id):
    conn, c = open_database_link()
    try:
        c.execute(f"select UserPassword from Account where UserID={id}")
        data=c.fetchone()
        close_database_link(conn)
        if data != None: 
            return {'pwd':data}
        else :
            return {'status':'400'}
    except Exception as e:
        close_database_link(conn)
        return {'Error',str(e)}
        

# function to insert into table
def insert__password(name,email,password):
    conn, c = open_database_link()
    try:
        c.execute(f"Insert into  Account values (NULL,'{name}','{email}','{password_hash(password)}')")
        close_database_link(conn)
        return {'status':'Data inserted successfully'}
    except Exception as e:
        close_database_link(conn)
        return {'Error',str(e)}

#function to encrypt your password  
def password_hash(pwd):
    hash_object = hashlib.md5(bytes(str(pwd), encoding='utf-8'))
    hex_dig= hash_object.hexdigest()
    return hex_dig    


  

# print(Insert('bob','bob@email.com',pass_encrypted))
# print(password_fetch(1))

conn, c = open_database_link()

try:
    c.execute("""CREATE TABLE Account (
    UserID integer primary key autoincrement,
    Username text,
    UserEmail nvarchar(255),
    UserPassword text
    )""")
    c.execute("""CREATE TABLE Student (
        StudentID integer primary key autoincrement,
        UserID integer,
        StudentName text,
        StudentSurname text,
        StudentEmail nvarchar(255),
        StudentDOB text,
        StudentGender text,
        StudentReg text,
        FOREIGN KEY(UserID) REFERENCES Account(UserID)
    )""")  
    c.execute("""CREATE TABLE Teacher (
        TeacherID integer primary key autoincrement,
        UserID integer,
        TeacherName text,
        TeacherSurname text,
        TeacherEmail nvarchar(255),
        TeacherRole text,
        TeacherReg text,
        FOREIGN KEY(UserID) REFERENCES Account(UserID)
    )""")
    c.execute("""CREATE TABLE Request (
        RequestID integer primary key autoincrement,
        StudentID integer,
        BookID integer,
        RequestDate text,
        RequestAcceptDate text,
        RequestStatus text,
        FOREIGN KEY(BookId) REFERENCES Book(BookID),
        FOREIGN KEY(StudentID) REFERENCES Student(StudentID)
    )""") 
    c.execute("""CREATE TABLE Book (
        BookID integer primary key autoincrement,
        BookTitle text,
        BookAuthor text,
        BookYear integer,
        BookGenre text,
        BookImage text,
        BookAvailability text,
        BookLocation text,
        BookIsRequest integer
    )""")    
    c.execute("""CREATE TABLE Tag (
        TagID integer primary key autoincrement,
        TagName text,
        TagSlug integer
    )""")
    c.execute("""CREATE TABLE BookTag (
        BookTagID integer primary key autoincrement,
        BookID integer,
        TagID interger,
        TagOrder integer,
        FOREIGN KEY(BookID) REFERENCES Book(BookID),
        FOREIGN KEY(TagID) REFERENCES Book(TagID)
    )""")   
    c.execute("""CREATE TABLE Borrow (
        BorrowID integer primary key autoincrement,
        StudentID integer,
        BookID integer,
        BorrowDate text,
        ReturnDate text,
        FOREIGN KEY(StudentID) REFERENCES Student(StudentID),
        FOREIGN KEY(BookID) REFERENCES Book(BookID) 
    )""")
except Exception as e:
    print(e)
# c.execute("INSERT INTO Book VALUES (NULL, 'Demon Dentist', 'David Walliams', 2013, 'children', 'demon_dentist','In Shelf', 'A12', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Gangster Granny', 'David Walliams', 2007, 'children', 'gangster_granny', 'Borrowed', 'A14', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Gangster Granny', 'David Walliams', 2007, 'children', 'gangster_granny', 'Borrowed', 'A14', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Minecraft Handbook', 'Mojang', 2011, 'short_stories', 'minecraft_handbook', 'Overdue', 'C5', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Percy Jackson And The Lighting Thief', 'Rick Riordan', 2020, 'action_and_adventure', 'percy_jackson_and_the_lighting_thief', 'Unavailable', 'D3', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'The Last Olympian', 'Rick Riordan', 2021, 'Non-Fiction', 'the_last_olympian', 'In Shelf', 'A2', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Ice Monster', 'David Walliams', 2005, 'children', 'ice_monster', 'Borrowed', 'C4', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")

# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', 'Unavailable', 'A5', 0)")

# print(insert__password('John Pinedia','johpin@school.com','password'))
# print(password_fetch(1))
# c.execute("INSERT INTO Student VALUES (NULL, 1, 'John', 'Pinedia', 'johpin@school.com', '01/06/1999', 'male', '12C')")
# c.execute("INSERT INTO Borrow VALUES (NULL, 1, 4, '21/11/2022', '27/12/2022')")
# c.execute("INSERT INTO Borrow VALUES (NULL, 1, 5, '11/11/2022', '11/12/2022')")
# c.execute("INSERT INTO Request VALUES (NULL, 1, 16, '11/11/2022', NULL, 'Pending Confirmation')")
# c.execute("INSERT INTO Request VALUES (NULL, 1, 17, '9/6/2022', '21/7/20222', 'Ready')")
# c.execute("INSERT INTO Request VALUES (NULL, 1, 18, '10/9/2022', '21/10/2022', 'Rejected')")
# c.execute("INSERT INTO Request VALUES (NULL, 1, 19, '21/8/2022', '21/8/2022', 'Accepted')")
# c.execute("INSERT INTO Request VALUES (NULL, 1, 20, '15/9/2022', '15/9/2022', 'Accepted')")
# c.execute("INSERT INTO Book VALUES (NULL, 'Midnight Gang', 'David Walliams', 1995, 'children', 'midnight_gang', NULL, NULL, 1)")
# c.execute("INSERT INTO Book VALUES (NULL, 'The Last Olympian', 'Rick Riordan', 2021, 'Non-Fiction Story', 'the_last_olympian', 'In Shelf', 'A2', 1)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Gangster Granny', 'David Walliams', 2007, 'children', 'gangster_granny', NULL, NULL, 1)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Ice Monster', 'David Walliams', 2005, 'action_and_adventure', 'ice_monster', NULL, NULL, 1)")
# c.execute("INSERT INTO Book VALUES (NULL, 'Percy Jackson And The Lighting Thief', 'Rick Riordan', 2020, 'action_and_adventure', 'percy_jackson_and_the_lighting_thief', 'Unavailable', 'D3', 1)")


close_database_link(conn)