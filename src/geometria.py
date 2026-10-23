import math


def wrap(pos, worldSize):

    x=pos[0] % worldSize[0]
    y=pos[1] % worldSize[1]

    return (x,y)

def delta(a,b, worldSize):
    metadeL= worldSize[0]/2
    metadeA= worldSize[1]/2

    vx = ((b[0] - a[0] + metadeL) % worldSize[0]) - metadeL
    vy = ((b[1] - a[1] + metadeA) % worldSize[1]) - metadeA
    return (vx,vy)


def angulo_relativo(ang_creatura: float, vetor_comida:tuple[float,float]):
        ang_absoluto_comida= math.atan2(vetor_comida[1], vetor_comida[0])
        inter = ang_absoluto_comida-ang_creatura

        v = ((inter + math.pi) % (2*math.pi)) - math.pi

        return v

def pitagoras(ponto: tuple):
     return math.sqrt(ponto[0]**2 + ponto[1]**2)