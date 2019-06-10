#demand at time slot t, renewable energy, electricity market price where between m and M 
# 1. time t
# 2. demand
# 3. renewable energy generation 
# 4. electricity market price


import numpy as np
import math
import sys
from matplotlib import pyplot as plt

# General constants
PRICE_GAUSSIAN_STD = 0.005
HOURS_IN_DAY = 24

# Solar constants
AVG_SOLAR_GEN = 250
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
    solar_gen = np.random.normal(AVG_SOLAR_GEN * math.sin(math.pi * dayPassed) * cloudEffect * tempEffect,\
                                 SOLAR_GAUSSIAN_STD * math.sin(math.pi * dayPassed) * cloudEffect * tempEffect)
  return 0#max(0, solar_gen)

def generateDemand(t, numAttending, numHere):
  '''
  This generates the demand in kWh at a given timestep and returns it. Demand can never be below 0.

  Parameters:
  t            - The current timestep
  numAttending - The number of employees going to work on a particular day
  
  Return:
  This function returns the demand at a given timestep in kWh.
  '''
  people = 0
  if t >= 20 or t < 7:
    # LOW DEMAND: from 8PM to 7AM
    demand = np.random.normal(LOW_DEMAND_AVG, LOW_DEMAND_VAR ** 0.5)
  elif t >= 9 and t < 17:
    # HIGH DEMAND: from 9AM to 5PM
    demand = np.random.normal(HIGH_DEMAND_NO_PPL_AVG + numAttending * CONSUMPTION_PER_EMPLOYEE, \
                              (HIGH_DEMAND_NO_PPL_VAR + numAttending * EMPLOYEE_VAR) ** 0.5)
    people = numAttending
  elif t >= 7 and t < 9:
    # RAMP UP TO HIGH DEMAND: from 7AM to 9AM
    # Assuming .3 probability to show up before 7, .6 probability to show up before 8
    showedUp = max(numHere, np.random.binomial(numAttending, PROB_EARLY * (t - 6)))
    demand = np.random.normal(HIGH_DEMAND_NO_PPL_AVG + numHere * CONSUMPTION_PER_EMPLOYEE, \
               (HIGH_DEMAND_NO_PPL_VAR + numHere * EMPLOYEE_VAR) ** 0.5)\
            + np.random.normal((showedUp - numHere) * CONSUMPTION_PER_EMPLOYEE,\
                               ((showedUp - numHere) * EMPLOYEE_VAR) ** 0.5) / 2
    people = showedUp
  elif t >= 17 and t < 20:
    # RAMP DOWN TO LOW DEMAND: from 5PM to 8PM
    # Assuming 0.45 chance to remain after 5, 0.3 after 6, 0.15 after 7
    stayedLate = min(numHere, np.random.binomial(numAttending, PROB_STAY_LATE * (20 - t)))
    demand = np.random.normal(HIGH_DEMAND_NO_PPL_AVG + numHere * CONSUMPTION_PER_EMPLOYEE, \
                              (HIGH_DEMAND_NO_PPL_VAR + numHere * EMPLOYEE_VAR) ** 0.5)\
            + np.random.normal((stayedLate - numHere) * CONSUMPTION_PER_EMPLOYEE,\
                              (abs(stayedLate - numHere) * EMPLOYEE_VAR) ** 0.5) / 2
    people = stayedLate
  return (max(0, demand), people) # demand < 0 rarely happens, but we want to guard against this possibility anyway

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
  prevPeople = 0
  for t in range(HOURS_IN_DAY):
    demand, prevPeople = generateDemand(t, numAttending, prevPeople)
    if t > 0:
      price = generatePrice(t, demand, data[t - 1][1])
    else:
      price = generatePrice(t, demand, 0)
    solar = generateSolar(t, weather)
    eachStep = (t, demand, prevPeople, solar, price)
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
  
  # PREDICTION FUNCTIONS BELOW

  def predictDemand(self, t, people):
    if t >= 20 or t < 7:
      demand = LOW_DEMAND_AVG
    elif t == 9:
      demand = HIGH_DEMAND_NO_PPL_AVG + people / 0.6 * CONSUMPTION_PER_EMPLOYEE
    elif t > 9 and t < 17:
      demand = HIGH_DEMAND_NO_PPL_AVG + people * CONSUMPTION_PER_EMPLOYEE
    elif t == 7:
      demand = HIGH_DEMAND_NO_PPL_AVG + NUM_EMPLOYEES * PROB_ATTEND * CONSUMPTION_PER_EMPLOYEE * PROB_EARLY
    elif t == 8:
      demand = HIGH_DEMAND_NO_PPL_AVG + people * 2 * CONSUMPTION_PER_EMPLOYEE
    elif t == 17:
      demand = HIGH_DEMAND_NO_PPL_AVG + people * PROB_STAY_LATE * 3 * CONSUMPTION_PER_EMPLOYEE
    elif t == 18:
      demand = HIGH_DEMAND_NO_PPL_AVG + people * 2 / 3 * CONSUMPTION_PER_EMPLOYEE
    elif t == 19:
      demand = HIGH_DEMAND_NO_PPL_AVG + people * 1 / 2 * CONSUMPTION_PER_EMPLOYEE
    return max(0, demand)

  def predictPrice(self, t, predDemand, currDemand):
    price = 0
    if t >= 9 and t < 14:
      price = 0.37729
    elif (t >= 14 and t < 16) or (t >= 6 and t < 9):
      price = 0.26202
    else:
      price = 0.18524
    if t not in [0, 6, 9, 14, 16]:
      if predDemand > currDemand:
        price += math.log(predDemand - currDemand) * 0.02
      elif currDemand > predDemand:
        price -= math.log(currDemand - predDemand) * 0.02
    return max(0, price)

  # OFFLINE ALGORITHM BELOW

  def offlineAlgo(self, fullDayDemands):
    '''
    fullDayDemands is an list of tuples; each tuple is an hour in 24 hour day 
    representing(time, demand(t), renewable(t), electricity_price(t))
    '''
    self.battery_avail = 0
    self.profit = 0
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, people, solar, price = fullDayDemands[index]
      if index < numSteps - 1:
        predPrice = fullDayDemands[index + 1][4]
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

  # ONLINE ALGORITHMS BELOW

  def onlineAlgo(self, fullDayDemands):
    self.battery_avail = 0
    self.profit = 0
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, people, solar, price = fullDayDemands[index]
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

  def onlineAlgoBetter(self, fullDayDemands):
    self.battery_avail = 0
    self.profit = 0
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, people, solar, price = fullDayDemands[index]
      predPrice = self.predictPrice(t + 1, self.predictDemand(t + 1, people), demand) # need to write these functions
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

  # Online baseline -- random price predictor
  def onlineAlgoRandom(self, fullDayDemands):
    self.battery_avail = 0
    self.profit = 0
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, people, solar, price = fullDayDemands[index]
      predPrice = np.random.random_sample() * 0.45 + 0.05
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
  # Greedy baseline
  def baseline(self, fullDayDemands):
    self.battery_avail = 0
    self.profit = 0 
    numSteps = len(fullDayDemands)
    for index in range(numSteps):
      t, demand, people, solar, price = fullDayDemands[index]
      self.profit += (solar - demand) * price
    return self.profit



def main():
  np.random.seed(42)
  offline_profits = []
  online_profits = []
  online_better_profits = []
  baseline_profits = []
  random_profits = []
  online_ratios = []
  online_better_ratios = []
  baseline_ratios = []
  random_ratios = []
  data_list = []
  for x in range(100000):
    weather = generateWeather()
    data = generateInput(weather)
    data_list.append(data)
    EMS = EnergyManagementSystem(180)
    offline = EMS.offlineAlgo(data)
    online = EMS.onlineAlgo(data)
    online_better = EMS.onlineAlgoBetter(data)
    baseline = EMS.baseline(data)
    random = EMS.onlineAlgoRandom(data)
    offline_profits.append(offline)
    online_profits.append(online)
    online_better_profits.append(online_better)
    baseline_profits.append(baseline)
    random_profits.append(random)
    online_ratios.append(online / offline)
    online_better_ratios.append(online_better / offline)
    baseline_ratios.append(baseline / offline)
    random_ratios.append(random / offline)
  avgOfflineProfit = np.average(offline_profits)
  avgOnlineProfit = np.average(online_profits)
  avgOnlineBetterProfit = np.average(online_better_profits)
  avgBaselineProfit = np.average(baseline_profits)
  avgRandomProfit = np.average(random_profits)
  avgOnlineRatio = avgOnlineProfit / avgOfflineProfit
  avgOnlineBetterRatio = avgOnlineBetterProfit / avgOfflineProfit
  avgBaselineRatio = avgBaselineProfit / avgOfflineProfit
  avgRandomRatio = avgRandomProfit / avgOfflineProfit
  print('Average offline profit:\t {}\nAverage online profit:\t {}\nAverage online (better predictor) profit:\t {}\nAverage baseline profit: {}\nAverage random profit:\t {}'.format(avgOfflineProfit, avgOnlineProfit, avgOnlineBetterProfit, avgBaselineProfit, avgRandomProfit))
  print('Worst online ratio:\t {}\nAverage online ratio:\t {}'.format(max(online_ratios), avgOnlineRatio))
  print('Worst online (better predictor) ratio:\t {}\nAverage online (better predictor) ratio:\t {}'.format(max(online_better_ratios), avgOnlineBetterRatio))
  print('Worst baseline ratio:\t {}\nAverage baseline ratio:\t {}'.format(max(baseline_ratios), avgBaselineRatio))
  print('Worst random ratio:\t {}\nAverage random ratio:\t {}'.format(max(random_ratios), avgRandomRatio))
  i = online_ratios.index(max(online_ratios))
  worst_case = data_list[i] # (t, demand, solar, price)
  worst_demand = []
  worst_solar = []
  worst_price = []
  for d in worst_case:
    worst_demand.append(d[1])
    worst_solar.append(d[3])
    worst_price.append(d[4])
  plt.figure()
  plt.subplot(211)
  plt.title('Worst Case Data')
  plt.plot(worst_demand, label='demand', color='red')
  plt.plot(worst_solar, label='solar', color='green')
  plt.ylabel('kWh')
  plt.legend()
  plt.subplot(212)
  plt.plot(worst_price, label='price', color='blue')
  plt.ylabel('USD/kWh')
  plt.xlabel('Timestep')
  plt.legend()
  plt.show()
  print(offline_profits[i], online_profits[i])


if __name__ == '__main__':
    main()

