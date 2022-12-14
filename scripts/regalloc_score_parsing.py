import sys

copyWeight = 0.2
loadWeight = 4.0
storeWeight = 1.0
cheapRematWeight = 0.2
expensiveRematWeight = 1.0

if __name__ == '__main__':
    with open(sys.argv[1]) as regalloc_score_file:
        raw_functions = regalloc_score_file.readlines()
        totalCopyCount = 0
        totalLoadCount = 0
        totalStoreCount = 0
        totalLoadStoreCount = 0
        totalExpensiveRematCount = 0
        totalCheapRematCount = 0
        for raw_function in raw_functions:
            components = raw_function.split(',')
            callCount = float(components[0])
            copyCount = float(components[1])
            loadCount = float(components[2])
            storeCount = float(components[3])
            loadStoreCount = float(components[4])
            expensiveRematCount = float(components[5])
            cheapRematCount = float(components[6])
            totalCopyCount += callCount * copyCount
            totalLoadCount += callCount * loadCount
            totalStoreCount += callCount * storeCount
            totalLoadStoreCount += callCount * loadStoreCount
            totalExpensiveRematCount += callCount * expensiveRematCount
            totalCheapRematCount += callCount * cheapRematCount
        totalCopy = totalCopyCount * copyWeight
        totalStore = totalStoreCount * storeWeight
        totalLoad = totalLoadCount * loadWeight
        totalLoadStore = totalLoadStoreCount * (loadWeight + storeWeight)
        totalExpensiveRemat = totalExpensiveRematCount * expensiveRematWeight
        totalCheapRemat = totalCheapRematCount * cheapRematWeight
        total = totalCopy + totalStore + totalLoad + totalLoadStore + totalExpensiveRemat + totalCheapRemat
        print(total, end='')
        