class OrderException(Exception):
    pass

class CartServiceUnavailable(OrderException):
    pass

class CartEmpty(OrderException):
    pass

class MenuItemNotFound(OrderException):
    pass

class MenuServiceUnavailable(OrderException):
    pass

class CartClearFailed(OrderException):
    pass