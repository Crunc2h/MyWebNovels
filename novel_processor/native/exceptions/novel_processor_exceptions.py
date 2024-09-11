import novel_scraper.native.cout_custom as cout


class NovelProcessorException(Exception):
    def __init__(self, message, header) -> None:
        self.message = cout.COut.get_styled(
            message=message, header=header, style="fail"
        )
        super().__init__(self.message)


class ProcessPoolLockedException(NovelProcessorException):
    def __init__(self):
        self.header = "NOVEL_PROCESS_POOL"
        self.message = "Process pool is locked!"
        super().__init__(self.message, self.header)


class ProcessAlreadyActiveException(NovelProcessorException):
    def __init__(self, process_base_link):
        self.header = f"NOVEL_PROCESS_POOL"
        self.message = f"Process {process_base_link} is already active!"
        super().__init__(self.message, self.header)


class ProcessAlreadyInactiveException(NovelProcessorException):
    def __init__(self, process_base_link):
        self.header = f"NOVEL_PROCESS_POOL"
        self.message = f"Process {process_base_link} is already inactive!"
        super().__init__(self.message, self.header)
