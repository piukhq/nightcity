""" NightCity Police Department"""

from nightcity.ncpd.assets import FreshService


def run() -> None:
    fs = FreshService()
    fs.get_all_freshservice_requestors()
