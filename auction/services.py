from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import filters
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from auction.models import Auction
from auction.serializers import AuctionSerializer

#Used generics from rest_framework library for browsing
class BrowseAuctionApi(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

#Search done with get_object_or_404
class SearchAuctionApi(APIView):
    def get(self, request, title):
        auct = get_object_or_404(Auction, title=title)
        serializer = AuctionSerializer(auct)
        return Response(serializer.data)

#term search done again with generics
class SearchAuctionWithTermApi(generics.ListCreateAPIView):
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

#id search done with pk in get_object_or_404
class SearchAuctionApiById(APIView):
    def get(self, request, pk):
        auct = get_object_or_404(Auction, pk=pk)
        serializer = AuctionSerializer(auct)
        return Response(serializer.data)

#was not skillful enough for bidAPI
class BidAuctionApi(APIView):
    pass
