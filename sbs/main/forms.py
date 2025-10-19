from django import forms
from .models import Contacts

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your.email@example.com'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Inquiry subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message here...', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'message':
                field.widget.attrs['class'] = 'form-input'
            else:
                field.widget.attrs['class'] = 'form-textarea'

class CheckoutForm(forms.Form):
    # Customer Information
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'pattern': '[0-9]{10,15}'}))
    # Shipping Address
    street_address = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'placeholder': 'Street Address'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'City'}))
    pincode = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Pincode', 'pattern': '[0-9]{4,10}'})) 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'