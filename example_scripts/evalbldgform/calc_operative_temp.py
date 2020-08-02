import math

air_v = 1
mrt = 22 + 273.15
airt = 31 + 273.15

air_v_10 = 10*air_v
air_v_sqrt = math.sqrt(air_v_10)

top = mrt + (airt*air_v_sqrt)
bottom = 1 + air_v_sqrt
to = top/bottom

to2 = (mrt + airt)/2

print(to-273.15)
print(to2-273.15)