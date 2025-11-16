import numpy as np

# == Scene ==
class Scene():
    def __init__(self, spheres: list[Sphere], lights: list[Light]):
        self.spheres = spheres
        self.lights = lights

# == Objects ==
class Sphere():
    def __init__(self, centre: list[float, float, float], radius: int, colour: list[int, int, int], specular: int, reflectivity: float):
        self.centre: np.ndarray = np.array(centre)
        self.radius: int = radius
        self.colour: list[int, int, int] = colour
        self.specular: int = specular
        self.reflectivity: float = reflectivity
        
# == Lights ==
class Light():
    def __init__(self, intensity: float):
        self.intensity = intensity
        
class AmbientLight(Light):
    def __init__(self, intensity: float):
        super().__init__(intensity)

class PointLight(Light):
    def __init__(self, intensity: float, position: tuple[int, int, int]):
        self.pos: np.ndarray = np.array(position)
        super().__init__(intensity)
        
class DirectionalLight(Light):
    def __init__(self, intensity: float, direction: tuple[int, int, int]):
        self.direction: np.ndarray = np.array(direction)
        super().__init__(intensity)