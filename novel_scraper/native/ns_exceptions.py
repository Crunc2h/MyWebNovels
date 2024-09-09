from novel_scraper.native.cout_custom import COut


class NovelScraperException(Exception):
    def __init__(self, message):
        self.message = COut.get_styled(message, style="fail")
        super().__init__(self.message)


class ProcessPoolLockedException(Exception):
    def __init__(self, header):
        self.message = COut.get_styled("Process pool is locked!", header=header)
        super().__init__(self.message)


class NoProcessPoolExistsException(Exception):
    def __init__(self, header):
        self.message = COut.get_styled("No process pool exists!", header=header)
        super().__init__(self.message)


class MultipleProcessPoolsExistException(Exception):
    def __init__(self, header):
        self.message = COut.get_styled("Multiple process pools exist!", header=header)
        super().__init__(self.message)


class ProcessAlreadyActiveException(Exception):
    def __init__(self, process_base_link):
        self.message = COut.get_styled(
            f"Process {process_base_link} is already active!", header="NOVEL_PROCESS"
        )
        super().__init__(self.message)


class ProcessAlreadyInactiveException(Exception):
    def __init__(self, process_base_link):
        self.message = COut.get_styled(
            f"Process {process_base_link} is already inactive!", header="NOVEL_PROCESS"
        )
        super().__init__(self.message)


class InvalidUpdaterFuncTypeException(Exception):
    def __init__(self, updater_function_type):
        self.message = COut.get_styled(
            f"{updater_function_type} is an invalid updater function type!",
            header="NOVEL_UPDATER",
        )
        super().__init__(self.message)


class DuplicatedEnumException(Exception):
    def __init__(self, enum_type, val):
        self.message = COut.get_styled(
            f"Multiple enums of type {enum_type} and value '{val} exists!'",
            header="ENUM_MANAGER",
        )
        super().__init__(self.message)
