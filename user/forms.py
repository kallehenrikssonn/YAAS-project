from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from auction.models import Auction, BidAuction


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username', 'email', 'password')

class EditProfileForm(forms.ModelForm):
    class Meta():
        model = User
        fields = ('email', 'password')

class CreateAuctionForm(forms.ModelForm):
    deadline_date = forms.DateTimeField(widget=forms.DateTimeInput(format="%d.%m.%Y %H:%M:%S"),
                                        input_formats=("%d.%m.%Y %H:%M:%S", ))
    class Meta:
        model = Auction
        fields = ('title', 'description', 'minimum_price')

class ConfAuctionForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
    title = forms.CharField(widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.HiddenInput())
    minimum_price = forms.DecimalField(widget=forms.HiddenInput())
    deadline_date = forms.DateTimeField(widget=forms.HiddenInput())


class EditAuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['description']

class SearchAuctionsForm(forms.ModelForm):
    class Meta():
        model = Auction
        fields = ('title',)

class BidAuctionForm(forms.ModelForm):
    class Meta:
        model = BidAuction
        fields = ['value']


