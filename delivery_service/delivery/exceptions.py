class DeliveryException(Exception):
    pass

class UserNotFound(DeliveryException):
    pass

class UserServiceUnavailable(DeliveryException):
    pass

class OrderNotFound(DeliveryException):
    pass

class OrderServiceUnavailable(DeliveryException):
    pass

class UserNotDeliveryCrew(DeliveryException):
    pass

class OrderNotPlaced(DeliveryException):
    pass

