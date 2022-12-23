from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from datetime import datetime

from .models import User, Auction, Bid, Comment, Watchlist, Category

origin = ""

def index(request):
    
    auctions = Auction.objects.all()
        
        
    return render(request, "auctions/index.html", {
        "auctions": auctions, "title": "Active Listings"
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
            "auctions": auctions, "title": "Active Listings"
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
    
    # Catch the last bid, if have
    try:
        bids = Bid.objects.filter(auction= id)
        last_bid = bids.last()
    except: 
        last_bid = None
    
    # Catch comments of auction, if have
    try:
        comments = Comment.objects.filter(auction= id)
    except: 
        comments = None
    
    # Parameters to verifications
    id_auction = id
    user_auction = False
    your_bid = False
    
    
    if request.method == 'POST':
        
        auction = Auction.objects.get(pk= id_auction)
        
        your_bid = False
        if last_bid != None:
            if last_bid.user == request.user:
                your_bid = True
            else:
                your_bid = False
        
        # Catch watchlist status   
        try:
            watchlist_item = Watchlist.objects.get(user= request.user, auction= auction)
            in_watchlist = True   
        except:
            in_watchlist = False
        
        # Verify if post's origin by add a whatchlist
        try:
            watchlist = request.POST['watchlist']
        except:
            watchlist = False
        
        
        # WATCHLIST POST    
        if watchlist != False:
            
            try:
                watchlist_item = Watchlist.objects.get(user= request.user, auction= auction)
                watchlist_item.delete()
                in_watchlist = False  
        
            except:  
                add_item = Watchlist(user= request.user, auction= auction)
                add_item.save()
                in_watchlist = True      
            
            if auction.active == True:
            
                if your_bid != True:
                    return render(request, "auctions/listauction.html",{
                                                    "auction": auction, "alert_class": "alert-success", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist, "your_bid": your_bid
                                                })
                else:
                    return render(request, "auctions/listauction.html",{
                                                    "auction": auction, "alert_class": "alert-success", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist, "your_bid": your_bid, "msg_last": "Keep an eye on the auction! 👀"
                                                })
            else:
                   return render(request, "auctions/listclosed.html",{
                                                "auction": auction, "alert_class": "alert-success", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist, "your_bid": your_bid, "msg": f"This auction is closed, the winning bid belongs to {bids.last().user}"
                                            })
        else:
            
            # Verify if post's origin by add a comment
            try:
                comment = request.POST['text_comment']
            except:
                comment = False
            
            # BID POST    
            if comment == False:
                
                bid_value = float(request.POST['bid'])
                if request.user.is_authenticated:
                    
                    # Verify if the user loged is the user that created the auction 
                    if request.user == auction.user:
                        user_auction = True
                        return render(request, "auctions/listauction.html",{
                                            "auction": auction, "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist
                                        })
                    else:
                        
                        user_auction = False  
                        # Verify if have bids in the auction
                        if last_bid is not None:
            
                            # Verify if the last bid pertences to loged user
                            if last_bid.user == request.user:
                                your_bid = True
                                return render(request, "auctions/listauction.html",{    
                                                "auction": auction, "msg": "Your bid is the last", "alert_class": "alert-danger", "bids": bids, "your_bid": your_bid, "comments":  comments, "in_watchlist": in_watchlist, "msg_last": "Keep an eye on the auction! 👀"
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
                                        "auction": auction, "msg": "Your bid has been successfully registered!", "alert_class": "alert-success", "bids": bids, "your_bid": your_bid, "comments":  comments, "in_watchlist": in_watchlist
                                    })
                                    
                                else:
                                    return render(request, "auctions/listauction.html",{
                                        "auction": auction, "msg": "Your bid needs to be higher than the last bid", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist
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
                                    "auction": auction, "msg": "Your bid has been successfully registered!", "alert_class": "alert-success", "bids": bids, "your_bid": your_bid, "comments":  comments, "in_watchlist": in_watchlist
                                })
                            
                            else:
                                
                                return render(request, "auctions/listauction.html",{
                                                "auction": auction, "msg": "Your bid needs to be greater than or equal to the starting bid", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist
                                            })
                                
                # If user is not authenticated                               
                else:
                    user_auction = False  
                    return render(request, "auctions/listauction.html",{
                                "auction": auction, "msg": "Your need to make a login first", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction, "comments":  comments
                            })   
                    
            # Comment POST                
            else:        
            
                if request.user.is_authenticated:
                        
                        if request.user != auction.user:
                            comment = Comment(text= request.POST['text_comment'], user= request.user, auction= auction)
                            comment.save()
                            comments = Comment.objects.filter(auction= id)
                            
                            return render(request, "auctions/listauction.html",{
                                            "auction": auction, "msg_comment": "Comment add with sucess!", "alert_class": "alert-success", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist, "your_bid": your_bid
                                        })
                            
                        else:
                            return render(request, "auctions/listauction.html",{
                                            "auction": auction, "msg": "Your can't comment to yourself", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction, "comments":  comments, "in_watchlist": in_watchlist, "your_bid": your_bid
                                        })
                else: 
                    return render(request, "auctions/listauction.html",{
                                    "auction": auction, "msg": "Your need to authenticated first!", "alert_class": "alert-danger", "bids": bids, "user_auction": user_auction, "comments":  comments
                                })
                    
                    
            
    # If method = "GET"  
    else:
        
        try:
            auction = Auction.objects.get(id= id)
            
        except:
            auction = None
        
        if auction is not None:
            
            # Catch watchlist status   
            try:
                watchlist_item = Watchlist.objects.get(user= request.user, auction= auction)
                in_watchlist = True   
            except:
                in_watchlist = False
                
            if auction.active == True:
                
                if request.user.is_authenticated:
                    
                    if request.user == auction.user:
                        
                        return render(request, "auctions/listauction.html",{
                                        "auction": auction, "bids": bids, "user_auction": True, "comments":  comments
                                    })
                    else:
                        
                        if last_bid is not None:
                            
                            if last_bid.user == request.user:
                                your_bid = True
                                return render(request, "auctions/listauction.html",{    
                                                "auction": auction, "msg_last": "Keep an eye on the auction! 👀", "alert_class": "alert-success", "bids": bids, "your_bid": your_bid, "comments":  comments, "in_watchlist": in_watchlist
                                            })
                            
                            else:
                                return render(request, "auctions/listauction.html",{
                                            "auction": auction, "bids": bids, "user_auction": False, "comments":  comments, "in_watchlist": in_watchlist
                                        })
                        else:
                            
                            return render(request, "auctions/listauction.html",{
                                            "auction": auction, "bids": bids, "user_auction": False, "comments":  comments, "in_watchlist": in_watchlist
                                        })
                else:
                    return render(request, "auctions/listauction.html",{
                                        "auction": auction, "bids": bids, "user_auction": False, "comments":  comments
                                    })
            
            else:
                
                return render(request, "auctions/listclosed.html",{
                                        "auction": auction, "bids": bids, "user_auction": False, "msg": f"This auction is closed, the winning bid belongs to {bids.last().user}", "alert_class": "alert-success", "comments":  comments, "in_watchlist": in_watchlist
                                    })
                
        
        else:
            return render(request, "auctions/listauction.html", {
                "msg": "This Auction don't exist!"
            } )
                 
def watchlist(request):
    
    watchlist = Watchlist.objects.filter(user= request.user)
    auctions = []
    for item in watchlist:
        auctions.append(item.auction)
         
    return render(request, "auctions/watchlist.html", {
        "auctions": auctions
        })
    
def list_closed(request, id):
    
    try:
        auction = Auction.objects.get(pk=id)
    except:
        auction = False
    
    if auction != False:
        
        try:
            bids = Bid.objects.filter(auction = id)
        except:
            bids = False
         
    if request.method == "POST":
        
        if bids:
            auction.active = False
            auction.save()
            
            return render(request, "auctions/listclosed.html",{
                "auction": auction, "msg": f"Auction is closed, the winning bid belongs to {bids.last().user}", "alert_class": "alert-success"
                })
        
        else:
            
            auction.delete()
            
            return render(request, "auctions/listclosed.html", {
                "msg_delete": "Auction delete!", "alert_class": "alert-success"
            })
        
    else:
       
        if auction == False:
                return HttpResponseRedirect("/")
        else:
            
            if auction.active == False:
                
                return render(request, "auctions/listclosed.html",{
                    "auction": auction, "msg": f"This auction is closed, the winning bid belongs to {bids.last().user}", "alert_class": "alert-success"
                    })
                
            else:
                return HttpResponseRedirect("/")
            
def my_auctions(request):
    
    my_auctions = Auction.objects.filter(user= request.user)
           
    return render(request, "auctions/myauctions.html", {
        "auctions": my_auctions
        })
    
def categories(request):
    categories = ['Toy', 'Woman', 'Eletronic', 'Home']
    auctions_filtered = []
    
    if request.method == "POST":
        active_category = request.POST['category']
        
        auctions = Category.objects.filter(name= active_category)
        
        for auction in auctions:
            
            
            auctions_filtered.append(auction.auction)
        
        
        return render(request, "auctions/categories.html", {
            "categories": categories, "auctions": auctions_filtered
        })
    else:
        return render(request, "auctions/categories.html", {
            "categories": categories 
        })
    
    