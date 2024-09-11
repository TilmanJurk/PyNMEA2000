# PyNMEA2000
Python NMEA2000 library. Fork of https://github.com/finnboeger/NMEA2000

This library is still in an beta state and is currently missing support for the following:

- several messages (as noted by the `todo` comments in [n2k/messages.py](n2k/messages.py)
- testing for the included messages
- support for transport protocol messages
- support for group functions
- proper logging
- good documentation. For now only the expected values for the messages are documented

The interface for creating messages will likely change in the future.
There is currently no pypi package, thus the library needs to be installed manually using 
python setup.py build && python setup.py install
