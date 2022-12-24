from django.contrib import admin

from .models import Auction, Bid, User, Comment, Watchlist, Category

# Register your models here.
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user")

class BidAdmin(admin.ModelAdmin):
     list_display = ("id", "auction", "value", "user")
    
class UserAdmin(admin.ModelAdmin):
    pass

        
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Watchlist)
admin.site.register(Category)