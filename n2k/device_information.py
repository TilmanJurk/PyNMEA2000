class DeviceInformation:
    unique_number: int  # 21 bits
    manufacturer_code: int  # 11 bits
    device_instance: int  # 8 bits
    device_function: int  # 8 bits
    device_class: int  # 8 bits
    # https://github.com/ttlappalainen/NMEA2000/blob/master/src/NMEA2000.h#L133
    system_instance: int  # 4 bits
    industry_group: int  # 4 bits (actually 3 bits but the upper is always set)
    
    @property
    def name(self) -> int:
        """
        TODO: Confirm!
              Base behaviour tested here: http://tpcg.io/_HZMR7R
              -
              Formatting as described here:
              https://www.nmea.org/Assets/20140710%20nmea-2000-060928%20iso%20address%20claim%20pgn%20corrigendum.pdf \n
              21: Unique Number\n
              11: Manufacturer Code\n
               3: Device Instance Lower\n
               5: Device Instance Upper\n
               8: Device Function\n
               1: Reserved\n
               7: Device Class\n
               4: System Instance\n
               3: Industry Group\n
               1: Reserved\n
              Stored in little endian order (based on N2kMsg.cpp: 512)
              This only serves to heighten my confusion
        This might be very configuration dependent! As long as we don't use both the name accessor and the direct access
        at the same time it will not matter but a better understanding of the composition of the name is required
        
        :return:
        """
        return (self.unique_number & 0x1fffff) << 0 | \
               (self.manufacturer_code & 0x7ff) << 21 | \
               (self.device_instance & 0xff) << 32 | \
               (self.device_function & 0xff) << 40 | \
               (self.device_class & 0xff) << 48 | \
               (self.system_instance & 0x0f) << 56 | \
               (self.industry_group & 0x07) << 60 | \
               (1 << 63)
               
    @name.setter
    def name(self, value) -> None:
        self.unique_number = value & 0x1fffff
        self.manufacturer_code = (value >> 21) & 0x7ff
        self.device_instance = (value >> 32) & 0xff
        self.device_function = (value >> 40) & 0xff
        self.device_class = (value >> 48) & 0xff
        self.system_instance = (value >> 56) & 0x0f
        self.industry_group = (value >> 60) & 0x07
        
    def calculated_unique_number_and_manufacturer_code(self) -> int:
        return (self.manufacturer_code & 0x7ff) << 21 | \
               (self.unique_number & 0x1fffff)
    
    def get_device_instance_lower(self) -> int:
        return self.device_instance & 0x07
    
    def get_device_instance_upper(self) -> int:
        return (self.device_instance >> 3) & 0x1f
    
    def calculated_device_class(self) -> int:
        return (self.device_class & 0x7f) << 1 >> 1  # ?? in which direction should it be shifter or why shift at all?
    
    def calculated_industry_group_and_system_instance(self) -> int:
        return (self.industry_group << 4) | 0x80 | (self.system_instance & 0x0f)
