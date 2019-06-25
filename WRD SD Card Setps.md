## Table of Contents
- Raspbian Setup
- Development Setup
- USB Mic configuration
- I2S Mic configuration
- Using pyaudio
- Uisng Bottle: Python Web Framework
- Pi Stats
- Samba File Server
- Python GET/POST Rest Requests
- Python Script "record.py"


- Installing Adafruit DHT Library

- Using 8 channel relay with external power supply
- Using Adafruit PiRTC - PCF8523 Real Time Clock for Raspberry Pi
- Using UPS

## Raspbian Setup
- Installed Raspbian Strech Lite on 32 Gb SD Card. Followed Raspberry pi installation guide.       https://www.raspberrypi.org/documentation/installation/installing-images/README.md
- Configure SD Card for wifi connection and enabled SSH. https://core-electronics.com.au/tutorials/raspberry-pi-zerow-headless-wifi-setup.html
wpa_supplicant.conf file content:
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=IN

    network={
            ssid="Nandanvan"
            psk="********"
            key_mgmt=WPA-PSK
    }

    network={
            ssid="OnePlus3"
            psk="*******"
            key_mgmt=WPA-PSK
    }
```
- Note: After login, Can use command "sudo nano /etc/wpa_supplicant/wpa_supplicant.conf" to edit/update ssid’s
- Using command 'sudo raspi-config' update country, localisation, hostname, password, expand fileset.
- Interfacing Options" / "Pi Serial". It is then necessary to answer as follows:
       ```
   		 "Would you like a login shell to be accessible over serial?" - No
   		 "Would you like the serial port hardware to be enabled?" - Yes
       ```
- Reboot pi

## Development Setup
- Then Run below command
```
  sudo apt-get update
  sudo apt-get upgrade
  sudo apt-get install python-dev
  sudo apt-get install python-setuptools
  sudo easy_install rpi.gpio
```

## USB Mic configuration
- If using USB microphone then follow Adafruit doc for USB Mic configuration. https://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/figure-out-your-chipset

## I2S MEMS Mic configuration
- If using I2S MEMS microphone then follow Adafruit doc for Adafruit I2S Mic configuration. https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout?view=all

## Using pyaudio
- install pyaudio using below commands
```
sudo apt-get install git
sudo git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
cd pyaudio
sudo python setup.py install
```
- Now you can record audio using python program
- For USB mic use below details in python script
```
channels=1, rate=44100, frames_per_buffer=1024
"format=pyaudio.paInt16" in start_recording() funaction  and "pyaudio.paInt16" in _prepare_file() function
```
- For Adafruit I2S mic use below details in python script
```
channels=1, rate=48000, frames_per_buffer=2400
"format=pyaudio.paInt32" in start_recording() function and "pyaudio.paInt32" in _prepare_file() function
```
## Uisng Bottle: Python Web Framework
- Use 'sudo apt-get install python-bottle' command to install 
- In python script let server listen to all interfaces at once (e.g. run(host='0.0.0.0'))
  ref. https://electronut.in/talking-to-a-raspberry-pi-from-your-phone-using-bottle-python/
  
## Pi Stats
- Install psutil using below commands
```
sudo apt-get install python-pip python-dev
sudo pip install psutil
```
- Ref. https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=22180

## Samba File Server
- In order to share the files from RPI we willbe using Samba file server
- Install Samba using below commands
```
sudo apt-get install samba samba-common-bin
sudo mkdir -m 1777 /home/pi/RecordedFiles
```
- Edit Samba’s config files to make the file share visible to the Windows PCs on the network.
```
sudo nano /etc/samba/smb.conf
add below lines at the end of file
   
   [RecordedFiles]
    Comment = Pi shared folder
    Path = /home/pi/RecordedFiles
    Browseable = yes
    Writeable = Yes
    only guest = no
    create mask = 0777
    directory mask = 0777
    Public = yes
    Guest ok = yes
```
- Set new sambs password using below command. This will add the user pi to the list of Samba users and pi
```
    sudo smbpasswd -a pi
    #new password: samba
```
- Now restart the Samba. sudo /etc/init.d/samba restart
- Now try to access RPI file from PC. Shared folder path will be @"\\<ip address>\RecordedFiles\filename.wav"
- Samba Server Installation ref.  https://www.raspberrypi.org/magpi/samba-file-server/
    
## Python GET/POST Rest Requests
- Install 'requests' using command. sudo pip install requests
 
## Python Script "record.py"
- Please refer 'src' folder for source code.
- To run 'recod.py' as service. ref. http://www.diegoacuna.me/how-to-run-a-script-as-a-service-in-raspberry-pi-raspbian-jessie/
- Define the service to run this script:
```
cd /lib/systemd/system/
sudo nano record.service
```
- The service definition must be on the /lib/systemd/system folder. Our service is going to be called "record.service":
```
   	[Unit]
	Description=Recording Service
	After=multi-user.target
 
	[Service]
	Type=simple
	ExecStart=/usr/bin/python /home/pi/record.py
	Restart=on-abort
 
	[Install]
	WantedBy=multi-user.target
```
- Now that we have our service we need to activate it
```
sudo chmod 644 /lib/systemd/system/record.service
chmod +x /home/pi/record.py
sudo systemctl daemon-reload
sudo systemctl enable record.service
sudo systemctl start record.service
```
- For every change that we do on the /lib/systemd/system folder we need to execute a 'daemon-reload'. If we want to check the status of our service, you can execute: 'sudo systemctl status record.service'
- In general:
```
# Check status
sudo systemctl status record.service
 
# Start service
sudo systemctl start record.service
 
# Stop service
sudo systemctl stop record.service
 
# Check service's log
sudo journalctl -f -u record.service
```


