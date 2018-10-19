# Wearable-Recording-Device (WRD)
Smart wearable recording device with 10 hours of battery life to record CD quality audio.

# Architecture
<img src="images/Architecture.png" width="500">

# Design Details
1. WRD dimensions: 88x127x8mm. Same as medium size ID card. Since electronic component and battery max thickness is 5mm, overall thickness can be reduced to 7mm!!
2. WRD consists of microcomputer, power management circuit and LIPO battery.
3. Each WRD will record mono high quality audio (channels=1, rate=44100, frames_per_buffer=1024) in wav fomrat.
4. Using 'Recording Admin' user can start and stop the recording
5. 'Record Admin' (RA) in node.js application running on web server. It will communicate with the WRD's on port 8080 to start/stop the recordings. And at the end of recording copy the recorded files to server.Wav file will be converted to mp3(alomost 10 fold size reduction). Mono file from customer and sales manager will be mergered together to create stereo combined mp3 file. Each mono and combined stereo file will be uploaed to Amazon S3.  RA will also update the Saleforce CRM with recording id against the customer and sales manager.
6. Saleforce CRM will be integrated with Amazon Streaming services to listen to the recorded files(available on S3)
7. Speachh Analytics: As per customer requirements rules can be set for analytics using mono as wel as stereo files.
8. SMS Gateway: On recording start and end, SMS will be sent to the customer 

# Record Admin
<img src="images/Record Admin.png" width="500">