
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
