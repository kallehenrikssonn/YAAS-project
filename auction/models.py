from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone

class Auction(models.Model):
    active = models.BooleanField(default=True)
    seller = models.CharField(max_length=128)
    seller_email=models.EmailField(max_length=128, default="")
    bidder = models.CharField(max_length=128, default="")
    bidder_email = models.EmailField(max_length=128, default="")
    title = models.CharField(max_length=150)
    description = models.TextField()
    minimum_price = models.DecimalField(max_digits=8, decimal_places=2)
    deadline_date = models.DateTimeField(default=datetime.now()+timedelta(hours=72))
    banned = models.BooleanField(default=False)

    #class Meta:
      #  ordering = ['-deadline_date']

    def __str__(self):
        return "{} {}".format(self.title, self.description)

class BidAuction(models.Model):
    bidder = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(
    Auction, on_delete=models.CASCADE, null=True, related_name="auctionBid"
    )
    value = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    hasWon = models.BooleanField(default=False)

class Email(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    emailTo = models.ForeignKey(
    get_user_model(), on_delete=models.CASCADE, null=True, related_name="emailTo"
    )
    body = models.TextField()
    title = models.CharField(max_length=150)



    """title = models.CharField(max_length=150)
    description = models.TextField()
    minimum_price = models.FloatField()
    deadline_date = models.DateTimeField(auto_now=True)"""