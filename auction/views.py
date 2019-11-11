from django.views import View
from django.http import HttpResponseRedirect
from user.forms import CreateAuctionForm, ConfAuctionForm
from django.shortcuts import render, get_object_or_404
from auction.models import Auction
from django.contrib import messages
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.urls import reverse
from django.db import OperationalError, transaction
from django.utils.translation import gettext as _
from django.utils import translation
import requests
import json
from decimal import Decimal

#Function for showing all active and not banned auctions
def index(request):
    if request.user.is_superuser:
        aucts = Auction.objects.filter(active=True, banned=False)
        bannedAucts = Auction.objects.filter(banned=True)
        currency = "€"
        return render(request, "base.html", {'aucts': aucts, 'currency':currency, 'bannedAucts':bannedAucts})
    else:
        aucts = Auction.objects.filter(active=True, banned=False)
        currency = "€"
        return render(request, "base.html", {'aucts': aucts, 'currency':currency})


#search done with object filtering
def search(request):
    title = request.POST['title']
    if request.method == 'POST':
        results = Auction.objects.filter(title__contains=title, banned=False)
        return render(request, 'base.html', {'aucts': results})

#get for getting the form to create auction, post to post filled form to save the auction
class CreateAuction(View):
    def get(self, request):
        if request.user.is_authenticated:
            form = CreateAuctionForm()
            return render(request, 'create.html', {'form': form})
        else:
            return HttpResponseRedirect(reverse("signup"))

    def post(self, request):
        form = CreateAuctionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            title = cd['title']
            description = cd['description']
            minimum_price = cd['minimum_price']
            deadline_date = cd['deadline_date']
            form = ConfAuctionForm({"title": title, "description": description, "minimum_price": minimum_price,
                                    "deadline_date": deadline_date})
            return render(request, 'save_auction.html', {'form': form, 'title': title})
        else:
            return render(request, 'create.html', {'form': form})
#Function connected to save_auction.html
def saveAuction(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        minimum_price = request.POST.get('minimum_price', '')
        deadline_date = request.POST.get('deadline_date', '')
        deadline = datetime.strptime(deadline_date, '%Y-%m-%d %H:%M:%S') #deadline in format required
        if deadline < (datetime.now() + timedelta(hours=72)): #Checking that deadline meets requirements
            saveAuctionMessage = _("Deadline must be at least 72 hours from now")
            return render(request, 'save_auction.html', {'title': title, 'saveAuctionMessage': saveAuctionMessage})
        else:
            auct=Auction(seller=request.user ,title=title, description=description, minimum_price=minimum_price,
                         deadline_date=deadline_date)
            auct.save()
            send_mail('Auction added successfully.', 'Auction titled ' + str(auct.title) + ' added successfully. Description: '
                  + str(auct.description) + '. Link to your auction: http://127.0.0.1:8000/auction/' + str(auct.id),
                      'admin@admin.com', [request.user.email]) #Sending link to auction
            return HttpResponseRedirect(reverse("auction:index"))
    else:
        return HttpResponseRedirect(reverse("auction:index"))

#get for getting form for auction editing, post for posting edited version of the auction
class EditAuction(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            user = request.user
            auct = get_object_or_404(Auction, id=id)
            if auct.seller == user.username: #check if user has rights to edit the auction
                return render(request, "edit.html", {"auct": auct})
            else:
                editauctionmessage = _("That is not your auction to edit")
                return render(request, 'edit.html', {"editauctionmessage": editauctionmessage})
        else:
            return HttpResponseRedirect(reverse("signin"))

    def post(self, request, id):
        auct = Auction.objects.get(id=id)
        description = request.POST["description"].strip() #New description from the form to auction's description
        auct.description = description
        auct.save()
        return HttpResponseRedirect(reverse("auction:index"))


#Since bidding was not as a class, I used if request.method for get and post situations
def bid(request, item_id):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            auct = get_object_or_404(Auction, id=item_id)
            if auct.seller == user.username: #check if user has rights to bid
                bidauctionmessage = _("You cannot bid on your own auctions")
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            else:
                return render(request, "bid.html", {"auct": auct})
        else:
            return HttpResponseRedirect(reverse("signin"))

    if request.method == "POST":
        if request.user.is_authenticated:
            auct = Auction.objects.get(id=item_id)
            new_price = float(request.POST["minimum_price"].strip())
            minimum_price = float(auct.minimum_price) #convert to float to enable comparison to old price
            deadline_date = auct.deadline_date
            deadline = datetime.strptime(deadline_date, '%Y-%m-%d %H:%M:%S')
            #if-sentences for every possible scenario where bidding should be aborted
            if auct.active == False:
                bidauctionmessage = _("You can only bid on active auctions")
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            if deadline <= datetime.now():
                bidauctionmessage = _("You can only bid on active auctions")
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            if new_price <= minimum_price:
                bidauctionmessage = _("New bid must be greater than the current bid for at least 0.01")
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            else: #Everything is fine
                auct.minimum_price = new_price
                auct.bidder = request.user.username
                auct.bidder_email = request.user.email
                auct.save()
                send_mail('You have bid to an auction.',
                          'Auction titled ' + str(auct.title) + ' has a currently winning bid placed by you.', 'admin@admin.com', [auct.bidder_email])
                send_mail('Auction where you are the seller has been bid.',
                          'Auction titled ' + str(auct.title) + ' has been bid by one of our users.', 'admin@admin.com', [auct.seller_email])
                message = "You has bid succesfully"
                return render(request, 'base.html', {"message": message})

#Again used request.method for get and post
def ban(request, item_id):
    if request.method == "GET":
        if request.user.is_superuser:
            user = request.user
            auct = get_object_or_404(Auction, id=item_id)
            return render(request, "ban.html", {"auct": auct})

    if request.method == "POST":
        auct = Auction.objects.get(id=item_id)
        auct.banned = True
        auct.active = False
        saved = False
        try: #Auction exists and is bannable
            with transaction.atomic():
                auct.save()
                saved = True
                message=_("Ban succesfully")
                #Mails for bidder and seller
                send_mail('Auction you have bid has been banned.',
                          'Auction titled ' + str(auct.title) + ' has been banned.',
                          'admin@admin.com', [auct.bidder_email])
                send_mail('Auction where you are the seller has been banned.',
                          'Auction titled ' + str(auct.title) + ' has been banned.', 'admin@admin.com',
                          [auct.seller_email])
                return render(request, "base.html", {"message": message})
        except OperationalError: #Auction can't be found
            messages.add_message(request, messages.ERROR, "Something went wrong. Please try again.")
            return render(request, "ban.html", {"auct": auct})

#Resolving starts with get request to auction/resolve by authenticated user
def resolve(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            aucts = Auction.objects.all()
            resolved=[]
            for auct in aucts:
                if datetime.now() > auct.deadline_date: #Check if deadline has been passed
                    resolved.append(auct.title)
                    auct.active=False
                    bidderEmail = auct.bidder_email
                    sellerEmail = auct.seller_email
                    #send mail to bidder and seller that auction has been resolved
                    send_mail('Auction you have bid has been resolved.',
                          'Auction titled ' + str(auct.title) + ' has been resolved.', 'admin@admin.com', [bidderEmail])
                    send_mail('Auction where you are the seller has been resolved.',
                          'Auction titled ' + str(auct.title) + ' has been resolved.', 'admin@admin.com', [sellerEmail])
                return render(request, "resolve.html", {"resolved": resolved})
        else:
            return HttpResponseRedirect(reverse("signin"))

#Used lab instructions as an example for language changing
def changeLanguage(request, lang_code):
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    if lang_code=="sv":
        changeLanguageMessage="Language has been changed to Swedish"
    if lang_code=="en":
        changeLanguageMessage = "Language has been changed to English"
    return render(request, "base.html", {"changeLanguageMessage": changeLanguageMessage})
    #return HttpResponseRedirect(reverse("auction:index"))


def changeCurrency(request, currency_code):
    if currency_code == "usd":
        currencyFrom ="EUR"
        currencyTo="USD"
        url = "https://api.exchangeratesapi.io/latest?base=" + currencyFrom #Found this api good for this purpose
        response = requests.get(url)
        data = response.text
        parsed = json.loads(data) #Load currency rates to a variable
        rates=parsed["rates"]
        for currency, rate in rates.items(): #Loop currency rates until needed rate is found
            if currency == currencyTo:
                ConversionRate=Decimal(str(rate)) #Decimal object needed for arithmetic operations
        aucts = Auction.objects.filter(active=True, banned=False)
        for auct in aucts: #Loop through auctions and perform multiplication by currency rate
            auct.minimum_price = auct.minimum_price * ConversionRate
        currency = "$" #Display information about currency change
        message = "Currency has been changed to USD"
        return render(request, "base.html", {'aucts': aucts, 'currency': currency, 'message':message})
    if currency_code == "eur": #This was a lazy choice
        aucts = Auction.objects.filter(active=True, banned=False)
        currency = "€"
        message = "Currency has been changed to EUR"
        return render(request, "base.html", {'aucts': aucts, 'currency': currency, 'message':message})


