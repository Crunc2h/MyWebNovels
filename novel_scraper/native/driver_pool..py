import novel_scraper.native.cout_custom as cout
import novel_scraper.native.ns_exceptions as nsexc
from selenium import webdriver
from datetime import datetime, timezone


class Driver:
    def __init__(self, id) -> None:
        self.id = id
        self.t_init = datetime.now(timezone.utc)
        self.t_start_curr = datetime.now(timezone.utc)
        self.is_being_used = False
        self.t_usages = []
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        cout.COut.broadcast(
            f"Browser initialized",
            header=f"DRIVER_POOL::DRIVER-{self.id}",
            style="success",
        )

    def release_driver(self, releasing_updater_func_type):
        if not self.is_being_used:
            raise nsexc.DriverAlreadyReleasedException(self)
        self.t_usages.append(
            (
                (datetime.now(timezone.utc) - self.t_start_curr).seconds,
                releasing_updater_func_type,
            )
        )
        self.is_being_used = False

    def capture_driver(self):
        if self.is_being_used:
            raise nsexc.DriverAlreadyCapturedException(self)
        self.is_being_used = True
        self.t_start_curr = datetime.now(timezone.utc)


class DriverPool:
    def __init__(self, max_concurrent_ops) -> None:
        self.is_locked = False
        self.drivers = []
        for i in range(0, max_concurrent_ops):
            self.drivers.append(Driver(i))
        cout.COut.broadcast(
            "Initialization successful", header="DRIVER_POOL", style="success"
        )

    def get_available_driver(self):
        if self.is_locked:
            raise nsexc.DriverPoolLockedException()
        self.is_locked = True
        for driver in self.drivers:
            if not driver.is_being_used:
                self.is_locked = False
                driver.capture_driver()
                return driver
        self.is_locked = False
        raise nsexc.NoDriverAvailableException()
