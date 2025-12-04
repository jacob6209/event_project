from django import template

register = template.Library()

farsi_numbers = {
    1: "اول",
    2: "دوم",
    3: "سوم",
    4: "چهارم",
    5: "پنجم",
    6: "ششم",
    7: "هفتم",
    8: "هشتم",
    9: "نهم",
    10: "دهم",
    11: "یازدهم",
    12: "دوازدهم",
    13: "سیزدهم",
    14: "چهاردهم",
    15: "پانزدهم",
    16: "شانزدهم",
    17: "هفدهم",
    18: "هجدهم",
    19: "نوزدهم",
    20: "بیستم",
    # Add more as needed
}

@register.filter
def number_to_farsi(value):
    """Converts a number to its Farsi equivalent."""
    return farsi_numbers.get(value, str(value))  # Default returns the number if not in dictionary



# Persian digits
PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵',
    '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}

@register.filter(name='persian_digits')
def persian_digits(value):
    """Convert digits to Persian (Farsi) numerals."""
    return ''.join(PERSIAN_DIGITS.get(c, c) for c in str(value))