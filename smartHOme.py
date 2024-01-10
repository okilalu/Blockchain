import random
import time

# Define the initial state of the smart home
lights_on = False
temperature = 20.0
humidity = 50.0
motion_detected = False

# Simulate a day in the smart home
for hour in range(24):
    # Simulate sensor data
    temperature += random.uniform(-1.0, 1.0)
    humidity += random.uniform(-5.0, 5.0)
    motion_detected = random.choice([True, False])

    # Simulate the smart home's response to the sensor data
    if hour >= 6 and hour < 8:
        # Turn on the lights in the morning
        lights_on = True
    elif hour >= 18 and hour < 22:
        # Turn on the lights in the evening
        lights_on = True
    else:
        # Turn off the lights at night
        lights_on = False

    if motion_detected:
        # Increase the temperature and humidity when motion is detected
        temperature += 1.0
        humidity += 10.0

    # Print the current state of the smart home
    print("Time: {:02d}:00, Lights: {}, Temperature: {:.1f}C, Humidity: {:.1f}%, Motion Detected: {}".format(
        hour, "On" if lights_on else "Off", temperature, humidity, motion_detected))

    # Wait for 1 second to represent the passage of time
    time.sleep(1)
