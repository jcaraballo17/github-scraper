import math
from datetime import timedelta, datetime
from urllib.error import HTTPError


class RateLimitExceededError(HTTPError):
    """ Github Rate Limit was exceeded and no more requests can be done for the next hour. """

    def __init__(self, url, code, msg, hdrs, fp, last_id: int = None):
        super().__init__(url, code, msg, hdrs, fp)
        self.last_id = last_id
        limit_reset_header = int(hdrs.get('X-RateLimit-Reset'))
        reset_difference: timedelta = datetime.utcfromtimestamp(limit_reset_header) - datetime.utcnow()
        self.limit_reset_seconds: int = math.ceil(reset_difference.total_seconds())
