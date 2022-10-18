from time import time


def millis() -> int:
    return int(time() * 1000)


class IntRef:
    value: int
    
    def __init__(self, value: int = 0):
        self.value = value

    def __add__(self, other):
        if isinstance(other, IntRef):
            return self.value + other.value
        elif isinstance(other, int):
            return self.value + other
        else:
            raise TypeError("unsupported operand type(s) for +: 'IntRef' and '" + type(other).__name__ + "'")
        
    def __radd__(self, other):
        if isinstance(other, IntRef):
            return other.value + self.value
        elif isinstance(other, int):
            return other + self.value
        else:
            raise TypeError("unsupported operand type(s) for +: '" + type(other).__name__ + "' and 'IntRef'")
        
    def __sub__(self, other):
        if isinstance(other, IntRef):
            return self.value - other.value
        elif isinstance(other, int):
            return self.value - other
        else:
            raise TypeError("unsupported operand type(s) for -: 'IntRef' and '" + type(other).__name__ + "'")
        
    def __rsub__(self, other):
        if isinstance(other, IntRef):
            return other.value - self.value
        elif isinstance(other, int):
            return other - self.value
        else:
            raise TypeError("unsupported operand type(s) for +: '" + type(other).__name__ + "' and 'IntRef'")
    
    def __mult__(self, other):
        if isinstance(other, IntRef):
            return self.value * other.value
        elif isinstance(other, int):
            return self.value * other
        else:
            raise TypeError("unsupported operand type(s) for *: 'IntRef' and '" + type(other).__name__ + "'")
        
    def __floordiv__(self, other):
        if isinstance(other, IntRef):
            return self.value // other.value
        elif isinstance(other, int):
            return self.value // other
        else:
            raise TypeError("unsupported operand type(s) for //: 'IntRef' and '" + type(other).__name__ + "'")
        
    def __rfloordiv__(self, other):
        if isinstance(other, IntRef):
            return other.value // self.value
        elif isinstance(other, int):
            return other // self.value
        else:
            raise TypeError("unsupported operand type(s) for +: '" + type(other).__name__ + "' and 'IntRef'")
        
    def __truediv__(self, other):
        if isinstance(other, IntRef):
            return self.value / other.value
        elif isinstance(other, int):
            return self.value / other
        else:
            raise TypeError("unsupported operand type(s) for /: 'IntRef' and '" + type(other).__name__ + "'")
        
    def __rtruediv__(self, other):
        if isinstance(other, IntRef):
            return other.value / self.value
        elif isinstance(other, int):
            return other / self.value
        else:
            raise TypeError("unsupported operand type(s) for +: '" + type(other).__name__ + "' and 'IntRef'")

    def __repr__(self):
        return "IntRef(" + str(self.value) + ")"
    
    def __str__(self):
        return str(self.value)
    
    def __int__(self):
        return self.value
