import subprocess
import sys

import get_bbs

def getThroughputFromHex(inputHex):
    uiCACommandVector = ["python3", "/uiCA/uiCA.py", "-hex", inputHex, '-arch',
                         'SNB']
    with subprocess.Popen(uiCACommandVector, stdout=subprocess.PIPE) as uiCAProcess:
        out, err = uiCAProcess.communicate()
        allLines = out.decode("UTF-8").split('\n')
        throughput = float(allLines[0].split(': ')[1])
        return throughput

def loadFrequencies(frequencyFileName, functionName):
    # format of frequency file is
    # function name, mbb id, relative frequency (float)
    rawMBBData = []
    with open(frequencyFileName) as frequencyFile:
        for line in frequencyFile:
            tokens = line.strip().split(',')
            rawMBBData.append((tokens[0], int(tokens[1]), float(tokens[2])))
    mbbFrequencies = {}
    for rawMBB in rawMBBData:
        if rawMBB[0] == functionName:
            mbbFrequencies[rawMBB[1]] = rawMBB[2]
    return mbbFrequencies

def getBasicBlockCycleMap(basicBlockHexMap):
    basicBlockCycleMap = {}
    for id in basicBlockHexMap:
        basicBlockCycleMap[id] = getThroughputFromHex(basicBlockHexMap[id])
    return basicBlockCycleMap

def getWeightedCycleCount(basicBlockCycleMap, frequencyMap):
    totalCycleCount = 0
    for id in basicBlockCycleMap:
        totalCycleCount += basicBlockCycleMap[id] * frequencyMap[id]
    return totalCycleCount

def getWeightedCycleCountFromFiles(executable, frequencyDump, functionName):
    frequencyMap = loadFrequencies(frequencyDump, functionName)
    bbHexMap = get_bbs.getBasicBlockHexMap(executable, functionName)
    
    bbCycleMap = getBasicBlockCycleMap(bbHexMap)
    
    return getWeightedCycleCount(bbCycleMap, frequencyMap)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 process_bbs.py <executable> <frequency dump>")
        sys.exit(1)
    
    executable = sys.argv[1]
    frequencyDump = sys.argv[2]
    totalCycles = getWeightedCycleCountFromFiles(executable, frequencyDump, "main")

    print(totalCycles)
