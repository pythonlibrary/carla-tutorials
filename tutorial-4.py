import copy
import random

import carla
import cv2
import numpy as np
from carla import ColorConverter as cc

import time


client = carla.Client("localhost", 2000)
client.set_timeout(10.0)

# get world
world = client.load_world('Town02')
#world = client.get_world()
weather = carla.WeatherParameters(
    cloudiness=0.0,
    precipitation=0.0,
    sun_altitude_angle=50.0)

world.set_weather(weather)

picked_spawn_points = []

# get vehicle blueprint
model3_bp = world.get_blueprint_library().find('vehicle.tesla.model3')
model3_bp.set_attribute('color', '255,255,255')

camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', str(1028))
camera_bp.set_attribute('image_size_y', str(720))

# get avaliable spawn points 
spawn_points = world.get_map().get_spawn_points()
random.shuffle(spawn_points)

# spawn vehicle
model3_spawn_point = spawn_points[-1]
model3 = world.spawn_actor(model3_bp, model3_spawn_point)
picked_spawn_points.append(model3_spawn_point) 

NUMBER_OF_VEHICLES = 10

vehicle_bps = world.get_blueprint_library().filter('vehicle.*.*')

vehicle_bps = [x for x in vehicle_bps if int(x.get_attribute('number_of_wheels')) == 4]

vehicle_list = []

for i in range(NUMBER_OF_VEHICLES):
    point = spawn_points[i]
    vehicle_bp = np.random.choice(vehicle_bps)
    try:
        vehicle = world.spawn_actor(vehicle_bp, point)
        picked_spawn_points.append(point)
        vehicle_list.append(vehicle)
    except:
        print('failed')
        pass

tm = client.get_trafficmanager()
tm.global_percentage_speed_difference(30.0)

tm_port = tm.get_port()
for v in vehicle_list:
    v.set_autopilot(True, tm_port)
    tm.ignore_lights_percentage(v,100)
    tm.distance_to_leading_vehicle(v,0)
    tm.vehicle_percentage_speed_difference(v,-20)

model3.set_autopilot(True)

# spawn camera
camera = world.spawn_actor(camera_bp, 
                           carla.Transform(carla.Location(x=-5.5, z=2.5), carla.Rotation(pitch=8.0)), 
                           model3,
                           carla.AttachmentType.SpringArm
                           )
camera.listen(lambda image:parse_image(image)) #image.save_to_disk('output/%06d.png' % image.frame))


Image_Array = None
Cars = None

Car_Cascade = cv2.CascadeClassifier('cars.xml')

def parse_image(image):
    global Image_Array
    global Car_Cascade
    global Cars
    # image.raw_data is a memoryview type: https://docs.python.org/3/c-api/memoryview.html
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array_gray = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    Cars = Car_Cascade.detectMultiScale(array_gray, 1.3, 5)

    Image_Array = array 
    # array = array[:, :, ::-1]

while True:
    if Image_Array is not None:
        image = copy.copy(Image_Array)
        if Cars is not None:
            for (x,y,w,h) in Cars:
                cv2.rectangle(image,(int(x),int(y)),(int(x+w),int(y+h)),(255,0,0), 2)
        cv2.imshow('Carla Tutorial', image )
    if cv2.waitKey(25) & 0xFF == ord('q'):
        # destroy cv2 window when 'q' is pressed
        cv2.destroyAllWindows()
        break