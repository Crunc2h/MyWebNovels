import novel_scraper.native.cout_custom as cout


class EnumException(Exception):
    def __init__(self, message, header):
        self.message = cout.COut.get_styled(message, header=header, style="fail")
        super().__init__(self.message)


class DuplicatedEnumException(EnumException):
    def __init__(self, enum_type, val):
        self.header = "ENUM_MANAGER"
        self.message = cout.COut.get_styled(
            f"Multiple enums of type {enum_type} and value '{val}' exists!",
        )
        super().__init__(self.message, self.header)
