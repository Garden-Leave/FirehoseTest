# FirehoseTest
This repository provides an example of how to use the Cisco DNA Spaces Firehose API stream to extract useful information.

The scripts are written for Python3 
We will collect and save the following events:
1.	Temperature in Celsius from an IoT Sensor with mac address e2:66:43:1b:cc:07
2.	Air pressure from an IoT Sensor with mac address cd:c5:34:a6:92:e6
3.	CO2 Parts per million for Air Quality from an IoT Sensor with mac address 68:27:19:3b:cd:4a
4.	Humidity from an IoT Sensor with mac address cd:c5:34:a6:92:e6
5.	Battery percent value from an IoT Sensor with mac address f8:20:d5:9d:91:ad
The API Key used for this script is generated and acquired by creating an Application in the Partner Dashboard as explained in this guide.

This script can be used as a reference and an example. Please change the API key and the device and / or event details as needed for your account.
Every customer would have different types of devices and some may not even have BLE sensors in the account. You should pick the event types that you are interested in and are available in your account and use those in your own use case.


Dependencies:
The following python modules are used in the scripts.
•	requests
•	json
•	socket
•	flask
Please install requests and flask modules for python3 by running the commands ‘pip install requests’ and ‘pip install flask’

To run, copy the code and make needed changes for your DNA Spaces account.

Run the testWebserver.py file first, followed by the testStream.py file in a separate terminal window.

To launch the UI, open a web browser and navigate to the URL mentioned in the output of the testWebserver.py file. It would be your local IP on port 80.
As details like temperature, pressure, humidity etc. gets collected, the table would be updated. Until the information is available, the output would show as unknown.
