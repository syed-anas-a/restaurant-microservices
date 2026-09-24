class CartException(Exception):
    pass

class MenuItemNotFound(CartException):
    pass

class MenuServiceUnavailable(CartException):
    pass

class CartNotFound(CartException):
    pass

class CartItemNotFound(CartException):
    pass