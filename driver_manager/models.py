import driver_manager.native.exceptions as dmexc
import novel_scraper.native.cout_custom as cout
from django.db import models
from selenium import webdriver
from datetime import datetime, timezone


class Driver(models.Model):
    pool = models.ForeignKey(
        DriverPool, on_delete=models.CASCADE, related_name="drivers"
    )
    id = models.IntegerField(blank=True, null=True)

    t_init = models.DateTimeField(auto_now=True)
    t_start_current = models.DateTimeField(blank=True, null=True)

    is_being_used = models.BooleanField(default=False)

    def save(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        self.id = Driver.objects.count()
        cout.COut.broadcast(
            f"Driver is successfully initialized",
            header=f"DRIVER_POOL::DRIVER-{self.id}",
            style="success",
        )
        return super().save()

    def release_driver(self, releasing_updater_func_type):
        if not self.is_being_used:
            raise dmexc.DriverAlreadyReleasedException(self)

        new_usage = DriverUsage(
            t_start=self.t_start_current,
            t_end=datetime.now(timezone.utc),
            updater_func_type=releasing_updater_func_type,
            driver=self,
        )
        new_usage.save()

        self.is_being_used = False

    def capture_driver(self):
        if self.is_being_used:
            raise dmexc.DriverAlreadyCapturedException(self)
        self.t_start_curr = datetime.now(timezone.utc)
        self.is_being_used = True

    def close(self):
        self.driver.quit()
        self.delete()


class DriverUsage(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="usages")
    updater_func_type = models.CharField(max_length=64)
    t_start = models.DateTimeField()
    t_end = models.DateTimeField()
    t_delta_seconds = models.IntegerField(blank=True, null=True)

    def save(self) -> None:
        self.t_delta_seconds = (self.t_end - self.t_start).seconds
        return super().save()


class DriverPool(models.Model):
    is_locked = models.BooleanField(default=False)

    def initialize(self, max_concurrent_ops):
        if self.drivers.count() > 0:
            cout.COut.broadcast(
                "Previously present drivers discovered, deletion in progress...",
                header="DRIVER_POOL",
                style="warning",
            )
        for driver in self.drivers.all():
            driver.close()
        for i in range(max_concurrent_ops):
            driver = Driver(
                pool=self,
            )
            driver.save()
        cout.COut.broadcast(
            "Initialization successful", header="DRIVER_POOL", style="success"
        )

    def get_available_driver(self):
        if self.is_locked:
            raise dmexc.DriverPoolLockedException()
        self.is_locked = True
        for driver in self.drivers:
            if not driver.is_being_used:
                self.is_locked = False
                driver.capture_driver()
                return driver
        self.is_locked = False
        return None
