from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import filters
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from auction.models import Auction
from auction.serializers import AuctionSerializer


class BrowseAuctionApi(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer


class SearchAuctionApi(APIView):
    def get(self, request, title):
        auct = get_object_or_404(Auction, title=title)
        serializer = AuctionSerializer(auct)
        return Response(serializer.data)


class SearchAuctionWithTermApi(generics.ListCreateAPIView):
    search_fields = ['title']
    filter_backends = (filters.SearchFilter,)
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer


class SearchAuctionApiById(APIView):
    def get(self, request, pk):
        auct = get_object_or_404(Auction, pk=pk)
        serializer = AuctionSerializer(auct)
        return Response(serializer.data)


class BidAuctionApi(APIView):
    pass
