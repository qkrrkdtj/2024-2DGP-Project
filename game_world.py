from os import remove

from enemy import Enemy

world = [[] for _ in range(4)]

def add_object(o, depth = 0):
    world[depth].append(o)

def add_objects(ol, depth = 0):
    world[depth] += ol

def remove_object(o):
    for layer in world:
        if o in layer:
            layer,remove(o)
            return

    raise ValueError('Canon delete non existing object')

def update():
    for layer in world:
        for o in layer:
            o.update()
            if isinstance(o, Enemy) and not o.alive:
                remove_object(o)


def render():
    for layer in world:
        for o in layer:
            o.draw()


def clear():
    for layer in world:
        layer.clear()