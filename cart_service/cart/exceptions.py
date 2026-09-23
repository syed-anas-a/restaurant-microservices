class CartException(Exception):
    pass

class MenuItemNotFound(CartException):
    pass