from novel_scraper.native.cout_custom import COut


class NovelScraperException(Exception):
    def __init__(self, message):
        self.message = COut.get_styled(message, style="fail")
        super().__init__(self.message)


class ProcessPoolLockedException(NovelScraperException):
    def __init__(self, header):
        self.message = COut.get_styled("Process pool is locked!", header=header)
        super().__init__(self.message)


class NoProcessPoolExistsException(NovelScraperException):
    def __init__(self, header):
        self.message = COut.get_styled("No process pool exists!", header=header)
        super().__init__(self.message)


class MultipleProcessPoolsExistException(NovelScraperException):
    def __init__(self, header):
        self.message = COut.get_styled("Multiple process pools exist!", header=header)
        super().__init__(self.message)


class ProcessAlreadyActiveException(NovelScraperException):
    def __init__(self, process_base_link):
        self.message = COut.get_styled(
            f"Process {process_base_link} is already active!", header="NOVEL_PROCESS"
        )
        super().__init__(self.message)


class ProcessAlreadyInactiveException(NovelScraperException):
    def __init__(self, process_base_link):
        self.message = COut.get_styled(
            f"Process {process_base_link} is already inactive!", header="NOVEL_PROCESS"
        )
        super().__init__(self.message)


class InvalidUpdaterFuncTypeException(NovelScraperException):
    def __init__(self, updater_function_type):
        self.message = COut.get_styled(
            f"{updater_function_type} is an invalid updater function type!",
            header="NOVEL_UPDATER",
        )
        super().__init__(self.message)


class DuplicatedEnumException(NovelScraperException):
    def __init__(self, enum_type, val):
        self.message = COut.get_styled(
            f"Multiple enums of type {enum_type} and value '{val} exists!'",
            header="ENUM_MANAGER",
        )
        super().__init__(self.message)


SCRAPER_PROCESS_FAILURE_RETRY_BROADCAST = "WARNING !!! SCRAPER PROCESS FAILURE GRACE RETRY !- GRACE PERIOD >> {current_grace_period} of {max_grace_period}"
SCRAPER_PROCESS_FAILURE_COMPLETE_BROADCAST = (
    "WARNING !!! SCRAPER PROCESS FAILURE GRACE COMPLETE !! KILLING THE SCRAPER FUNCTION"
)
NOVEL_PROCESS_FAILURE_RETRY_BROADCAST = "WARNING !!! NOVEL PROCESS FAILURE GRACE RETRY !- GRACE PERIOD >> {current_grace_period} of {max_grace_period}"


class ScraperProcessFailureException(NovelScraperException):
    def __init__(self, wrapped_exc, current_url, header):
        self.wrapped_exc = wrapped_exc
        self.header = header
        self.message = (
            f"An error occured while scraping {current_url} ==> \n{repr(wrapped_exc)}"
        )
        super().__init__(self.message)


class NovelProcessFailureException(NovelScraperException):
    def __init__(self, process_failure_exc, process):
        self.message = COut.get_styled(
            message=f"PROCESS FAILURE {process.base_link} >>\n"
            + process_failure_exc.message,
            header="NOVEL_UPDATER::" + process_failure_exc.header,
        )
        super().__init__(self.message)


class NoDriverAvailableException(NovelScraperException):
    def __init__(self):
        self.message = COut.get_styled(
            "No drivers available for updaters!", header="DRIVER_POOL"
        )
        super().__init__(self.message)


class DriverPoolLockedException(NovelScraperException):
    def __init__(self):
        self.message = COut.get_styled("Driver pool is locked!", header="DRIVER_POOL")
        super().__init__(self.message)


class DriverAlreadyCapturedException(NovelScraperException):
    def __init__(self, driver):
        self.message = COut.get_styled(
            f"Driver  id_{driver.id} is already captured!", header="DRIVER_POOL"
        )
        super().__init__(self.message)


class DriverAlreadyReleasedException(NovelScraperException):
    def __init__(self, driver):
        self.message = COut.get_styled(
            f"Driver  id_{driver.id} is already released!", header="DRIVER_POOL"
        )
        super().__init__(self.message)
