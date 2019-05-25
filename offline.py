#demand at time slot t, renewable energy, electricity market price where between m and M 
# 1. time t
# 2. demand
# 3. renewable energy generation 
# 4. electricity market price


# global variable: battery storage
import numpy as np
import math

NUM_EMPLOYEES = 100
PROB_ATTEND = 0.9
CONSUMPTION_PER_EMPLOYEE = 110.9
DEMAND_GUASSIAN_STD = 100
PRICE_GAUSSIAN_STD = 0.005
SOLAR_GAUSSIAN_STD = 200
HOURS_IN_DAY = 24
MAX_SOLAR_GEN = 9500

def getRandomNoiseArray(std_scale, num_elems):
	return np.random.normal(0, std_scale, num_elems)

#assume peak work hour is 12pm
def getSinusoidalDemand(t, numAtWork):
	return CONSUMPTION_PER_EMPLOYEE * numAtWork * math.sin((t/24.0)*math.pi)

def generateSolar(t):
	solarNoise = getRandomNoiseArray(SOLAR_GAUSSIAN_STD, 1)[0]
	solar = (MAX_SOLAR_GEN * math.sin((t/24.0) * math.pi)) + solarNoise
	return max(0, solar)

def generateDemand(t, numAttending):
	demandNoise = getRandomNoiseArray(DEMAND_GUASSIAN_STD, 1)[0]
	demand = getSinusoidalDemand(t, numAttending) + demandNoise
	return max(0, demand)

def generatePrice(t):
	price = 0
	if t > 13 and t < 19:
		price = 0.37729
	elif (t > 10 and t < 13) or (t > 19 and t < 21):
		price = 0.26202
	else:
		price = 0.18524
	return price + getRandomNoiseArray(PRICE_GAUSSIAN_STD, 1)[0]

def generateInput(): 
	numAttending = np.random.binomial(NUM_EMPLOYEES, PROB_ATTEND)
	print("num at work: {}".format(numAttending))
	data = []
	for t in range(HOURS_IN_DAY):
		demand = generateDemand(t, numAttending) 
		price = generatePrice(t)
		solar = generateSolar(t)
		eachStep = (t, demand, solar, price)
		data.append(eachStep)
	return data



class EnergyManagementSystem():
	def __init__(self, B_max):
		self.B_max = B_max
		self.battery_avail = 0
		self.profit = 0

	#fullDayDemands is an list of tuples; each tuple is an hour in 24 hour day 
	#representing(time, demand(t), renewable(t), electricity_price(t))
	def offlineAlgo(self, fullDayDemands):
		def drawFromRenewable():
			for index, t in enumerate(fullDayDemands): 
				tList = list(t)
				tList [1] -= tList[2]
				t = tuple(tList)
				fullDayDemands[index] = t


		max_price_tuple = max(fullDayDemands, key=lambda item:item[3]) #returns tuple w highest price
		max_price = max_price_tuple[3]
		max_price_index = max_price_tuple[0]
		# print("max price is {} at time {}".format(max_price, max_price_index))

		min_price_tuple = min(fullDayDemands, key=lambda item:item[3]) #returns tuple w highest price
		min_price = min_price_tuple[3]
		min_price_index = min_price_tuple[0]
		# print("min price is {} at time {}".format(min_price, min_price_index))

		max_demand_tuple = max(fullDayDemands, key=lambda item:item[1]) #returns tuple w highest price
		max_demand = max_price_tuple[1]
		max_demand_index = max_demand_tuple[0] 
		# print("max demand is {} at time {}".format(max_demand, max_demand_index))

		# print("before drawing from renewable:")
		# print("\t{}".format(fullDayDemands))
		drawFromRenewable()
		# print("after drawing from renewable: ")
		# print("\t{}".format(fullDayDemands))
		numSteps = len(fullDayDemands)
		for index, t in enumerate(fullDayDemands):
			# print("TIME {}: ".format(t[0]))
			
			tList = list(t)
			currDemand = tList[1]
			priceNow = tList[3]

			if currDemand > 0: #still have demand to meet: go to battery
				if self.battery_avail > 0 and self.battery_avail < currDemand: #have energy sitting in battery
					tList[1] -= self.battery_avail
					self.battery_avail = 0
				if self.battery_avail > 0 and self.battery_avail >= currDemand:
					tList[1] = 0
					self.battery_avail -= currDemand
			currDemand = tList[1]
			if currDemand > 0: #if battery couldnt satisfy
				self.profit -= priceNow*currDemand #buy to satisfy demand. have no excess to sell
				tList[1] = 0
			if index != numSteps - 1:
				priceNext = fullDayDemands[index+1][3]
				if priceNow < priceNext: #buy energy to fill up battery 
					self.profit -= (self.B_max - self.battery_avail)*priceNow #fill up battery, update cost
					self.battery_avail = self.B_max
				else:
					if self.battery_avail > 0:
						self.profit += priceNow*self.battery_avail
						self.battery_avail = 0
			fullDayDemands[index] = tuple(tList)
			# print("\tprofit is: {}".format(self.profit))
			# print("\tbattery capacity is: {}".format(self.battery_avail))
		# print("after offline algo: ")
		# print(fullDayDemands)
		return self.profit
		

def main():
	
	# for d in data:
		# print(d)
	# fullDayDemands = [(0, 5, 3, 6), (1, 6, 3, 9), (2, 4, 2, 3)]
	

	profits = []
	for x in range(1000):
		data = generateInput()
		EMS = EnergyManagementSystem(10000)
		p = EMS.offlineAlgo(data)
		profits.append(p)
		print(p)
	avgProfit = np.average(profits)
	print("average profit {}".format(avgProfit))



if __name__ == '__main__':
    main()

