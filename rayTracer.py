from canvas import Canvas
from primitives import *
from math import inf, sqrt
import time
import numpy as np

class RayTracer():
    def __init__(self, dimX: int, dimY: int, scene: Scene = Scene([], []), cameraPos: tuple[int, int, int] = (0, 0, 0), cameraRot: tuple[int, int] = (0, 0), recursionDepth: int = 3):
        self.canvas = Canvas(dimX, dimY)
        
        self.recursionDepth: int = recursionDepth
        
        self.cW: int = dimX
        self.cH: int = dimY
        
        self.cameraPos: np.ndarray[3] = np.array(cameraPos) # X Y Z
        self.cameraRot: list[float] = cameraRot # Pitch Yaw
        
        # Rotational matrix:
        pitch = np.radians(-self.cameraRot[0])  # Up/down (rotation around X-axis)
        yaw = np.radians(self.cameraRot[1])    # Left/right (rotation around Y-axis)
        rX = np.array([
            [1, 0, 0],
            [0, np.cos(pitch), -np.sin(pitch)],
            [0, np.sin(pitch), np.cos(pitch)]
        ])
        rY = np.array([
            [np.cos(yaw), 0, np.sin(yaw)],
            [0, 1, 0],
            [-np.sin(yaw), 0, np.cos(yaw)]
        ])
        rotationalMatrix: np.ndarray = rY @ rX 

        self.vW: int = 1
        self.vH: int = 1
        self.vD: int = 1
        
        self.scene: Scene = scene
        
        pixel = 1
        pixelCount = dimX * dimY
        startTime = time.time()
        
        for yCoord in range(self.cH // 2, (-self.cH) // 2, -1):
            for xCoord in range((-self.cW) // 2, self.cW // 2) :
                print(f"Rendering pixel {pixel} / {pixelCount} | {(100 * pixel / pixelCount):.3f}%", end="\r")
                coords: np.ndarray[3] = rotationalMatrix @ self.canvasToViewport(xCoord, yCoord)
                colour = self.traceRay(self.cameraPos, coords, 1, inf, self.recursionDepth)
                self.canvas.setPixel(xCoord, yCoord, colour)
                pixel += 1
            self.canvas.updateCanvas() # Show chunk

        print(f"\nRendered {dimX * dimY} pixels in {(time.time() - startTime):.3f}s")
    
        self.canvas.finishRendering()
    
    def canvasToViewport(self, cX: int, cY: int) -> np.ndarray[3]:
        return np.array((cX * (self.vW / self.cW), cY * (self.vH / self.cH), self.vD))
    
    def closestIntersection(self, origin: np.ndarray[3], coords: np.ndarray[3], startDistance: float | int, endDistance: float | int) -> tuple[Sphere | None, float]:
        closestT = inf
        closestSphere: None | Sphere = None
        
        for sphere in self.scene.spheres:
            t1, t2 = self.intersectRaySphere(origin, coords, sphere)
            if startDistance <= t1 <= endDistance and t1 < closestT:
                closestT = t1
                closestSphere = sphere
            if startDistance <= t2 <= endDistance and t2 < closestT:
                closestT = t2
                closestSphere = sphere
                
        return closestSphere, closestT
    
    def traceRay(self, origin: np.ndarray[3], coords: np.ndarray[3], startDistance: float | int, endDistance: float | int, recursionDepth: int) -> np.ndarray[3]:
        closestSphere, closestT = self.closestIntersection(origin, coords, startDistance, endDistance)
                
        if closestSphere == None:
            return np.array([0, 0, 0]) # Black BG
        
        # Local colour
        surfacePos: np.ndarray[3] = origin + closestT * coords # Intersection
        normal: np.ndarray[3] = surfacePos - closestSphere.centre # Surface normal at intersection
        normal: np.ndarray[3] = normal / np.linalg.norm(normal)
        localColour: np.ndarray[3] = np.clip(np.array(closestSphere.colour) * self.computeLighting(surfacePos, normal, -coords, closestSphere.specular), 0, 255) # Clamp to [0, 255] to prevent overflow

        reflectivity = closestSphere.reflectivity
        if recursionDepth <= 0 or reflectivity <= 0:
            return localColour
        
        reflectedRay: np.ndarray[3] = self.reflectRay(normal, -coords)
        reflectedColour: np.ndarray[3] = self.traceRay(surfacePos, reflectedRay, 0.001, inf, recursionDepth - 1)
        
        return localColour * (1 - reflectivity) + reflectedColour * reflectivity
    
    def reflectRay(self, normal: np.ndarray[3], ray: np.ndarray[3]) -> np.ndarray[3]:
        return 2 * normal * np.dot(normal, ray) - ray
    
    def intersectRaySphere(self, cameraPos: np.ndarray[3], coords: np.ndarray[3], sphere: Sphere) -> tuple[float, float]:
        radius = sphere.radius
        centreToCam = cameraPos - sphere.centre
        
        coordsVector = coords
        
        # Solve the quadratic
        a = np.dot(coordsVector, coordsVector)
        b = 2 * np.dot(centreToCam, coordsVector)
        c = np.dot(centreToCam, centreToCam) - radius ** 2
        
        # Look for valid solution
        discriminant = b ** 2 - 4 * a * c
        if discriminant < 0: # Quadratic has no real solution
            return (inf, inf)
        
        return (-b + sqrt(discriminant)) / (2 * a), (-b - sqrt(discriminant)) / (2 * a)
    
    def computeLighting(self, hitPos: np.ndarray, normal: np.ndarray, viewVector: np.ndarray, specular: int) -> float:
        intensity: float = 0.0
        
        for light in self.scene.lights:
            
            if isinstance(light, AmbientLight):
                intensity += light.intensity
            else:
                if isinstance(light, PointLight):
                    lightDirection = light.pos - hitPos
                    maxT = 1
                else:
                    lightDirection = light.direction
                    maxT = inf
                
                # Check for shadows
                shadowSphere, _ = self.closestIntersection(hitPos, lightDirection, 0.001, maxT)
                if shadowSphere != None:
                    continue
                
                # Diffuse reflection
                normalDotDirection = np.dot(normal, lightDirection)
                if normalDotDirection > 0:
                    intensity += light.intensity * normalDotDirection / (np.linalg.norm(normal) * np.linalg.norm(lightDirection))
                    
                # Specular reflection
                if specular != -1:
                    reflectedRay: np.ndarray = self.reflectRay(normal, lightDirection)
                    reflectedDotView: np.ndarray = np.dot(reflectedRay, viewVector)
                    if reflectedDotView > 0:
                        intensity += light.intensity * np.pow(reflectedDotView / (np.linalg.norm(reflectedRay) * np.linalg.norm(viewVector)), specular)
                    
        return intensity