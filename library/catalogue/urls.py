from django.views.generic import RedirectView
from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('search/',RedirectView.as_view(url='/catalogue/search/1'), name="search_default"),
    path('search/<page_num>', views.search, name="search"),
    path('detail/<book_num>', views.detail, name="detail"),
    path('borrow_post/<book_id>',views.borrow_post, name="borrow_post")

]