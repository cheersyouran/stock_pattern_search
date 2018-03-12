from codes.config import config
import os
import pandas as pd
import numpy as np
from memory_profiler import profile

class Market:
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        print('Init Market! ', os.getpid())
        self.all_data = None
        self._init_all_data(config.speed_method)

        self.codes = None
        self._init_codes()

        self.trading_days = None
        self._init_trading_days()

        self.pattern = None
        self.targets = None
        self.current_date = self.pass_days(config.start_date, config.pattern_length - 1)

    def _init_all_data(self, speed_method=config.speed_method):

        if speed_method == 'fft_euclidean':
            file = config.ZZ800_FFT_DATA
        elif speed_method == 'value_ratio_fft_euclidean':
            file = config.ZZ800_VALUE_RATIO_FFT_DATA
        elif speed_method == 'rm_market_vr_fft':
            file = config.ZZ800_RM_VR_FFT

        if self.all_data is None:
            print('Init All Data! ', os.getpid())
            self.all_data = pd.read_csv(file, parse_dates=['DATE'], low_memory=False)

    def _init_codes(self):
        if config.market_index == 300:
            path = config.HS300_CODES
        elif config.market_index == 800:
            path = config.ZZ800_CODES
        else:
            raise Exception()
        self.codes = pd.read_csv(path).head(config.nb_codes).values.flatten()

    def _init_trading_days(self):
        self.trading_days = pd.read_csv(config.TRAINING_DAY, parse_dates=['DATE'])

    def _pass_a_day(self):
        self.current_date = pd.to_datetime(self.trading_days[self.trading_days['DATE'] > self.current_date].head(1).values[0][0])
        config.start_date = pd.to_datetime(self.trading_days[self.trading_days['DATE'] > config.start_date].head(1).values[0][0])

    def _pass_a_week(self):
        self.current_date = pd.to_datetime(self.trading_days[self.trading_days['DATE'] > self.current_date].head(5).tail(1).values[0][0])
        config.start_date = pd.to_datetime(self.trading_days[self.trading_days['DATE'] > config.start_date].head(5).tail(1).values[0][0])

    def get_historical_data(self, start_date=None, end_date=None, code=config.code):

        targets = self.all_data[self.all_data['CODE'] != code].reset_index(drop=True)
        targets = targets[targets['DATE'] < market.current_date.date()]

        if start_date == None and end_date != None:
            self.pattern = self.all_data[(self.all_data['CODE'] == code) & (self.all_data['DATE'] <= end_date)].tail(config.pattern_length)
        elif start_date != None and end_date == None:
            self.pattern = self.all_data[(self.all_data['CODE'] == code) & (self.all_data['DATE'] >= start_date)].head(config.pattern_length)
        elif start_date != None and end_date != None:
            self.pattern = self.all_data[(self.all_data['CODE'] == code) & (self.all_data['DATE'] <= end_date) & (self.all_data['DATE'] >= start_date)]

        self.pattern = self.pattern.reset_index(drop=True)
        self.targets = targets
        self.targets = self.targets.dropna()

        return self.all_data, self.pattern, self.targets

    def get_data(self, start_date=None, end_date=None, code=None, pattern_length=config.pattern_length):

        all_data = self.all_data

        if code is not None:
            if start_date == None and end_date != None:
                pattern = all_data[(all_data['CODE'] == code) & (all_data['DATE'] <= end_date)].tail(pattern_length)
            elif start_date != None and end_date == None:
                pattern = all_data[(all_data['CODE'] == code) & (all_data['DATE'] >= start_date)].head(pattern_length)
            elif start_date != None and end_date != None:
                pattern = all_data[(all_data['CODE'] == code) & (all_data['DATE'] <= end_date) & (all_data['DATE'] >= start_date)]
        else:
            if start_date == None and end_date != None:
                pattern = all_data[(all_data['DATE'] <= end_date)].tail(pattern_length)
            elif start_date != None and end_date == None:
                pattern = all_data[(all_data['DATE'] >= start_date)].head(pattern_length)
            elif start_date != None and end_date != None:
                pattern = all_data[(all_data['DATE'] <= end_date) & (all_data['DATE'] >= start_date)]

        return pattern

    def pass_days(self, date, nb_day):
        date_ = pd.to_datetime(self.trading_days[self.trading_days['DATE'] > date].head(nb_day).tail(1).values[0][0])
        return date_

    def get_span_market_ratio(self, df, n):
        array = np.cumprod(df[config.market_ratio_type] / 100 + 1).values - 1
        return array[n]


market = Market()