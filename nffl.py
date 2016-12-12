"""
Contains factories which produce FuelComplex objects which represent the 
NFFL fuel models.
"""

from rothweights import RothermelFuelComplex, \
                        DEAD, LIVE, ONEHR, TENHR, HUNDREDHR
from model import RothermelFuel

#
# To change which types of objects this factory produces, change the 
# values of FuelComponent and FuelComplex below.  (For instance, if you wanted
# Albini fuels instead of Rothermel fuels....
#
FuelComponent = RothermelFuel
FuelComplex   = RothermelFuelComplex

def nffl1() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 1
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR, FuelComponent(3500., 0.034))
  fuel.setExtMoisture(DEAD, 0.12)
  fuel.setDepth(1.)
  return fuel
  
def nffl2() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 2
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(3000., 0.092))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.046))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.023))
  fuel.setFuelParams(LIVE, ONEHR,     FuelComponent(1500., 0.023))

  fuel.setExtMoisture(DEAD, 0.15)
  fuel.setDepth(1.)
  return fuel
  
  
def nffl3() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 3
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(1500., 0.138))

  fuel.setExtMoisture(DEAD, 0.25)
  fuel.setDepth(2.5)
  return fuel

def nffl4() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 4
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(2000., 0.230))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.184))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.092))
  fuel.setFuelParams(LIVE, ONEHR,     FuelComponent(1500., 0.230))

  fuel.setExtMoisture(DEAD, 0.20)
  fuel.setDepth(6.)
  return fuel
  

def nffl5() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 5
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(2000., 0.046))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.023))
  fuel.setFuelParams(LIVE, ONEHR,     FuelComponent(1500., 0.092))

  fuel.setExtMoisture(DEAD, 0.20)
  fuel.setDepth(2.)
  return fuel
  

def nffl6() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 6
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(1750., 0.069))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.115))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.092))

  fuel.setExtMoisture(DEAD, 0.25)
  fuel.setDepth(2.5)
  return fuel
  

def nffl7() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 7
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(1750., 0.052))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.086))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.069))
  fuel.setFuelParams(LIVE, ONEHR,     FuelComponent(1550., 0.017))

  fuel.setExtMoisture(DEAD, 0.40)
  fuel.setDepth(2.5)
  return fuel
  

def nffl8() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 8
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(2000., 0.069))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.046))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.115))

  fuel.setExtMoisture(DEAD, 0.30)
  fuel.setDepth(0.2)
  return fuel
  

def nffl9() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 9
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(2500., 0.134))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.019))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.007))

  fuel.setExtMoisture(DEAD, 0.25)
  fuel.setDepth(0.2)
  return fuel
  

def nffl10() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 10
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(2000., 0.138))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.092))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.230))
  fuel.setFuelParams(LIVE, ONEHR,     FuelComponent(1500., 0.092))

  fuel.setExtMoisture(DEAD, 0.25)
  fuel.setDepth(1.)
  return fuel
  

def nffl11() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 11
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(1500., 0.069))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.207))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.253))

  fuel.setExtMoisture(DEAD, 0.15)
  fuel.setDepth(1.)
  return fuel
  

def nffl12() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 12
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(1500., 0.184))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  0.644))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   0.759))

  fuel.setExtMoisture(DEAD, 0.20)
  fuel.setDepth(2.3)
  return fuel
  

def nffl13() : 
  """
  Produces and returns a FuelComplex object representative of NFFL model 13
  """
  fuel = FuelComplex()
  fuel.setFuelParams(DEAD, ONEHR,     FuelComponent(1500., 0.322))
  fuel.setFuelParams(DEAD, TENHR,     FuelComponent(109.,  1.058))
  fuel.setFuelParams(DEAD, HUNDREDHR, FuelComponent(30.,   1.288))

  fuel.setExtMoisture(DEAD, 0.25)
  fuel.setDepth(3.0)
  return fuel
  
