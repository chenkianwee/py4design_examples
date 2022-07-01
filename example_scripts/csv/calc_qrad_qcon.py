vams = 0.1
tair = 30.0
tskin = 0.3182*tair + 22.406
#tskin = 33
t_delta = tskin-tair

if vams > 0.1:
    hc = 10.4 * (vams**0.56)
    
else:    
    hc= 0.78* t_delta**0.56
    
qcon = hc * t_delta

emissivity = 0.98
boltzman = 5.670367*10**-8

ar_ad = 1

tmrt = 13
td = tskin-tmrt
td4 = tskin**4-tmrt**4

temp3 = (273.15 + ((tskin+tmrt)/2))**3
hr = 4*emissivity*boltzman*ar_ad*temp3
print hr, td
qrad = emissivity*boltzman*td4
print qrad

#x2 = (qrad/x1) - 273.15**3
#print x2
#x3 = 8*x2
#x4 = x3**(1/4.0)
#
#print x4 + 32
#print qcon