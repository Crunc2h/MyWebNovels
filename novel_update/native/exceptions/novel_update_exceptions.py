import novel_scraper.native.cout_custom as cout


class NovelUpdateException(Exception):
    def __init__(self, message, header) -> None:
        self.message = cout.COut.get_styled(message, header=header, style="failure")
        super().__init__(self.message)


class NoNovelProcessPoolExistsException(NovelUpdateException):
    def __init__(self, updater_func_type):
        self.header = f"NOVEL_UPDATER::{updater_func_type}"
        self.message = "No novel process pool exists!"
        super().__init__(self.message, self.header)


class MultipleNovelProcessPoolsExistException(NovelUpdateException):
    def __init__(self, updater_func_type):
        self.header = f"NOVEL_UPDATER::{updater_func_type}"
        self.message = "Multiple novel process pools exist!"
        super().__init__(self.message, self.header)


class NoDriverPoolExistsException(NovelUpdateException):
    def __init__(self, updater_func_type):
        self.header = f"NOVEL_UPDATER::{updater_func_type}"
        self.message = "No driver pool exists!"
        super().__init__(self.message, self.header)


class MultipleDriverPoolsExistException(NovelUpdateException):
    def __init__(self, updater_func_type):
        self.header = f"NOVEL_UPDATER::{updater_func_type}"
        self.message = "Multiple driver pools exist!"
        super().__init__(self.message, self.header)
