import sys

copyWeight = 0.2
loadWeight = 4.0
storeWeight = 1.0
cheapRematWeight = 0.2
expensiveRematWeight = 1.0

if __name__ == '__main__':
    # parse call counts
    callCounts = {}
    with open(sys.argv[2]) as call_count_file:
        raw_call_counts = call_count_file.readlines()
        for raw_function in raw_call_counts:
            components = raw_function.split(',')
            callCounts[components[0]] = int(components[1])

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
            copyCount = float(components[0])
            loadCount = float(components[1])
            storeCount = float(components[2])
            loadStoreCount = float(components[3])
            expensiveRematCount = float(components[4])
            cheapRematCount = float(components[5])
            functionName = components[6].replace('\n','')
            callCount = callCounts[functionName]
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
    
