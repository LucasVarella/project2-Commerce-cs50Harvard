from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="createlisting"),
    path("auctions/<int:id>", views.list_auction, name="listauction"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("myauctions", views.my_auctions, name="myauctions"),
    path("categories", views.categories, name="categories"),
    path("auctions/closed/<int:id>", views.list_closed, name="listclosed")
    
]
