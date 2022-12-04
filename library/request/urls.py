from django.urls import path
from django.views.generic import RedirectView
from request import views

app_name = 'request'

urlpatterns = [
    path('create_order/', views.create_order, name="create_order"),
    path('list_order_teacher/', views.list_order_teacher, name="list_order_teacher",),
    path('list_order', views.order_list, name="order_list"),
    path('update_order/<order_id>', views.update_order, name="update_order"),
    path('approve_order/<order_id>', views.approve_order, name="approve_order"),
    path('reject_order/<order_id>', views.reject_order, name="reject_order"),
    path('',RedirectView.as_view(url='/request/list_order')),

]