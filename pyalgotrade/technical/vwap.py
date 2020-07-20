# PyAlgoTrade
#
# Copyright 2011-2018 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

from pyalgotrade import technical
from pyalgotrade.dataseries import bards


class VWAPEventWindow(technical.EventWindow):
    def __init__(self, windowSize, useTypicalPrice):
        super(VWAPEventWindow, self).__init__(windowSize, dtype=object)
        self.__useTypicalPrice = useTypicalPrice
        self.__cumTotal = 0    # cumulative total scope increased to class level
        self.__cumVolume = 0   # cumulative volume scope increased to class level
        self.__dateHolder = dt.datetime.now().date()  # new datetime variable, which will hold the date (YYYY-mm-dd) to be compared with bar in next iteration

    def getValue(self):
        ret = None
        if self.windowFull():
            cumTotal = 0
            cumVolume = 0

            for bar in self.getValues():
                if self.__dateHolder != bar.getDateTime().date() :   # if the date in dateHolder is not equal to date in the current bar
                    self.__cumTotal = 0    # reset the cumulative total, so that anchor point of vwap is set to opening of new day
                    self.__cumVolume = 0   # reset the cumulative volume also, so that anchor point of vwap is set to opening of new day
                    self.__dateHolder = bar.getDateTime().date() # and finally replace the date in dateHolder variable with the date of the current bar
                if self.__useTypicalPrice:
                    cumTotal += bar.getTypicalPrice() * bar.getVolume()
                else:
                    cumTotal += bar.getPrice() * bar.getVolume()
                cumVolume += bar.getVolume()

            try :
                ret = cumTotal / float(cumVolume)
            except ZeroDivisionError:
                if self.__useTypicalPrice:
                    ret = bar.getTypicalPrice()  # if divide by zero error, return typical price itself, if useTypicalPrice is set to true
                else :
                    ret = bar.getPrice()  # Otherwise return the normal price
        return ret


class VWAP(technical.EventBasedFilter):
    """Volume Weighted Average Price filter.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.bards.BarDataSeries`.
    :param period: The number of values to use to calculate the VWAP.
    :type period: int.
    :param useTypicalPrice: True if the typical price should be used instead of the closing price.
    :type useTypicalPrice: boolean.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, useTypicalPrice=False, maxLen=None):
        assert isinstance(dataSeries, bards.BarDataSeries), \
            "dataSeries must be a dataseries.bards.BarDataSeries instance"

        super(VWAP, self).__init__(dataSeries, VWAPEventWindow(period, useTypicalPrice), maxLen)
