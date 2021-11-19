import re


def validate_field(value, regex):
    return re.match(regex, value)


def validate_email(email):
    regex: str = r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+"
    return validate_field(email, regex)
