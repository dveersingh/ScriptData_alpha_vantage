
import pandas as pd 
import numpy as np

from alpha_vantage.timeseries import TimeSeries

from pyalgotrading.utils import func 
from pyalgotrading.constants import PlotType


class ScriptData:
    
    
    def __init__(self):
        self._dict = {}
        self.api_key = 'H3UKOVC7728S4FJF'       # key of alpha vantage api
        self.output_format ='pandas'            #output format
        self.interval = '5min'                  # interval for market data
        
    def __getitem__(self, script):
        if self.__contains__(script):
            return self._dict[script]
        return "NO Key Found"
        
           
    def __setitem__(self, script, val):
            self._dict[script] = val

    def __contains__(self, script):
            
        if script in self._dict :
            return True 
        else 
            return False
        
        
    def fetch_intraday_data(self, script): 
        ts = TimeSeries(key= self.api_key, output_format=self.output_format)
        #calling alpha vantage api
        
        data, meta_data = ts.get_intraday(symbol=script,interval=self.interval, outputsize='full')
        self.__setitem__(script, data)
        
        ## set the data in _dict (key = script)
    
    
    def convert_intraday_data(self, script):
        data = self.__getitem__(script)
        #getting data from _dict
        
        df = pd.DataFrame(data).reset_index(level=0)
        # creating panda dataframe and reset the index
        
        df.rename(columns = {'date':'timestamp', 
                             '1. open':'open',
                             '2. high':'high',
                             '3. low':'low',
                             '4. close':'close',
                             '5. volume':'volume'}, 
                              inplace = True )
        
        #renamed the column names
        
        self.__setitem__(script, df)
        # update the df in _dict 
        
 


def indicator1(df, timeperiod):
    
    indicator_df = pd.DataFrame({ 
                         "timestamp":df["timestamp"],
                         "indicator":df['close'].rolling(window=timeperiod).mean()
                          })
    
    """ creating new dataframe with 2 colums and calculating 
        moving average of close column
    """
    return indicator_df



class Strategy:
    def __init__(self, script):
        self.script = script
        self.timeperiod = 5
       
        
    def get_script_data(self):
        self.script_data = ScriptData()
        self.script_data.fetch_intraday_data(self.script)
        self.script_data.convert_intraday_data(self.script)
        #script_data[self.script]
    
    def get_signals(self):
        indicator_data = indicator1(
                             self.script_data[self.script],  
                             self.timeperiod )
        
        self.temp_df = pd.merge(self.script_data[self.script], 
                           indicator_data, on='timestamp')
        #merging df and indicator_df o timestamp and creating temp_df
        
        del indicator_data
        
        self.temp_df['Diff'] = self.temp_df.close - self.temp_df.indicator
        """ Difference of close_data and indicator data """
        
        self.temp_df['signal'] = np.select([((self.temp_df.Diff < 0) & (self.temp_df.Diff.shift() > 0)),
                                     ((self.temp_df.Diff > 0) & (self.temp_df.Diff.shift() < 0))], 
                                     ['BUY', 'SELL'], 'None')
        """  
             diff < 0 and next index of diff > 0 then BUY
             diff > 0 and next index of diff  < 0 then SELL
         """
        
        signals = self.temp_df.loc[self.temp_df['signal'].isin(['BUY','SELL'])]
        
        """ Checking signal = BUY or SELL and then accessing only those rows """
        
        signals = pd.DataFrame({'timestamp':signals['timestamp'],
                      'signal':signals['signal']}).reset_index(drop=True)
        
        """ created new df --> signals with 2 column -> timestamp and signal"""
        
        return signals
    
    
    
    
    def plot_candlestick(self):
        
        """ Function for plotting the candlestic chart"""
        func.plot_candlestick_chart(self.temp_df.head(100), 
            PlotType.JAPANESE, 
            caption='', 
            hide_missing_dates=False, 
            show=True, 
            indicators=([{
                'name':'SMA',
                'data':self.temp_df['indicator'].head(100)}]), 
            plot_indicators_separately=False, 
            plot_height=500, plot_width=1000 )





