from datetime import datetime, timezone
import novel_scraper.native.cout_exceptions as coutexc
import os


class COutColors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"

    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    LINE_UP = "\033[1A"
    LINE_CLEAR = "\33[2K"

    @staticmethod
    def get_style(style_str):
        if style_str == None:
            return ""
        elif style_str == "init":
            return COutColors.BOLD + COutColors.HEADER
        elif style_str == "progress":
            return COutColors.CYAN
        elif style_str == "success":
            return COutColors.BOLD + COutColors.GREEN
        elif style_str == "warning":
            return COutColors.UNDERLINE + COutColors.YELLOW
        elif style_str == "fail":
            return COutColors.BOLD + COutColors.RED
        else:
            raise coutexc.InvalidStyleException(style_str)


class COutLoading:
    def __init__(self) -> None:
        self.symbols = ["\\", "|", "/", "-"]
        self.current = 0

    def load(self):
        self.current += 1
        return self.symbols[self.current % 4]


class COut:
    @staticmethod
    def get_styled(message, header=None, style=None, loader=None):
        body = f"{COutColors.get_style(style)}[{datetime.now(timezone.utc).strftime('%d/%m/%Y::%H:%M:%S')}]"

        if header != None:
            body += f"[~@{header}] > {message}"
        else:
            body += f" > {message}"

        if style == "progress":
            body += (
                COutColors.get_style("success") + " " + loader.load() + COutColors.ENDC
            )
        else:
            body += COutColors.ENDC
        return body

    @staticmethod
    def broadcast(message, header=None, style=None, loader=None):
        if style == "progress":
            print(
                COutColors.LINE_CLEAR
                + COut.get_styled(message, header=header, style=style, loader=loader),
                end="\r",
            )
            return
        elif style == "init":
            os.system("clear")
        print(COut.get_styled(message, header=header, style=style))
