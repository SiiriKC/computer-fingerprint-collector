#!/usr/bin/env python3
"""
Computer Fingerprint Collector
Author: Siiri
Date: 01.02.2025

This script collects system information (computer name, IP address, MAC address, etc.)
and appends it to a CSV file for tracking within Midtown IT.
"""

import os
import csv
import platform
import socket
import datetime
import subprocess
import json
import threading

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def getComputerName():
    """
    Returns the local computer name.
    """
    return socket.gethostname()

def getOsType():
    """
    Returns the operating system type (e.g., Windows, Linux, Darwin).
    """
    return platform.system()

def getProcessorModel():
    """
    Retrieves processor information.
    - Windows approach: platform.processor(), wmic, etc.
    - Linux/macOS approach: platform.processor() or /proc/cpuinfo
    """
    return platform.processor() or "Unknown Processor"

def getCurrentTime():
    """
    Returns current system time as a string.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getIpAddresses():
    """
    Returns a string of IP addresses found on the system,
    or 'Not Available' if none are found.

    Tries DNS-based lookup first; if that fails or is empty,
    uses a fallback method of connecting a dummy socket.
    """
    ipAddresses = []
    hostName = socket.gethostname()

    try:
        ipInfo = socket.gethostbyname_ex(hostName)
        ipAddresses = ipInfo[2]  # list of IPs
    except socket.gaierror:
        pass

    if not ipAddresses:
        try:
            # Attempt a temporary UDP connection to force OS to select an interface
            dummySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dummySocket.connect(("8.8.8.8", 80))
            fallbackIp = dummySocket.getsockname()[0]
            ipAddresses.append(fallbackIp)
            dummySocket.close()
        except Exception:
            pass

    if len(ipAddresses) == 0:
        return "Not Available"
    else:
        return ";".join(ipAddresses)

def getMacAddresses():
    """
    Returns a string of MAC addresses or 'Not Available'.

    1. If 'Darwin' (macOS) is detected, parse ifconfig output to find hardware addresses.
    2. Otherwise, fallback to socket.getnode() approach.

    For truly robust MAC detection, consider using a library like 'netifaces'.
    """
    currentOsType = getOsType().lower()

    # If on macOS, parse `ifconfig`
    if currentOsType == "darwin":
        try:
            ifconfigResult = subprocess.run(
                ["ifconfig"],
                capture_output=True,
                text=True
            )
            ifconfigOutput = ifconfigResult.stdout

            macList = []
            for line in ifconfigOutput.splitlines():
                if "ether " in line:
                    parts = line.strip().split()
                    if len(parts) == 2 and parts[0] == "ether":
                        macList.append(parts[1])

            if len(macList) > 0:
                return ";".join(macList)
            else:
                return "Not Available"

        except Exception:
            pass

    # Fallback for other platforms
    try:
        macNumber = socket.getnode()
        macString = ":".join(("%012X" % macNumber)[i:i+2] for i in range(0, 12, 2))
        return macString
    except Exception:
        return "Not Available"

def measureBasicConnectivity():
    """
    Attempts a simple ping to 8.8.8.8.
    Returns "Internet Up" if ping is successful, otherwise "Could Not Measure".
    """
    try:
        if platform.system().lower() == "windows":
            pingCommand = ["ping", "8.8.8.8", "-n", "1", "-w", "1000"]
        else:
            pingCommand = ["ping", "8.8.8.8", "-c", "1", "-W", "1"]

        pingResult = subprocess.run(pingCommand, capture_output=True, text=True)
        if pingResult.returncode == 0:
            return "Internet Up"
        else:
            return "Could Not Measure"
    except Exception:
        return "Could Not Measure"

def measureDetailedSpeed():
    """
    Measures internet speed by calling the speedtest-cli tool via subprocess.
    Returns a string with download, upload, and ping speeds.
    """
    try:
        # Run speedtest-cli with JSON output (depends on the installed version).
        # Make sure 'speedtest-cli' is installed via brew or pipx.
        speedTestResult = subprocess.run(
            ["speedtest-cli", "--json"],
            capture_output=True,
            text=True
        )
        if speedTestResult.returncode != 0:
            return "Could Not Measure (speedtest-cli error)"

        speedTestData = json.loads(speedTestResult.stdout)
        downloadMbps = speedTestData["download"] / 1_000_000
        uploadMbps = speedTestData["upload"] / 1_000_000
        pingMs = speedTestData["ping"]
        return f"{downloadMbps:.2f} Mbps Down / {uploadMbps:.2f} Mbps Up / {pingMs:.1f} ms Ping"
    except Exception as exceptionDetail:
        return f"Could Not Measure (Exception: {exceptionDetail})"

def isPortOpen(portNumber):
    """
    Checks if a given port is open on the localhost.
    Returns True if open, False otherwise.
    """
    testSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    testSocket.settimeout(0.5)

    try:
        testSocket.connect(("127.0.0.1", portNumber))
        testSocket.close()
        return True
    except:
        return False

def scanActivePorts(startPort=1, endPort=1024):
    """
    Scans ports in the given range on the local machine
    and returns a string listing open ports or 'None'.
    """
    activePorts = []

    for portNumber in range(startPort, endPort + 1):
        if isPortOpen(portNumber):
            activePorts.append(str(portNumber))

    if len(activePorts) == 0:
        return "None"
    else:
        return ";".join(activePorts)

def cleanData(dataString):
    """
    Cleans a data string to avoid CSV issues (e.g., removing commas).
    """
    return dataString.replace(",", ";")

# -----------------------------------------------------------------------------
# Additional function to force open a port
# -----------------------------------------------------------------------------

def startDummyServer(port=8080):
    """
    Opens a simple server socket on the given port for demonstration,
    so there is guaranteed to be an open port for scanning.
    """
    def runDummyServer():
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(("0.0.0.0", port))
        serverSocket.listen(5)
        print(f"Dummy server is listening on port {port}...")

        while True:
            clientConnection, clientAddress = serverSocket.accept()
            receivedData = clientConnection.recv(1024)
            # Send a simple HTTP response (or any data you like)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Content-Length: 24\r\n\r\n"
                "Hello from dummy server!\n"
            )
            clientConnection.sendall(response.encode("utf-8"))
            clientConnection.close()

    # Run the server in a separate thread (daemon=True means auto-kill on main exit)
    thread = threading.Thread(target=runDummyServer, daemon=True)
    thread.start()

# -----------------------------------------------------------------------------
# Main entry point
# -----------------------------------------------------------------------------

def main():
    """
    Main function that collects system information
    and writes (appends) it to a CSV file.
    """
    # Start a dummy server on port 8080 so we know there's an open port
    startDummyServer(8080)

    # Collect data
    computerName = cleanData(getComputerName())
    osType = cleanData(getOsType())
    processorModel = cleanData(getProcessorModel())
    currentTime = getCurrentTime()
    ipAddresses = cleanData(getIpAddresses())
    macAddresses = cleanData(getMacAddresses())

    # Measure basic connectivity (ping)
    basicConnectivity = measureBasicConnectivity()

    # Measure actual speeds (speedtest-cli)
    detailedSpeed = measureDetailedSpeed()

    # Give the dummy server a moment to initialize (optional small sleep)
    # import time; time.sleep(1)

    # Scan for open ports (1 - 9000). We know 8080 should appear now.
    activePorts = scanActivePorts(startPort=1, endPort=9000)

    # Print to console for verification
    print("Computer Name:", computerName)
    print("OS Type:", osType)
    print("Processor Model:", processorModel)
    print("Current Time:", currentTime)
    print("IP Addresses:", ipAddresses)
    print("MAC Addresses:", macAddresses)
    print("Basic Connectivity:", basicConnectivity)
    print("Detailed Speed:", detailedSpeed)
    print("Open Ports:", activePorts)

    # Append data to a CSV file
    csvFileName = "fingerprint_data.csv"
    dataRow = [
        computerName,
        osType,
        processorModel,
        currentTime,
        ipAddresses,
        macAddresses,
        basicConnectivity,
        detailedSpeed,
        activePorts
    ]

    with open(csvFileName, "a", newline="") as fileHandle:
        writer = csv.writer(fileHandle)
        writer.writerow(dataRow)

    print(f"\nData collected and appended to '{csvFileName}'.\n")

if __name__ == "__main__":
    main()
