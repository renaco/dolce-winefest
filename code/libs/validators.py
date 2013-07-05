# Idea brought from wtforms
import re


class ValidationError(Exception):

    def __init__(self, status_code=None):
        self.status_code = status_code


class Regexp(object):

    def __init__(self, regex, status_code, flags=0):
        if isinstance(regex, basestring):
            regex = re.compile(regex, flags)
        self.regex = regex
        self.status_code = status_code

    def __call__(self, data):
        if not self.regex.match(data):
            raise ValidationError(self.status_code)


class Email(Regexp):

    def __init__(self, status_code=None):
        super(Email, self).__init__(
            r"^.+@[^.].*\.[a-z]{2,10}$",
            status_code,
            re.IGNORECASE
        )


class URL(Regexp):

    def __init__(self, status_code=None):
        super(URL, self).__init__(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            status_code,
            re.IGNORECASE
        )


class Length(object):

    def __init__(self, status_code, min_length=-1, max_length=-1):
        assert min_length != -1 or max_length != -1
        assert max_length == -1 or min_length <= max_length

        self.min_length = min_length
        self.max_length = max_length
        self.status_code = status_code

    def __call__(self, data):
        if len(data) < self.min_length or \
            (self.max_length != -1 and len(data) > self.max_length):
            raise ValidationError(self.status_code)


class Float(object):

    def __init__(self, status_code):
        self.status_code = status_code

    def __call__(self, data):
        try:
            data = float(data)
        except ValueError:
            raise ValidationError(self.status_code)


class ValueRange(object):

    def __init__(self, status_code, min_value=0, max_value=0):
        assert min_value is not None
        assert max_value is not None

        self.status_code = status_code
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, data):
        try:
            data = float(data)
            if not (self.min_value <= data <= self.max_value):
                raise ValidationError(self.status_code)
        except ValueError:
            raise ValidationError(self.status_code)


class AllowedChars(object):

    def __init__(self, regex, status_code):
        if isinstance(regex, basestring):
            regex = re.compile(regex, re.IGNORECASE)
        self.regex = regex
        self.status_Code = status_code

    def __call__(self, data):
        if self.regex.search(data) is not None:
            raise ValidationError(self.status_code)
