from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    # email = forms.EmailField(required=True)
    # phone = forms.CharField(required=False)
    # company_name = forms.CharField(required=True)
    # content = forms.CharField(
    #     required=True,
    #     widget=forms.Textarea
    # )