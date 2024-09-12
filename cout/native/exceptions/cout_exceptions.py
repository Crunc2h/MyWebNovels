import cout.native.cout_custom as cout


class COutException(Exception):
    def __init__(self, message):
        self.message = cout.COut.get_styled(message, style="fail")
        super().__init__(self.message)


class InvalidStyleException(COutException):
    def __init__(self, style):
        self.message = cout.COut.get_styled(
            f"{style} is an invalid style string!", header="CONSOLE_OUT"
        )
        super().__init__(self.message)
