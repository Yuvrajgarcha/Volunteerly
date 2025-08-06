import math

class Circle():
    def __init__(self, radius):
        self.radius = radius

    def calc_area(self):
        area = math.pi * self.radius ** 2
        print(f'The area of the circle is {area:.2f}')

# Ask for input
radius = float(input('Enter the radius of the circle: '))

#instanatiatin objects
cl = Circle(radius)

#assigning method to the object
cl.calc_area()