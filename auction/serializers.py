from rest_framework import serializers
from auction.models import Auction, BidAuction

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('title', 'description', 'minimum_price', 'deadline_date')

#class BidAuctionSerializer(serializers.ModelSerializer):
 #   class Meta:
  #      model = Auction
   #     fields = ('something')