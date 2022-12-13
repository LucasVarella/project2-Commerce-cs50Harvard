from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from datetime import datetime

from .models import User, Auction, Bid

origin = ""

def index(request):
    
    auctions = Auction.objects.all()
         
    return render(request, "auctions/index.html", {
        "auctions": auctions
        })  

def login_view(request):
    global origin
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            
            
            if (origin == "create"):
                origin = ""
                return HttpResponseRedirect(reverse("createlisting"))
            else:
                origin = ""
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.", "alert_class": "alert-danger"
            })
    else:
        origin = ""
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    global login_user
    login_user = None
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    
    global login_user
    # POST
    if request.method == "POST":   
        auction = Auction()
        auction = Auction(name= request.POST["title"], date_time= datetime.now() , description= request.POST["description"], image_url= request.POST["image_url"], init_bid = request.POST["init_bid"], category = request.POST["category"], user= request.user)
        auction.save()   
        auctions = Auction.objects.all()
        return render(request, "auctions/index.html", {
            "auctions": auctions
        })
    
    # GET  
    else:      
        user = request.user
        if user.is_authenticated: 
            return render(request, "auctions/createlisting.html", {
                "user": user
            })
        else:
            global origin
            origin = "create"
            return render(request, "auctions/login.html", {
                "message": "Login first.", "alert_class": "alert-warning"
            })
            
def list_auction(request, id):
    
    bids = Bid.objects.filter(auction= id)
    id_auction = id
    user_auction = False
    your_bid = False
    
    if bids.last():   
        last_bid = bids.last()
    else:
        last_bid = None
    
    if request.method == 'POST':
        
        bid_value = float(request.POST['bid'])
        auction = Auction.objects.get(pk= id_auction)
        
        if request.user.is_authenticated:
            
            # Verify if the user loged is the user that created the auction 
            if request.user == auction.user:
                user_auction = True
                return render(request, "auctions/listauction.html",{
                                    "auction": auction, "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction
                                })
            else:
                
                user_auction = False  
                # Verify if have bids in the auction
                if last_bid is not None:
    
                    # Verify if the last bid pertences to loged user
                    if last_bid.user == request.user:
                        your_bid = True
                        return render(request, "auctions/listauction.html",{    
                                        "auction": auction, "msg": "Your bid is the last", "alert_class": "alert-danger", "bids": bids, "your_bid": your_bid
                                    })
                        
                    else:
                        
                        # Verify if the bid is higher than the last bid
                        if bid_value > auction.price:
                            
                            new_bid = Bid(value=bid_value, user= request.user, auction = auction)
                            new_bid.save()
                            auction.price = bid_value
                            auction.save()
                            your_bid = True
                            return render(request, "auctions/listauction.html",{
                                "auction": auction, "msg": "Your bid has been successfully registered!", "alert_class": "alert-success", "bids": bids, "your_bid": your_bid
                            })
                            
                        else:
                            return render(request, "auctions/listauction.html",{
                                "auction": auction, "msg": "Your bid needs to be higher than the last bid", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction
                            })
                
                # If is the first bid in the auction           
                else:
                    
                    # Verify if bid greater than or equal to the starting bid
                    if bid_value >= auction.init_bid:
                        new_bid = Bid(value=bid_value, user= request.user, auction = auction)
                        new_bid.save()
                        auction.price = bid_value
                        auction.save()
                        your_bid = True
                        
                        return render(request, "auctions/listauction.html",{
                            "auction": auction, "msg": "Your bid has been successfully registered!", "alert_class": "alert-success", "bids": bids, "your_bid": your_bid
                        })
                    
                    else:
                         
                        return render(request, "auctions/listauction.html",{
                                        "auction": auction, "msg": "Your bid needs to be greater than or equal to the starting bid", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction
                                    })
                        
        # If user is not authenticated                               
        else:
            user_auction = False  
            return render(request, "auctions/listauction.html",{
                        "auction": auction, "msg": "Your need to make a login first", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction
                    })
            
            
    # If method = "GET"  
    else:
        
        try:
            auction = Auction.objects.get(id= id)
        except:
            auction = None
        
        if auction is not None:
            
            if request.user.is_authenticated:
                
                if request.user == auction.user:
                    
                    return render(request, "auctions/listauction.html",{
                                    "auction": auction, "bids": bids, "user_auction": True
                                })
                else:
                    
                    if last_bid.user == request.user:
                        your_bid = True
                        return render(request, "auctions/listauction.html",{    
                                        "auction": auction, "msg": "Keep an eye on the auction!", "alert_class": "alert-success", "bids": bids, "your_bid": your_bid
                                    })
                    else:
                        
                        return render(request, "auctions/listauction.html",{
                                        "auction": auction, "bids": bids, "user_auction": False
                                    })
            else:
                return render(request, "auctions/listauction.html",{
                                    "auction": auction, "bids": bids, "user_auction": False
                                })
        
        else:
            return render(request, "auctions/listauction.html", {
                "msg": "This Auction don't exist!"
            } )
                 
def watchlist(request):
    auctions = Auction.objects.all()
         
    return render(request, "auctions/index.html", {
        "auctions": auctions
        })
    
def list_closed(request, id):
    auction = Auction.objects.get(pk=id)
    bids = Bid.objects.filter(auction = id)
    
    if request.method == "POST":
        
        
        return render(request, "auctions/listclosed.html",{
            "auction": auction, "msg": f"Auction Closed! The higher bid pertence to {bids.last().user}", "alert_class": "alert-success"
            })
        