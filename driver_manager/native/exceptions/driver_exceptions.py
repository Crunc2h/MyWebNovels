class DriverException(Exception):
    def __init__(self, message, header):
        self.message = cout.COut.get_styled(message, header=header, style="failure")
        super().__init__(self.message)


class DriverPoolLockedException(DriverException):
    def __init__(self):
        self.message = cout.COut.get_styled(
            "Driver pool is locked!", header="DRIVER_POOL"
        )
        super().__init__(self.message)


class DriverAlreadyCapturedException(DriverException):
    def __init__(self, driver):
        self.message = cout.COut.get_styled(
            f"Driver  id_{driver.id} is already captured!",
            header=f"DRIVER_POOL::DRIVER{driver.id}",
        )
        super().__init__(self.message)


class DriverAlreadyReleasedException(DriverException):
    def __init__(self, driver):
        self.message = cout.COut.get_styled(
            f"Driver  id_{driver.id} is already released!",
            header=f"DRIVER_POOL::DRIVER-{driver.id}",
        )
        super().__init__(self.message)
