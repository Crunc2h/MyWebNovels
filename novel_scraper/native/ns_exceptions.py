from novel_scraper.native.cout_custom import COut


class NovelScraperException(Exception):
    def __init__(self, message):
        self.message = COut.get_styled(message, style="fail")
        super().__init__(self.message)

class ProcessPoolLocked(Exception):
    def __init__(self, header):
        self.message = COut.get_styled("Process pool is locked!", header=header)
        super().__init__(self.message)

class NoProcessPoolExists(Exception):
    def __init__(self, header):
        self.message = COut.get_styled("No process pool exists!", header=header)
        super().__init__(self.message)

class ProcessAlreadyActive(Exception):
    def __init__(self, process_base_link):
        self.message = COut.get_styled(f"Process {process_base_link} is already active!", header="NOVEL_PROCESS")
        super().__init__(self.message)

class ProcessAlreadyInactive(Exception):
    def __init__(self, process_base_link):
        self.message = COut.get_styled(f"Process {process_base_link} is already inactive!", header="NOVEL_PROCESS")
        super().__init__(self.message)

class InvalidUpdaterFunctionType(Exception):
    def __init__(self, updater_function_type):
        self.message = COut.get_styled(f"{updater_function_type} is an invalid updater function type!", header="NOVEL_UPDATER")
        super().__init__(self.message)
