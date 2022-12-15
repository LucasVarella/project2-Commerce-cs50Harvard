from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class User(AbstractUser):
   watchlist = []
   
class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 60)
    date_time = models.DateTimeField(datetime.now())
    description = models.CharField(max_length=200)
    image_url = models.CharField(max_length=200, blank=True)
    init_bid = models.FloatField()
    price = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    category = models.CharField(max_length = 60, blank=True)
    active = models.BooleanField(default=True)
    
    
    def __str__(self) -> str:
        return f"{self.name} | By: {self.user}\n"     
   
class Bid(models.Model):
    value = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, default=False)
   
class Comment(models.Model):
    text = models.CharField(max_length = 150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=False)
    
  


