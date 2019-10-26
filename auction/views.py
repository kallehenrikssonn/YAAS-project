from django.views import View
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from user.forms import CreateAuctionForm, ConfAuctionForm, EditAuctionForm, BidAuctionForm
from django.shortcuts import render, redirect, get_object_or_404
from auction.models import Auction, Email, BidAuction
from django.contrib import messages
from django.core.mail import send_mail, send_mass_mail
from datetime import datetime, timedelta
from django.urls import reverse
from django.db import IntegrityError, OperationalError, transaction
from django.template.loader import render_to_string
from django.contrib.auth.models import User
import json


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

"""def auctions(request):
    aucts = Auction.objects.order_by('-deadline_date')
    return render(request, "base.html", {'aucts': aucts})"""

"""def index(request):
    print(request.headers)
    print("creating response...")
    html = "<html><body>Hello! <br> <p> This was your request: %s %s <p> sent from the following browser: %s </body></html>" % (
    request.method, request.path, request.headers['User-Agent'])
    return HttpResponse(html)"""

"""def search(request):
    query = request.GET.get('q')
    aucts = Auction.objects.filter(
        Q(title__icontains=query)
    return render(request, 'search.html', {'aucts': aucts})"""

def search(request):
    title = request.POST['title']
    if request.method == 'POST':
        results = Auction.objects.filter(title__contains=title, banned=False)
        return render(request, 'base.html', {'aucts': results})


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

def saveAuction(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        minimum_price = request.POST.get('minimum_price', '')
        deadline_date = request.POST.get('deadline_date', '')
        deadline = datetime.strptime(deadline_date, '%Y-%m-%d %H:%M:%S')
        if deadline < (datetime.now() + timedelta(hours=72)):
            saveAuctionMessage = "Deadline must be at least 72 hours from now"
            return render(request, 'save_auction.html', {'title': title, 'saveAuctionMessage': saveAuctionMessage})
        else:
            auct=Auction(seller=request.user ,title=title, description=description, minimum_price=minimum_price,
                         deadline_date=deadline_date)
            auct.save()
            send_mail('Auction added successfully.', 'Auction titled ' + str(auct.title) + ' added successfully. Description: '
                  + str(auct.description) + '. Link to your auction: http://127.0.0.1:8000/auction/' + str(auct.id),
                      'admin@admin.com', [request.user.email])
            return HttpResponseRedirect(reverse("auction:index"))
    else:
        #messages.add_message(request, messages.INFO, _("Auction cancelled"))
        return HttpResponseRedirect(reverse("auction:index"))


class EditAuction(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            user = request.user
            auct = get_object_or_404(Auction, id=id)
            if auct.seller == user.username:
                return render(request, "edit.html", {"auct": auct})
            else:
                editauctionmessage = "That is not your auction to edit"
                return render(request, 'edit.html', {"editauctionmessage": editauctionmessage})
        else:
            return HttpResponseRedirect(reverse("signin"))

    def post(self, request, id):
        auct = Auction.objects.get(id=id)
        description = request.POST["description"].strip()
        auct.description = description
        auct.save()
        return HttpResponseRedirect(reverse("auction:index"))


#Why bidding is not done as a class
def bid(request, item_id):
    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            auct = get_object_or_404(Auction, id=item_id)
            if auct.seller == user.username:
                bidauctionmessage = "You cannot bid on your own auctions"
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            else:
                return render(request, "bid.html", {"auct": auct})
        else:
            return HttpResponseRedirect(reverse("signin"))

    if request.method == "POST":
        if request.user.is_authenticated:
            auct = Auction.objects.get(id=item_id)
            new_price = float(request.POST["minimum_price"].strip())
            minimum_price = float(auct.minimum_price)
            deadline_date = auct.deadline_date
            deadline = datetime.strptime(deadline_date, '%Y-%m-%d %H:%M:%S')
            if auct.active == False:
                bidauctionmessage = "You can only bid on active auctions"
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            if deadline <= datetime.now():
                bidauctionmessage = "You can only bid on active auctions"
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            if new_price <= minimum_price:
                bidauctionmessage = "New bid must be greater than the current bid for at least 0.01"
                return render(request, 'bid.html', {"bidauctionmessage": bidauctionmessage})
            else:
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
        try:
            with transaction.atomic():
                auct.save()
                saved = True
                message="Ban succesfully"
                send_mail('Auction you have bid has been banned.',
                          'Auction titled ' + str(auct.title) + ' has been banned.',
                          'admin@admin.com', [auct.bidder_email])
                send_mail('Auction where you are the seller has been banned.',
                          'Auction titled ' + str(auct.title) + ' has been banned.', 'admin@admin.com',
                          [auct.seller_email])
                return render(request, "base.html", {"message": message})
        except OperationalError:
            messages.add_message(request, messages.ERROR, "Database locked. Try again.")
            return render(request, "ban.html", {"auct": auct})


def resolve(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            aucts = Auction.objects.all()
            resolved=[]
            for auct in aucts:
                if datetime.now() > auct.deadline_date:
                    resolved.append(auct.title)
                    auct.active=False
                    bidderEmail = auct.bidder_email
                    sellerEmail = auct.seller_email
                    send_mail('Auction you have bid has been resolved.',
                          'Auction titled ' + str(auct.title) + ' has been resolved.', 'admin@admin.com', [bidderEmail])
                    send_mail('Auction where you are the seller has been resolved.',
                          'Auction titled ' + str(auct.title) + ' has been resolved.', 'admin@admin.com', [sellerEmail])
                return render(request, "resolve.html", {"resolved": resolved})
        else:
            return HttpResponseRedirect(reverse("signin"))


def changeLanguage(request, lang_code):
    pass


def changeCurrency(request, currency_code):
    pass