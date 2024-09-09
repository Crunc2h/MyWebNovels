from datetime import datetime, timezone
from novel_scraper.native.cout_exceptions import InvalidStyleException


class COutColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def get_style(style_str):
        if style_str == None:
            return ""
        elif style_str == "init": return COutColors.BOLD + COutColors.UNDERLINE + COutColors.HEADER
        elif style_str == "progress": return COutColors.CYAN
        elif style_str == "success": return COutColors.BOLD + COutColors.UNDERLINE + COutColors.GREEN 
        elif style_str == "warning": return COutColors.UNDERLINE + COutColors.YELLOW
        elif style_str == "fail": return COutColors.BOLD + COutColors.UNDERLINE + COutColors.RED
        else : raise InvalidStyleException(style_str)

class COut:
    @staticmethod
    def get_styled(message, header=None, style=None):
        message = f"{COutColors.get_style(style)}[{datetime.now(timezone.utc).strftime('%d/%m/%Y::%H:%M:%S')}]" 
        if header:
            message += f"[~@{header}] > {message}{COutColors.ENDC}"
        else:
            message += f" > {message}{COutColors.ENDC}"
        return message
    
    @staticmethod
    def broadcast(message, header=None, style=None):
        print(COut.get_styled(message, header, style))