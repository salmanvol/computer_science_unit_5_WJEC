from django.urls import path
from profiles import views

app_name = 'profiles'

urlpatterns = [
    path('<profile_num>', views.profile, name="profile"),
    path('return_book/<borrow_id>', views.return_book, name="return_book"),
    path('return_book_post/<borrow_id>/', views.return_book_post, name="return_book_post"),
    path('edit_account/<student_id>/', views.edit_account, name="edit_account"),
    path('extend_borrow/<borrow_id>/', views.extend_borrow, name="extend_borrow"),
    path('update_request/<request_id>/', views.update_request, name="update_request")

]