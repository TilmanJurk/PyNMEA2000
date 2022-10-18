# I/O stream used in the NMEA2000 libraries.
class Stream:
    def read(self) -> int:
        """
        :return: First byte of incoming data or -1 if no data
        """
        return 0
    
    def peek(self) -> int:
        return 0
    
    def write(self, data: bytearray) -> int:
        """
        Write data to stream
        
        :param data:
        :return:
        """
        return 0
    
    def print(self, s: str) -> int:
        """
        Print string to stream
        
        :param s:
        :return:
        """
        raise NotImplementedError()
    
    def println(self, s: str) -> int:
        print("NotImplemented println")
    
    def print_val(self, val: int, radix: int = 10) -> int:
        """
        Print value to string
        
        :param val:
        :param radix:
        :return:
        """
        raise NotImplementedError()
    
    def println_val(self, val: int, radix: int = 10) -> int:
        print("NotImplemented println_val")
