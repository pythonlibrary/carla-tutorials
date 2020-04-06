import carla
from carla import ColorConverter as cc
import numpy as np
import time

running = True


# Create client and connected to the server
client = carla.Client("localhost", 2000)
client.set_timeout(10.0)

# get world
world = client.load_world('Town02')
weather = carla.WeatherParameters(
    cloudiness=0.0,
    precipitation=0.0,
    sun_altitude_angle=50.0)
world.set_weather(weather)

# get vehicle blueprint
model3_bp = world.get_blueprint_library().find('vehicle.tesla.model3')
model3_bp.set_attribute('color', '255,255,255')

camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')

# spawn vehicle(Actor)
spawn_points = world.get_map().get_spawn_points()
model3_spawn_point = np.random.choice(spawn_points)
model3 = world.spawn_actor(model3_bp, model3_spawn_point)
model3.set_autopilot(True)


# spawn camera
camera = world.spawn_actor(camera_bp, 
                           carla.Transform(carla.Location(x=-5.5, z=2.5), carla.Rotation(pitch=8.0)), 
                           model3,
                           carla.AttachmentType.SpringArm
                           )
camera.listen(lambda image:image.save_to_disk('output/%06d.png' % image.frame))




while running:
    spectator = world.get_spectator()
    transform = model3.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(z=50),
    carla.Rotation(pitch=-90)))
    time.sleep(5)