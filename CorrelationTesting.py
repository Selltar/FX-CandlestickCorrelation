import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import pytz


# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)

print("Connecting.....")

# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()
else:
    print("Connection Successful")

timezone = pytz.timezone("Etc/UTC")  # set time zone to UTC
FirstCurrency = "AUDUSD"
SecondCurrency = "GBPUSD"

Timeframe = mt5.TIMEFRAME_M5  # data frequency/internval (eg. minutes, hourly, daily...etc)
Startdate = datetime(2022, 1, 7,
                     tzinfo=timezone)  # create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
AmountOfCandlesPerMonth = 5760
# 5M = 5760
# 15M = 1920
# 30M = 960
NumberOfMonths = 2
TimePeriod = AmountOfCandlesPerMonth * NumberOfMonths  # amount of data sets of your specified timeframe

print("Retrieving Data From MT5 Platform......")
# get data starting from specified dates in UTC time zone
Firstrates = mt5.copy_rates_from(FirstCurrency, Timeframe, Startdate, TimePeriod)
Secondrates = mt5.copy_rates_from(SecondCurrency, Timeframe, Startdate, TimePeriod)

mt5.shutdown()  # shut down connection to the MetaTrader 5 terminal

pd.set_option('display.max_columns', 30)  # number of columns to be displayed
pd.set_option('display.width', 500)  # max table width to display

# create DataFrame out of the obtained data
Firstdata = pd.DataFrame(Firstrates)
Firstdata['close'] = Firstdata['close'].astype(float)
Seconddata = pd.DataFrame(Secondrates)
Seconddata['close'] = Seconddata['close'].astype(float)
Firstdata.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Tick_volume', 'Spread', 'Real_volume']
Seconddata.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Tick_volume', 'Spread', 'Real_volume']

# extracting time from date dataset
Firstdata.insert(5, "Time", Firstdata['Date'], True)
Seconddata.insert(5, "Time", Seconddata['Date'], True)

# convert time in seconds into the datetime format
Firstdata['Time'] = pd.to_datetime(Firstdata['Time'], unit='s')
Seconddata['Time'] = pd.to_datetime(Seconddata['Time'], unit='s')

# Firstdata['Date'] = pd.to_datetime(Firstdata['Date'], unit='s')


print("Cleaning Datasets.....")
for i in range(len(Firstdata)):

    if Firstdata['Time'][i] in Seconddata['Time'].values:
        donothing = 'nothing'
    else:
        Firstdata.drop(i, inplace=True)

    if Seconddata['Time'][i] in Firstdata['Time'].values:
        donothing = 'nothing'
    else:
        Seconddata.drop(i, inplace=True)

Firstdata.index = range(len(Firstdata.index))
Seconddata.index = range(len(Seconddata.index))

# display data
print(Firstdata)
print(Seconddata)
print(len(Firstdata))
print(len(Seconddata))
print(Firstdata['Time'][0], Firstdata['Time'][100], Firstdata['Time'][len(Firstdata) - 1])
print(Seconddata['Time'][0], Seconddata['Time'][100], Seconddata['Time'][len(Seconddata) - 1])

# change df values to list
FirstDate = Firstdata['Date'].values
FirstTime = Firstdata['Time'].values
FirstOpenPrice = Firstdata['Open'].values
FirstHighPrice = Firstdata['High'].values
FirstLowPrice = Firstdata['Low'].values
FirstClosePrice = Firstdata['Close'].values
FirstSpread = Firstdata['Spread'].values
FirstTickVolume = Firstdata['Tick_volume'].values
FirstRealVolume = Firstdata['Real_volume'].values

SecondDate = Seconddata['Date'].values
SecondTime = Seconddata['Time'].values
SecondOpenPrice = Seconddata['Open'].values
SecondHighPrice = Seconddata['High'].values
SecondLowPrice = Seconddata['Low'].values
SecondClosePrice = Seconddata['Close'].values
SecondSpread = Seconddata['Spread'].values
SecondTickVolume = Seconddata['Tick_volume'].values
SecondRealVolume = Seconddata['Real_volume'].values


WinResultList = []
LossResultList = []
SignalList = []


class Results:
    def __init__(self, result, dateandtime, closeprice, openprice, volume, direction):
        self.result = result
        self.dateandtime = dateandtime
        self.closeprice = closeprice
        self.openprice = openprice
        self.volume = volume
        self.direction = direction


    def get_result(self):
        return self.result

    def get_dateandtime(self):
        return self.dateandtime

    def get_closeprice(self):
        return self.closeprice

    def get_openprice(self):
        return self.openprice

    def get_volume(self):
        return self.volume

    def get_direction(self):
        return self.direction


class Signals:
    def __init__(self, direction, dateandtime, closeprice, openprice, volume):
        self.direction = direction
        self.dateandtime = dateandtime
        self.closeprice = closeprice
        self.openprice = openprice
        self.volume = volume

    def get_direction(self):
        return self.direction

    def get_dateandtime(self):
        return self.dateandtime

    def get_closeprice(self):
        return self.closeprice

    def get_openprice(self):
        return self.openprice

    def get_volume(self):
        return self.volume


FirstTotalChange = []
SecondTotalChange = []
FirstandSecondDifference = []

print("Applying Strategy.....")
for i in range(len(Firstdata)):
    SignalPresent = ''
    BuyingOrSelling = ''

    #Get the hours of the day
    DateAndTimeFromString = FirstTime[i]
    TimeCountString = str(DateAndTimeFromString)
    WINTimeCount = TimeCountString.split("T")
    FinalTimeCount = WINTimeCount[1]
    FinalTimeCount = FinalTimeCount.replace("'", "")
    FinalTimeCount = FinalTimeCount.replace("]", "")
    FinalTimeCountString = str(FinalTimeCount)
    WINTimeCountTwo = FinalTimeCountString.split(':')
    FinalTimeCount = WINTimeCountTwo[0]
    #print(FinalTimeCount)
    FinalTimeCountInt = int(FinalTimeCount)

    if FinalTimeCountInt >= 10 and FinalTimeCountInt < 17: # Check candles between 10AM - 5PM

        # check if first currency candle is green
        if FirstOpenPrice[i] < FirstClosePrice[i]:

            SignalPresent = 'YES'
            BuyingOrSelling = 'GREEN'

            SignalV = Signals(BuyingOrSelling, FirstTime[i], FirstClosePrice[i], FirstOpenPrice[i], FirstTickVolume[i])
            SignalList.append(SignalV)

        # check if first currency candle is red
        elif FirstOpenPrice[i] > FirstClosePrice[i]:

            SignalPresent = 'YES'
            BuyingOrSelling = 'RED'

            SignalV = Signals(BuyingOrSelling, FirstTime[i], FirstClosePrice[i], FirstOpenPrice[i], FirstTickVolume[i])
            SignalList.append(SignalV)

        else:
            BuyingOrSelling = ''
            SignalPresent = ''

        if SignalPresent == "YES":

            for j in range(1):

                if j == 0:
                    j = i

                # check the candle color of first candle
                if BuyingOrSelling == "GREEN":

                    # check if second currency candle is green also
                    if SecondOpenPrice[j] < SecondClosePrice[j]:

                        ResultV = Results("CORRELATED", FirstTime[i], FirstClosePrice[i], FirstOpenPrice[i], FirstTickVolume[i], BuyingOrSelling)
                        WinResultList.append(ResultV)

                        break

                    elif SecondOpenPrice[j] > SecondClosePrice[j]:

                        ResultV = Results("NOTCORRELATED", FirstTime[i], FirstClosePrice[i], FirstOpenPrice[i], FirstTickVolume[i], BuyingOrSelling)
                        LossResultList.append(ResultV)

                        break

                # check candle color of first candle
                elif BuyingOrSelling == "RED":

                    # check if candle color is red also
                    if SecondOpenPrice[j] > SecondClosePrice[j]:

                        ResultV = Results("CORRELATED", FirstTime[i], FirstClosePrice[i], FirstOpenPrice[i], FirstTickVolume[i], BuyingOrSelling)
                        WinResultList.append(ResultV)

                        break

                    elif SecondOpenPrice[j] < SecondClosePrice[j]:

                        ResultV = Results("NOTCORRELATED", FirstTime[i], FirstClosePrice[i], FirstOpenPrice[i], FirstTickVolume[i], BuyingOrSelling)
                        LossResultList.append(ResultV)

                        break

                else:
                    donothing = 'nothing'


        else:
            useless = 2 + 2
            # print('NoTargetAnyway')

print("Applying Done")
print("Result:")
Dojicount = int(len(SignalList) - (len(WinResultList) + len(LossResultList)))
percentageCount = str(int(len(WinResultList) / len(SignalList) * 100))
percentageCount = percentageCount + "%"
Totalwinloss = len(WinResultList) + len(LossResultList)
percentageCountReal = str(int(len(WinResultList) / Totalwinloss * 100))
percentageCountReal = percentageCountReal + "%"
print('First Currency:', FirstCurrency)
print('Second Currency:', SecondCurrency)
print('Time Period', Timeframe)
print('No of Correlated Candles:', len(WinResultList))
print('No of Non-correlated Candles:', len(LossResultList))
print('Total Candles:', len(SignalList))
print('Correlation(%): ', percentageCountReal)

