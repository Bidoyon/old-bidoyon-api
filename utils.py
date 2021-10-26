from secrets import token_hex
from datetime import datetime

token = lambda: token_hex(32)
timestamp = lambda: str(datetime.now().timestamp())
