# MTE380

## System Requirements:  
Python3  


## Dependencies:  
See requirements.txt  
pip install requirements.txt  


## Running Simulation:  
python main.py  

## Running People Localization:  
python image_processing/objectDetector.py -m "MobileNetSSD_deploy.caffemodel" -p "MobileNetSSD_deploy.prototxt" -i input_videos\2.mp4 -o output_videos\2.mp4  

To turn on time measurement:  
python image_processing/objectDetector.py -m "MobileNetSSD_deploy.caffemodel" -p "MobileNetSSD_deploy.prototxt" -i input_videos\2.mp4 -o output_videos\2.mp4 -t  

To turn on grid drawing (slow and inefficient, only for showing):  
(Note that for now this only works for input_videos\2.mp4)
python image_processing/objectDetector.py -m "MobileNetSSD_deploy.caffemodel" -p "MobileNetSSD_deploy.prototxt" -i input_videos\2.mp4 -o output_videos\2.mp4 -g  