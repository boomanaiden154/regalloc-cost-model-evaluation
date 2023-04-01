import subprocess
import sys
import binascii

def getThroughputFromHex(inputHex):
    uiCACommandVector = ["python3", "/uiCA/uiCA.py", "-hex", inputHex, '-arch',
                         'SNB']
    with subprocess.Popen(uiCACommandVector, stdout=subprocess.PIPE) as uiCAProcess:
        out, err = uiCAProcess.communicate()
        allLines = out.decode("UTF-8").split('\n')
        throughput = float(allLines[0].split(': ')[1])
        return throughput

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 process_bbs.py <hex string>")
        sys.exit(1)
    
    hexString = sys.argv[1]
    throughput = getThroughputFromHex(hexString)

    print(throughput)
