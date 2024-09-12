import cout.native.cout_custom as cout


class NovelUpdateException(Exception):
    def __init__(self, message, header) -> None:
        self.message = cout.COut.get_styled(message, header=header, style="fail")
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


class NovelProcessFailureException(NovelUpdateException):
    def __init__(self, progress_failure_exc, process):
        self.header = self.header + "::" + progress_failure_exc.header
        self.message = (
            f"PROCESS FAILURE {process.base_link} >>\n" + progress_failure_exc.message
        )
        super().__init__(self.message, self.header)


class NovelLinksCollectorFailureException(NovelUpdateException):
    def __init__(self, progress_failure_exc):
        self.header = self.header + "::" + progress_failure_exc.header
        self.message = (
            f"NOVEL LINKS COLLECTOR FAILURE >>\n" + progress_failure_exc.message
        )
        super().__init__(self.message, self.header)


class InvalidUpdaterFuncTypeException(NovelUpdateException):
    def __init__(self, updater_function_type):
        super().__init__(self.message)
        self.header = "NOVEL_UPDATER"
        self.message = f"{updater_function_type} is an invalid updater function type!"
        super().__init__(self.message, self.header)
