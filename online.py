#demand at time slot t, renewable energy, electricity market price where between m and M 
# 1. time t
# 2. demand
# 3. renewable energy generation 
# 4. electricity market price


# global variable: battery storage
import numpy as np
import math

# General constants
PRICE_GAUSSIAN_STD = 0.005
HOURS_IN_DAY = 24

# Solar constants
AVG_SOLAR_GEN = 200
SOLAR_GAUSSIAN_STD = 50

# Worker constants
# Assuming every worker operates independently
NUM_EMPLOYEES = 100
PROB_ATTEND = 0.9
PROB_EARLY = 0.3
PROB_STAY_LATE = 0.15
CONSUMPTION_PER_EMPLOYEE = 0.2
EMPLOYEE_VAR = 0.05 ** 2

# Demand constants
LOW_DEMAND_AVG = 100             # security system, temp. control, etc.
LOW_DEMAND_VAR = 10 ** 2
HIGH_DEMAND_NO_PPL_AVG = 150     # low demand stuff + lights
HIGH_DEMAND_NO_PPL_VAR = 10 ** 2 + 5 ** 2  # high demand w/o people is actually two normals added together

# Weather constants
CLOUD_COVER_MULTPLIER = 0.3
TEMP_STD = 3
TEMP_MULTIPLIER = 0.00143

def generateWeather():
  # roll for season
  season = np.random.random()
  cloudy = np.random.random()
  if season < 0.25:
    # Winter
    
    # Generate cloud cover
    if cloudy < 0.45:
      # Partial coverage -- triangular distribution
      cloudCover = np.random.triangular(0.0, 0.7, 1.0)
    elif cloudy < 0.65:
      # Full coverage
      cloudCover = 1.0
    else:
      # Clear
      cloudCover = 0.0

    # Generate temperatures
    highTemp = np.random.normal(60, 25)
    lowTemp = np.random.normal(40, 16)
    if highTemp < lowTemp:
      t = highTemp
      highTemp = lowTemp
      lowTemp = t
    # Generate sunrise and sunset
    sunrise = np.random.choice([6, 7])
    sunset = np.random.choice([17, 18])
  elif season < 0.5:
    # Spring

    # Generate cloud cover -- triangular distribution
    if cloudy < 0.35:
      # Partial coverage
      cloudCover = np.random.triangular(0.0, 0.4, 1.0)
    elif cloudy < 0.5:
      # Full coverage
      cloudCover = 1.0
    else:
      # Clear
      cloudCover = 0.0

    # Generate temperatures
    highTemp = np.random.normal(70, 25)
    lowTemp = np.random.normal(45, 36)
    if highTemp < lowTemp:
      t = highTemp
      highTemp = lowTemp
      lowTemp = t
    # Generate sunrise and sunset
    sunrise = np.random.choice([6, 7])
    sunset = np.random.choice([18, 19, 20])
  elif season < 0.75:
    # Summer

    # Generate cloud cover -- triangular distribution
    if cloudy < 0.2:
      # Partial coverage
      cloudCover = np.random.triangular(0.0, 0.1, 1.0)
    elif cloudy < 0.25:
      # Full coverage
      cloudCover = 1.0
    else:
      # Clear
      cloudCover = 0.0

    # Generate temperatures
    highTemp = np.random.normal(80, 36)
    lowTemp = np.random.normal(55, 16)
    if highTemp < lowTemp:
      t = highTemp
      highTemp = lowTemp
      lowTemp = t
    # Generate sunrise and sunset
    sunrise = np.random.choice([5, 6])
    sunset = np.random.choice([20, 21])
  else:
    # Autumn
    if cloudy < 0.35:
      # Partial coverage -- triangular distribution
      cloudCover = np.random.triangular(0.0, 0.5, 1.0)
    elif cloudy < 0.5:
      # Full coverage
      cloudCover = 1.0
    else:
      # Clear
      cloudCover = 0.0

    # Generate temperatures
    highTemp = np.random.normal(65, 25)
    lowTemp = np.random.normal(43, 16)
    if highTemp < lowTemp:
      t = highTemp
      highTemp = lowTemp
      lowTemp = t
    # Generate sunrise and sunset
    sunrise = np.random.choice([6, 7])
    sunset = np.random.choice([18, 19, 20])
  return (cloudCover, highTemp, lowTemp, sunrise, sunset)

def generateSolar(t, weather):
  '''
  Generates solar power generation at given timestep
  '''
  cloudCover, highTemp, lowTemp, sunrise, sunset = weather
  if t < sunrise or t > sunset:
    # Before sunrise or after sunset
    solar_gen = 0
  else:
    # During the day
    cloudEffect = 1 - cloudCover * CLOUD_COVER_MULTPLIER
    dayPassed = float(t - sunrise) / (sunset - sunrise)
    temp = np.random.normal((- (highTemp - lowTemp) * math.cos(dayPassed * 2 * math.pi) + highTemp + lowTemp) / 2, TEMP_STD)
    tempEffect = 1 - max(0, temp - 77) * TEMP_MULTIPLIER
    solar_gen = np.random.normal(AVG_SOLAR_GEN * math.sin(math.pi * dayPassed) * cloudEffect * tempEffect, SOLAR_GAUSSIAN_STD * cloudEffect * tempEffect)
  return max(0, solar_gen)

def generateDemand(t, numAttending):
  '''
  This generates the demand in kWh at a given timestep and returns it. Demand can never be below 0.

  Parameters:
  t            - The current timestep
  numAttending - The number of employees going to work on a particular day
  
  Return:
  This function returns the demand at a given timestep in kWh.
  '''
  if t >= 20 or t < 7:
    # LOW DEMAND: from 8PM to 7AM
    demand = np.random.normal(LOW_DEMAND_AVG, LOW_DEMAND_VAR ** 0.5)
  elif t >= 9 and t < 17:
    # HIGH DEMAND: from 9AM to 5PM
    demand = np.random.normal(HIGH_DEMAND_NO_PPL_AVG + numAttending * CONSUMPTION_PER_EMPLOYEE, \
                              (HIGH_DEMAND_NO_PPL_VAR + numAttending * EMPLOYEE_VAR) ** 0.5)
  elif t >= 7 and t < 9:
    # RAMP UP TO HIGH DEMAND: from 7AM to 9AM
    # Assuming .3 probability to show up before 7, .6 probability to show up before 8
    showedUp = np.random.binomial(numAttending, PROB_EARLY * (t - 6))
    demand = np.random.normal(HIGH_DEMAND_NO_PPL_AVG + showedUp * CONSUMPTION_PER_EMPLOYEE, \
                              (HIGH_DEMAND_NO_PPL_VAR + showedUp * EMPLOYEE_VAR) ** 0.5)
  elif t >= 17 and t < 20:
    # RAMP DOWN TO LOW DEMAND: from 5PM to 8PM
    # Assuming 0.45 chance to remain after 5, 0.3 after 6, 0.15 after 7
    stayedLate = np.random.binomial(numAttending, PROB_STAY_LATE * (20 - t))
    demand = np.random.normal(HIGH_DEMAND_NO_PPL_AVG + stayedLate * CONSUMPTION_PER_EMPLOYEE, \
                              (HIGH_DEMAND_NO_PPL_VAR + stayedLate * EMPLOYEE_VAR) ** 0.5)
  return max(0, demand) # demand < 0 rarely happens, but we want to guard against this possibility anyway

def generatePrice(t, currDemand, prevDemand):
  '''
  Generates price
  '''
  price = 0
  if t >= 9 and t < 14:
    price = 0.37729
  elif (t >= 14 and t < 16) or (t >= 6 and t < 9):
    price = 0.26202
  else:
    price = 0.18524
  if t not in [0, 6, 9, 14, 16]:
    if currDemand > prevDemand:
      price += math.log(currDemand - prevDemand) * 0.02
    elif currDemand < prevDemand:
      price -= math.log(prevDemand - currDemand) * 0.02
  return max(0, np.random.normal(price, PRICE_GAUSSIAN_STD))

def generateInput(weather): 
  numAttending = np.random.binomial(NUM_EMPLOYEES, PROB_ATTEND)
  data = []
  for t in range(HOURS_IN_DAY):
    demand = generateDemand(t, numAttending)
    if t > 0:
      price = generatePrice(t, demand, data[t - 1][1])
    else:
      price = generatePrice(t, demand, 0)
    solar = generateSolar(t, weather)
    eachStep = (t, demand, solar, price)
    data.append(eachStep)
  return data



class EnergyManagementSystem():
  def __init__(self, B_max):
    self.B_max = B_max
    self.battery_avail = 0
    self.profit = 0
    self.priceTable = {}
    for t in range(9, 14):
      self.priceTable[t] = 0.37729
    for t in range(6, 9):
      self.priceTable[t] = 0.26202
    for t in range(14, 16):
      self.priceTable[t] = 0.26202
    for t in range(0, 6):
      self.priceTable[t] = 0.18524
    for t in range(16, 24):
      self.priceTable[t] = 0.18524
    self.priceTable[24] = 0
  
  def offlineAlgo(self, fullDayDemands):
    '''
    fullDayDemands is an list of tuples; each tuple is an hour in 24 hour day 
    representing(time, demand(t), renewable(t), electricity_price(t))
    '''
    self.battery_avail = 0
    self.profit = 0
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, solar, price = fullDayDemands[index]
      if index < numSteps - 1:
        predPrice = fullDayDemands[index + 1][3]
      else:
        predPrice = 0

      if demand > solar + self.battery_avail:
        # not enough energy to meet demand
        self.profit -= (demand - (solar + self.battery_avail)) * price
        self.battery_avail = 0
      elif demand <= solar + self.battery_avail:
        # generate excess energy
        self.battery_avail = solar + self.battery_avail - demand
        if self.battery_avail > self.B_max:
          self.profit += (self.battery_avail - self.B_max) * price
          self.battery_avail = self.B_max

      if price > predPrice:
        # price predicted to decrease at next timestep
        if self.battery_avail > 0:
          self.profit += self.battery_avail * price
          self.battery_avail = 0
      else:
        # price predicted to increase at next timestep
        self.profit -= (self.B_max - self.battery_avail) * price
        self.battery_avail = self.B_max
    return self.profit

  def onlineAlgo(self, fullDayDemands):
    self.battery_avail = 0
    self.profit = 0
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, solar, price = fullDayDemands[index]
      predPrice = self.priceTable[t + 1]
      if demand > solar + self.battery_avail:
        # not enough energy to meet demand
        self.profit -= (demand - (solar + self.battery_avail)) * price
        self.battery_avail = 0
      elif demand <= solar + self.battery_avail:
        # generate excess energy
        self.battery_avail = solar + self.battery_avail - demand
        if self.battery_avail > self.B_max:
          self.profit += (self.battery_avail - self.B_max) * price
          self.battery_avail = self.B_max

      if price > predPrice:
        # price predicted to decrease at next timestep
        if self.battery_avail > 0:
          self.profit += self.battery_avail * price
          self.battery_avail = 0
      else:
        # price predicted to increase at next timestep
        if t != numSteps - 1:
          self.profit -= (self.B_max - self.battery_avail) * price
          self.battery_avail = self.B_max
    return self.profit

  def baseline(self, fullDayDemands):
    self.battery_avail = 0
    self.profit = 0
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, solar, price = fullDayDemands[index]
      self.profit += (solar - demand) * price
    return self.profit



def main():
  offline_profits = []
  online_profits = []
  baseline_profits = []
  online_ratios = []
  baseline_ratios = []
  for x in range(100000):
    weather = generateWeather()
    data = generateInput(weather)
    EMS = EnergyManagementSystem(180)
    offline = EMS.offlineAlgo(data)
    online = EMS.onlineAlgo(data)
    baseline = EMS.baseline(data)
    offline_profits.append(offline)
    online_profits.append(online)
    baseline_profits.append(baseline)
    online_ratios.append(online / offline)
    baseline_ratios.append(baseline / offline)
  avgOfflineProfit = np.average(offline_profits)
  avgOnlineProfit = np.average(online_profits)
  avgBaselineProfit = np.average(baseline_profits)
  avgOnlineRatio = np.average(online_ratios)
  avgBaselineRatio = np.average(baseline_ratios)
  print('Average offline profit:\t {}\nAverage online profit:\t {}\nAverage baseline profit: {}'.format(avgOfflineProfit, avgOnlineProfit, avgBaselineProfit))
  print('Worst online ratio:\t {}\nAverage online ratio:\t {}'.format(max(online_ratios), avgOnlineRatio))
  print('Worst baseline ratio:\t {}\nAverage baseline ratio:\t {}'.format(max(baseline_ratios), avgBaselineRatio))

if __name__ == '__main__':
    main()

