import novel_scraper.native.cout_custom as cout


class DriverException(Exception):
    def __init__(self, message, header):
        self.message = cout.COut.get_styled(message, header=header, style="failure")
        super().__init__(self.message)


class DriverPoolLockedException(DriverException):
    def __init__(self):
        self.header = "DRIVER_POOL"
        self.message = "Driver pool is locked!"
        super().__init__(self.message, self.header)


class DriverAlreadyCapturedException(DriverException):
    def __init__(self, driver):
        self.header = f"DRIVER_POOL::DRIVER{driver.id}"
        self.message = (f"Driver  id_{driver.id} is already captured!",)
        super().__init__(self.message, self.header)


class DriverAlreadyReleasedException(DriverException):
    def __init__(self, driver):
        self.header = f"DRIVER_POOL::DRIVER{driver.id}"
        self.message = (f"Driver  id_{driver.id} is already released!",)
        super().__init__(self.message, self.header)
