## Introduction

This system was developed for a startup working on smart flower pots. It offers an all-in-one solution to monitor and manage various environmental parameters such as light, temperature, and soil moisture in real time. The focus is on creating an interactive and intelligent system for flower pots that can send notifications, control LEDs, adjust servo states, provide visual feedback on an OLED screen, and much more, based on sensor readings and user preferences.

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Usage](#usage)
6. [API Description](#api-description)

## Features

- **Sensor Management**: Handles readings from LDR, temperature, and soil moisture sensors.
- **Bluetooth Communication**: Sends commands and receives sensor data via BLE.
- **Servo and LED Control**: Dynamically controls servo states and RGB LEDs.
- **Visual Feedback**: Displays happy/sad faces on an OLED screen based on conditions.
- **Threaded Execution**: Runs multiple concurrent threads for seamless operation.
- **Exception Handling**: Robust error handling for ease of debugging.
- **Flexible API**: Provides an API for interaction, including calibration and custom actions.

## Prerequisites

- MicroPython-compatible microcontroller
- Supported sensors (LDR, temperature, soil moisture)
- OLED display
- RGB LED, Servo motor
- BLE support

## Installation

Below is the list of modules used in this project and their corresponding pin connections:

- **Light Dependent Resistor (LDR)**: Pin X
- **Temperature Sensor (DHT22)**: Pin Y
- **Soil Moisture Sensor**: Pin Z
- **OLED Display**: Pin A, Pin B
- **RGB LED**: Pin C, Pin D, Pin E
- **Servo Motor**: Pin F
- **Bluetooth Low Energy (BLE)**: Pin G, Pin H
- **Water Pump**: Pin I


## Usage

1. **Connect the Modules**: Connect all the modules to their corresponding pins as described in the Modules and Pins section. Ensure proper connections and consult the hardware documentation if needed.
2. **Place Sensors in Soil**: Place the temperature and soil moisture sensors into the soil in the planter or pot.
3. **Upload the Code**: Transfer the MicroPython code to your microcontroller.
4. **Run the Code**: Execute the code on the microcontroller.
5. **BLE Mobile App**: Use a mobile app to send functions over Bluetooth (as there are many applications on mobile app stores.)
6. **Water Pump Caution**: Do not connect the water pump until the system is fully ready and calibrated to avoid any unexpected behavior.
7. **Enjoy Your Smart Flower Pot**: Monitor and manage your smart flower pot through the app and watch as it takes care of your plants.

## API Description

The system accepts various JSON commands to control and monitor the smart flower pots. Below is a detailed explanation of each command:

### Calibration Command (`"c"`)

- **JSON**: `{"command":"c"}`
- **Description**: This command is used to start the calibration mode for the sensors. Calibration ensures accurate readings and optimal functioning of the smart flower pot.

### Set Required Light and Moisture (`"r"`)

- **JSON**: `{"command":"r", "reqLight":"80", "reqMoist":"70"}`
- **Description**: This command sets the required light and moisture levels to make the face on the OLED display happy. If these requirements are not met, the display will show a sad face.
  - `reqLight`: The required light percentage.
  - `reqMoist`: The required soil moisture percentage.

### Value Condition Command (`"v"`)

- **JSON Example for Light**: 
	`{"command":"v", "type":"light", "min":"50", "max":"60", "action":"notification", "param":"An example notification"}`
- **JSON Example for Moisture**:
	`{"command":"v", "type":"moist", "min":"50", "max":"60", "action":"led", "param":"255,255,255"}`
	- **Description**: This command sets the software to perform specific actions (e.g., sending notifications or lighting an LED) based on the given sensor values (light, moisture, temperature).
		- **type**: The type of value to monitor (e.g., "light", "moist").
		- **min**: The minimum value of the range.
		- **max**: The maximum value of the range.
		- **action**: The task to perform when the value is within the specified range. It can be "notification" for sending a message or "led" for controlling the LED.
		- **param**: Parameters related to the action. For LED, it's the color, and for notifications, it's the message content.
### Get Values Command (`"get"`)
- **JSON**: `{"command":"get", "type":"LDR/Moist/Temp/SoilTemp"}`
- **Description**: This command retrieves the specified values (light, moisture, temperature) asynchronously.
	- type: The type of value to get. Can be "LDR", "Moist", "Temp", "SoilTemp".
	
These commands enable you to interact with and control the smart flower pot system through the recommended mobile app via Bluetooth, providing you with a seamless and user-friendly experience.