
import recorder
import datetime
import time
from bottle import route, request, run, get
import socket
import logging.config
import os
import json
import threading
from subprocess import PIPE, Popen
import psutil
import fcntl
import struct
import requests
from subprocess import call
import subprocess

recFile = None
recordingStatus = None

def setup_logging(default_path, default_level, env_key):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        
logger = logging.getLogger(__name__)
setup_logging('/home/pi/logging.json', logging.INFO, 'LOG_CFG')


@route('/test/')
def test():
    result = None
    try:
        logger.info("test()> Request received")
        today_time = datetime.datetime.now()
        b = today_time + datetime.timedelta(seconds=3)

        logger.info("test()> today_time= " + str(today_time))
        logger.info("test()> b= " + str(b))
        today_time_3s = datetime.datetime(today_time.year, today_time.month, today_time.day,today_time.hour, today_time.minute, today_time.second +3, 0)
        logger.info("test()> today_time= " + str(today_time_3s))
        while True:
            if(datetime.datetime.now().second == today_time_3s.second):
                logger.info("test()> after 3 sec")
                break

        result = "Success"
    except Exception, e:
        result = "Failure"
        logger.error("test()>", exc_info = True)
    finally:        
        return result

# Non-blocking mode (start and stop recording):
@route('/startRecording/<wavFileName>,<channels>,<rate>,<frames_per_buffer>,<customername>,<customernumber>,<customersWRDnumber>,<SMname>,<SMid>,<SMWRDnumber>')
def startRecording(wavFileName, channels, rate, frames_per_buffer,customername, customernumber, customersWRDnumber, SMname, SMid, SMWRDnumber):
    result = None
    try:
        global recFile        
        global recordingStatus
        logger.info("startRecording()> I/P: wavFileName= " + str(wavFileName) + " , channels= " + str(channels) + " , rate= " + str(rate) + "frames_per_buffer= " + str(frames_per_buffer))
        logger.info("startRecording()> I/P: customername= " + str(customername) + " , customernumber= " + str(customernumber) + " , customersWRDnumber= " + str(customersWRDnumber) + "SMname= " + str(SMname) + " , SMid= " + str(SMid) + " , SMWRDnumber= " + str(SMWRDnumber))
        
        logger.info("startRecording()> Current recording status= "+ str(recordingStatus))

        if(recordingStatus == "started"):
            logger.info("startRecording()> Since current recording  is still not stopped, unable to start new recording")
            result = "Failure"
        else:
            logger.info("startRecording()> Since current recording  is stopped, starting new recording")
            rec = recorder.Recorder(int(channels), int(rate), int(frames_per_buffer))
            recFile = rec.open("/home/pi/RecordedFiles/" + wavFileName, 'wb')
            
            recFile.start_recording()
            logger.info("startRecording()> recording started")
            result = "Success"
            recordingStatus = "started"
    except Exception, e:
        result = "Failure"
        logger.error("startRecording()>", exc_info = True)    
    finally:        
        return result

@route('/stopRecording/<customername>,<customernumber>,<customersWRDnumber>,<SMname>,<SMid>,<SMWRDnumber>')
def stopRecording(customername, customernumber, customersWRDnumber, SMname, SMid, SMWRDnumber):
    result = None
    try:
        global recFile
        global recordingStatus

        logger.info("stopRecording()> customername= " + str(customername) + " , customernumber= " + str(customernumber) + " , customersWRDnumber= " + str(customersWRDnumber) + "SMname= " + str(SMname) + " , SMid= " + str(SMid) + " , SMWRDnumber= " + str(SMWRDnumber))

        logger.info("stopRecording()> Current recording status= "+ str(recordingStatus))

        if(recordingStatus == "started"):
            logger.info("stopRecording()> Stopping the current recording")
            recFile.stop_recording()
            recFile.close()
            logger.info("stopRecording()> recording stopped")
            result = "Success"
            recordingStatus = "stopped"
        else:
            logger.info("stopRecording()> There is no recording going on to stop")
            result = "Failure"
    except Exception, e:
        result = "Failure"
        logger.error("stopRecording()>", exc_info = True)
    finally:        
        return result

@route('/shutdown/')
def shutdown():
    result = None
    try:
        logger.info("shutdown()> As per user request executing shutdown command>> sudo shutdown -h +1")
        call("sudo shutdown -h +1", shell=True)
        result = "Success"
    except Exception, e:
        result = "Failure"
        logger.error("shutdown()>", exc_info = True)
    finally:        
        return result

def get_cpu_temperature():
    try:
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        return float(output[output.index('=') + 1:output.rindex("'")])
    except Exception, e:
        logger.error("get_cpu_temperature()>", exc_info = True)

def insertPiStats():
    try:
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()      
        cpu_temperature = float(output[output.index('=') + 1:output.rindex("'")])
        logger.info("insertPiStats()> cpu_temperature= " + str(cpu_temperature) + " C")

        cpu_usage = psutil.cpu_percent()
        logger.info("insertPiStats()> cpu_usage= " + str(cpu_usage) + "%")

        ram = psutil.virtual_memory()
        ram_total = ram.total / 2**20 # MiB.
        ram_used = ram.used / 2**20
        ram_free = ram.available / 2**20
        ram_percent_used = ram.percent    
        logger.info("insertPiStats()> ram_total= " + str(round(ram_total)) + " MB, ram_used= " + str(round(ram_used)) + " MB, ram_free= " + str(round(ram_free)) + " MB, ram_percent_used= " + str(ram_percent_used) + " %")
        
        disk = psutil.disk_usage('/')
        disk_total = disk.total / 2**30     # GiB.
        disk_used = disk.used / 2**30
        disk_free = disk.free / 2**30
        disk_percent_used = disk.percent
        logger.info("insertPiStats()> disk_total= " + str(round(disk_total)) + ", disk_used= " + str(round(disk_used)) + ", disk_percent_used= " + str(disk_percent_used)+ " %")
        logger.info("insertPiStats()> Calling POST API to update the details in DB")
        data =  { 'hostname': socket.gethostname(),
                  'cputemp' : cpu_temperature,
                  'cpuused': cpu_usage,
                  'diskused': disk_percent_used,
                  'ramused': ram_percent_used}
        piStatsPostRequest("pistats", data)
    except Exception, e:
        logger.error("insertPiStats()>", exc_info = True)

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def updateIpHostname():
    try:
        ip = get_ip_address('wlan0')
        hostname= socket.gethostname()
        logger.info("updateIpHostname()> ip= " + str(ip) + " , hostname =" + hostname)
        logger.info("updateIpHostname()> Calling POST API to update the details in DB")

        currentssid= subprocess.check_output(['sudo', 'iwgetid']).split('"')[1]
        logger.info("updateIpHostname()> currentssid= "+ currentssid) 

        if(currentssid == "Nandanvan"):
            apiEndPoint = "http://192.168.1.7:4000/api/wrd/" +hostname+ "/ip/" + ip  
        else:
            if (currentssid == "OnePlus3"):
                apiEndPoint = "http://192.168.43.80:4000/api/wrd/" +hostname+ "/ip/" + ip
            else:
                apiEndPoint = "http://172.29.10.31:4000/api/wrd/" +hostname+ "/ip/" + ip       

        logger.info("updateIpHostname()> apiEndPoint= "+ apiEndPoint)
        # sending post request and saving response as response object
        r = requests.post(url = apiEndPoint)
        # extracting response text 
        responseText = r.text
        logger.info("updateIpHostname()> responseText= "+ responseText)

    except Exception, e:
        logger.error("updateIpHostname()>", exc_info = True)

def startBottleServer():
    try:
        logger.info("startBottleServer()> **** START ****")
        logger.info("startBottleServer()> bottle web server started and listeing on port 8080")
        run(host = '0.0.0.0', port = '8080')
    except Exception, e:
        logger.error("startBottleServer()>", exc_info = True)

thread_ws=threading.Thread(target=startBottleServer,args=())
thread_ws.daemon = True
thread_ws.start()
#A daemon thread will stop whenever the main thread that it is running in is killed or dies.

def piStatsPostRequest(method, data):
    try:
        logger.info("piStatsPostRequest()> I/P method= "+ method + " , data= "+ str(data))
        apiEndPoint = "http://172.29.10.31:4000/api/" + method        

        logger.info("piStatsPostRequest()> apiEndPoint= "+ apiEndPoint)
        # sending post request and saving response as response object
        r = requests.post(url = apiEndPoint, data = data)
        # extracting response text 
        responseText = r.text
        logger.info("piStatsPostRequest()> responseText= "+ responseText)
    except Exception, e:
        logger.error("piStatsPostRequest()>", exc_info = True)

# Main thread
try:
    logger.info("Main()> Wait for 10 seconds, for RPI to get the IP address")
    time.sleep(10)
    updateIpHostname()
    while True:   
        time.sleep(3600)
        insertPiStats()
    # End program cleanly with keyboard or sys.exit(0)
except KeyboardInterrupt:
    logger.info("Main()> Quit (Ctrl+C)")
except SystemExit:
    logger.info("Main()> Quit (SIGTERM)")

logger.info("Main()> **** END ****\n")
