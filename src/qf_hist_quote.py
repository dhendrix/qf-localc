# coding: utf-8
#
# qf_hist_quote - implement historical quote with different data sources
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE.md file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE.md file).  If not, see <http://www.gnu.org/licenses/>.
#

import json
from qf_app_logger import AppLogger
from qf_extn_helper import normalize_date
from qf_cache_db import CacheDB
import qf_wsj
import qf_stooq
# import datetime
# import time
# import json
# Logger init

the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()

# For WSJ
wsj_category_map = {
    "stock": "",
    "mutf": "mutualfund",
    "mutualfund": "mutualfund",
    "etf": "etf",
    "index": "index"
}

def closing_price(ticker, category, for_date):
    """

    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The closing price for the given date
    """
    # Normalize date
    for_date = normalize_date(for_date)

    # Validate/translate category
    if category:
        if category.lower() in wsj_category_map.keys():
            category = wsj_category_map[category.lower()]
        else:
            return "Invalid category"
    else:
        category = ""

    # Cache look up
    ticker = ticker.upper()
    cr = CacheDB.lookup_closing_price_by_date(ticker, for_date)
    if cr:
        logger.debug("Cache hit for %s %s", ticker, for_date)
        return cr["Close"]

    # Try WSJ
    try:
        r = qf_wsj.get_historical_price_data(ticker, category, for_date)
        if r:
            # Cache result
            CacheDB.insert_closing_price(ticker, for_date, r['close'])
            return r['close']
    except Exception as ex:
        return str(ex)

    return "N/A"
