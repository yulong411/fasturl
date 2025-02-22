import re

class Base62():
    table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    base = 62 

    @classmethod
    def encode(cls, data): 
        """Convert an integer to a Base62 encoded string."""
        if data < 0:
            raise ValueError("Invalid number")

        if data == 0:
            return '0'

        result = []
        while data:
            data, remainder = divmod(data, cls.base)
            result.append(cls.table[remainder])  

        result.reverse()  
        return ''.join(result)
    
    @classmethod
    def decode(cls, data):
        """Convert a Base62 encoded string back to an integer."""
        result = 0
        for power, char in enumerate(reversed(data)):  
            result += cls.table.index(char) * (cls.base ** power)  

        return result

class UrlRegex():
    protocol = r"^(https?|ftp):\/\/"
    domain = r"([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    port = r"(:\d{1,5})?"
    link = r"(\/[^\s]*)?$"

    full_pattern = re.compile(protocol + domain + port + link)

    @classmethod
    def validate_url(cls, url): 
        return bool(cls.full_pattern.match(url))



