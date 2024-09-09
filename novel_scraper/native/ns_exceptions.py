from novel_scraper.native.cout_custom import COut


class NovelScraperException(Exception):
    def __init__(self, message):
        self.message = COut.get_styled(message, style="fail")
        super().__init__(self.message)

