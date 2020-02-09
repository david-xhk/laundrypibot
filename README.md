# LaundryPiBot

## Setup
To operate LaundryPiBot, there are three separate modules that need to be 
started: laundrypisensor.py, laundrypibot.py, and laundrypiapp.py.

### Install dependencies
Before running anything, we need to make sure that certain dependencies are 
installed. We assume everything hereon is running in Python 3.

    pip3 install python-telegram-bot
    pip3 install pyrebase
    
### Install Kivy
To install Kivy, we simply follow what Kivy recommends for installation for 
development purposes:

    git clone https://github.com/kivy/kivy
    cd kivy
    
    make
    echo "export PYTHONPATH=$(pwd):\$PYTHONPATH" >> ~/.profile
    source ~/.profile

## Demonstration
Navigate to the directory containing laundrypibot. For demonstration purposes, 
run the following to help set up the database first. This is for the case when
there is one idle washer, and there are some washers that are running and some 
that are faulty.

    cd laundrypibot
    python3 laundrypidemo.py 1

### Hooking Up the Sensor
Now, ensuring that the Raspberry Pi (RPi) is hooked up to a vibration sensor, 
activate the sensor module by running:

    python3 laundrypisensor.py

### Starting the Telegram Chat Bot
Information about washer states should start printing to the terminal screen.
Shaking the vibration sensor should register changes.
Next, run the module for the Telegram chat bot in a new terminal:

    python3 laundrypibot.py

The bot is now live. It should be able to respond to user interactions such as
/washers, /notify, and /report. /washers should report that there are four
washers: washer 1 is idle, washer 2 and 3 are running for about 20 and 12 
minutes respectively, and washer 4 is faulty; and /notify should inform you 
that washer 1 is currently idle.

### Starting the Kivy App
Lastly, run the module for the Kivy app in a new terminal:

    python3 laundrypiapp.py

This should fire up the Kivy app on the RPi display, which should be able to
accept user input immediately.

Bear in mind that there is a bug where interacting with the Kivy app on RPi 
display sends touch events through to the background of the RPi, where the 
terminals are probably still visible. There might be a chance that a touch 
event accidentally closes one of the terminals if the touch happens to be at 
the exit button of the terminal. To avoid this, move the terminals to the 
corners of the screen so that any exit button is out of reach of possible 
touches.

### Another Demonstration
To see the case when there are no idle washers, but only washers that are 
running with some that are faulty, run the following to set up the database 
one more time.

    python3 laundrypidemo.py 2

In the terminal running laundrypisensor.py, kill the execution and rerun the 
module once again in order to synchronise it with the newly updated database.

    *Execution interrupted with ctrl+c*
    python3 laundrypisensor.py

Now, running /washers on the Telegram chat bot should report that there are 
four washers: washer 1, 2, and 3 are running for about 27, 20, and 12 minutes 
respectively, while washer 4 is still faulty. /notify should inform you that
washer 1 has been running for 27 minutes, and you will be notified when it 
has stopped running.
