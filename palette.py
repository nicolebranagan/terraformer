from enum import Enum
import math

ega = [
    (0,0,0),
    (0,0,170),
    (0,170,0),
    (0,170,170),
    (170,0,0),
    (170,0,170),
    (170,85,00),
    (170,170,170),
    (85,85,85),
    (85,85,255),
    (85,255,85),
    (85,255,255),
    (255,85,85),
    (255,85,255),
    (255,255,85),
    (255,255,255)]

win16 = [
    (0,0,0),
    (0,0,128),
    (0,128,0),
    (0,128,128),
    (128,0,0),
    (128,0,128),
    (192,192,0),
    (192,192,192),
    (128,128,128),
    (0,0,255),
    (0,255,0),
    (0,255,255),
    (255,0,0),
    (255,0,255),
    (255,255,0),
    (255,255,255)]

class Constraint(Enum):
    Genesis = 0
    
def constrain(l, c):
    constrainfunc = {
        Constraint.Genesis : _constrain_genesis,
        }.get(c,lambda x: None)
    for i in range(0, len(l)):
        l[i] = constrainfunc(l[i])

def _constrain_genesis(c):
    return (math.floor(c[0]/32)*32,
            math.floor(c[1]/32)*32,
            math.floor(c[2]/32)*32)
