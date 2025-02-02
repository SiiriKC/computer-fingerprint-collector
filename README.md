# Computer Fingerprint Collector

**Author:** Your Name  
**Date:** YYYY-MM-DD  

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Usage](#usage)  
6. [Output](#output)  
7. [Configuration Options](#configuration-options)  
8. [Contributing](#contributing)  
9. [License](#license)  
10. [Contact / Support](#contact--support)

---

## Project Overview
This Python script collects hardware and network information from a local computer, such as:
- Hostname
- OS type
- CPU details
- IP addresses
- MAC addresses
- Basic connectivity check
- Internet speed measurements
- Open port scanning (with a dummy server on port 8080)

Data is appended to a CSV file, allowing Midtown IT to maintain a simple record of machine fingerprints.

## Features
- **Automatic Data Collection**: Gathers system info without user intervention.
- **Network Checks**: Pings `8.8.8.8` to verify connectivity.
- **Speed Test**: Uses `speedtest-cli` to measure bandwidth.
- **Open Port Scan**: Scans ports `1-9000` and displays any that are open.
- **Dummy Server**: Automatically starts a server on port `8080` to ensure at least one open port is detected.

## Prerequisites
1. **Python 3.7+** (Python 3.9 recommended).
2. **speedtest-cli** installed via:
   ```bash
   pip install speedtest-cli
   ```
3. Internet access for running ping and speed tests.
## Installation
1. Clone this repository (or download the ZIP):
```bash
git clone https://github.com/SiiriKC/computer-fingerprint-collector.git
``` 
2. Change directory:
```bash
cd computer-fingerprint-collector
```
3. Install dependencies:
```bash
brew install speedtest-cli
```
## Usage
Run the script using:

```bash
python3 getComputerData.py
```
The script will:

1. Display system information in the terminal.
2. Append a row of data into fingerprint_data.csv in the same directory.
### Sample Output:

```
Computer Name: MyComputer
OS Type: Darwin
Processor Model: ...
Current Time: 2025-02-02 12:34:56
IP Addresses: 192.168.1.10;10.0.0.5
MAC Addresses: 00:1A:2B:3C:4D:5E
Basic Connectivity: Internet Up
Detailed Speed: 50.00 Mbps Down / 10.00 Mbps Up / 20.0 ms Ping
Open Ports: 8080
```
## Output
A CSV file named fingerprint_data.csv is created or appended to with each run.
### Sample CSV row:
```
MacBook-Pro.local,Darwin,arm,2025-02-02 20:15:00,127.0.0.1;192.168.20.37,52:bb:cc:c1:28:fc;52:bb:cc:c1:28:fb;52:bb:cc:c1:28:db;52:bb:cc:c1:28:dc;36:f0:22:cd:df:c0;36:f0:22:cd:df:c4;36:f0:22:cd:df:c0;ea:eb:49:ef:4a:c5;be:e1:b8:45:6d:cd;96:f8:61:15:85:60;96:f8:61:15:85:60,Internet Up,102.47 Mbps Down / 14.84 Mbps Up / 21.8 ms Ping,5000;6463;7000;8080

```
## Configuration Options
* Port Scanning Range: Modify startPort and endPort in scanActivePorts if you want a different range.
* Dummy Server: Adjust or remove the call to startDummyServer(8080) in main() if you do not need to ensure an open port.
* Ping Settings: Tweak the command in measureBasicConnectivity() if you need a different host or additional flags.