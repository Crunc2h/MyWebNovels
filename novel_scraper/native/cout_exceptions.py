from novel_scraper.native.cout_custom import COut

class COutException(Exception):
    def __init__(self, message):
        self.message = COut.get_styled(message, style="fail")
        super().__init__(self.message)

class InvalidStyleException(Exception):
    def __init__(self, style):
        self.message = f"{style} is an invalid style string!"
        super().__init__(self.message)
