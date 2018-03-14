from django.db.models import TextField
# This file is the answer from Udi on Stack Overflow
# https://stackoverflow.com/questions/38995764/django-textfield-charfield-is-stripping-spaces-blank-lines


class NonStrippingTextField(TextField):
    """A TextField that does not strip whitespace at the beginning/end of
    it's value.  Might be important for markup/code."""

    def formfield(self, **kwargs):
        kwargs['strip'] = False
        return super(NonStrippingTextField, self).formfield(**kwargs)
