class CartException(Exception):
    pass

class MenuItemNotFound(CartException):
    pass

class MenuServiceUnavailable(CartException):
    pass