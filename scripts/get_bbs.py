import subprocess
import sys
import json
import binascii

def hexStringToSeparatedHexString(inputString):
    toReturn = ""
    for index in range(0, len(inputString), 2):
        toReturn += "0x" + inputString[index:index+2] + " "
    return toReturn

def getAssembly(inputString):
    commandVector = ["/llvm-install/bin/llvm-mc", "-disassemble"]
    with subprocess.Popen(commandVector, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE) as disassembleProcess:
        out, err = disassembleProcess.communicate(input=inputString.encode())
        return out.decode("UTF-8")

def getBBAddrMap(inputFile):
    BBAddrMapCommandVector = [
        "/llvm-project/build/bin/llvm-readelf", "--bb-addr-map",
        "--elf-output-style=JSON", inputFile
    ]
    with subprocess.Popen(BBAddrMapCommandVector,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as ReadElfProcess:
        out, err = ReadElfProcess.communicate()
        return json.loads(out.decode("UTF-8"))

def getBasicBlocks(inputFile, functionName):
    bbaddrmap = getBBAddrMap(inputFile)

    functionIndex = 0
    for index, function in enumerate(bbaddrmap[0]["BBAddrMap"]):
        if function["Function"]["Name"] == functionName:
            functionIndex = index
            break

    
    functionStart = bbaddrmap[0]["BBAddrMap"][functionIndex]["Function"]["At"]
    BasicBlocks = []
    for bbEntry in bbaddrmap[0]["BBAddrMap"][functionIndex]["Function"]["BB entries"]:
        newBasicBlock = {
            "offset": bbEntry["Offset"],
            "id": bbEntry["ID"],
            "size": bbEntry["Size"]
        }
        BasicBlocks.append(newBasicBlock)
    binaryFileData = {}
    with open(sys.argv[1], "rb") as executableFile:
        binaryFileData = executableFile.read()
    for basicBlock in BasicBlocks:
        basicBlock["hex"] = binascii.hexlify(
            binaryFileData[functionStart + basicBlock["offset"]:functionStart +
                           basicBlock["offset"] + basicBlock["size"]]).decode("UTF-8")
        basicBlock["asm"] = getAssembly(hexStringToSeparatedHexString(basicBlock["hex"]))
    return BasicBlocks

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 get_bbs.py <executable path> <function name>")
        sys.exit(1)
    
    ExecutablePath = sys.argv[1]
    FunctionName = sys.argv[2]

    BasicBlocks = getBasicBlocks(ExecutablePath, FunctionName)

    # remove textual asm for display
    for basicBlock in BasicBlocks:
        basicBlock.pop("asm")
    
    print(json.dumps(BasicBlocks, indent=4))
