from novel_scraper.native.cout_custom import COut


class NovelScraperException(Exception):
    def __init__(self, message):
        self.message = COut.get_styled(message, style="fail")
        super().__init__(self.message)


class InvalidUpdaterFuncTypeException(NovelScraperException):
    def __init__(self, updater_function_type):
        self.message = COut.get_styled(
            f"{updater_function_type} is an invalid updater function type!",
            header="NOVEL_UPDATER",
        )
        super().__init__(self.message)


class ScraperProgressFailureException(NovelScraperException):
    def __init__(self, wrapped_exc, current_url, header):
        self.wrapped_exc = wrapped_exc
        self.header = header
        self.message = (
            f"An error occured while scraping {current_url} ==> \n{repr(wrapped_exc)}"
        )
        super().__init__(self.message)
