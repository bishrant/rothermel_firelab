"""
Contains the Rothermel equations for rate of spread, reaction rate, 
and intensity.  The parameters included in the equations are 
not the parameters included in the stylized models.  To translate between 
the two, one needs to weight the individual fuel size classes by an 
appropriate method.

There are a number of different methods for calculating various parameters,
and wherever possible the relevant computation is exposed as an 
attribute of the class which can be overwritten as desired.

The units used in this class are English, not metric.

Author: Bryce Nordgren / USDA Forest Service

References: 
Albini, F. A. Estimating Wildfire Behavior and Effects.  General Technical 
Report INT-30, USDA Forest Service. 1976. 92 p.

Rothermel, R. C. A mathematical model for predicting fire spread in 
  wildland fuels.  General Technical Report INT-115, USDA Forest Service.
  1972. 40 p.
"""

import math 

def RothermelNetFuelLoading(self) : 
  """
  Calculates the net fuel loading given the fuel mineral content and the 
  ovendry fuel loading.  This method is specified in Rothermel's eqn
  24.
  Requires:
    self.totMineralContent 
    self.ovendryLoading
  Produces:
    self.netFuelLoading 
  """
  self.netFuelLoading = self.ovendryLoading / (1+self.totMineralContent)

def RothermelExponentA(self) :
  """
  Calculates the exponent "A" by Rothermel's equation 39.  Requires the
  "sigma" attribute.  Produces the "exponentA" attribute
  """
  self.exponentA = 1./(4.77 * math.pow(self.sigma, 0.1) - 7.27)


class Fuel:
  """
  This class describes the fundamental characteristics of a "fuel" 
  element.  It is, in effect, an abstract class.  It should not be instantiated
  directly.  Use either RothermelFuel (this file) or AlbiniFuel.

  Attributes:
  calcExponentA                     method by which exponent A calc'd
  calcNetFuelLoading                method by which net fuel loading calc'd
  bulkDensity (rho_b) lb/ft^3       fuel-bed weight per unit volume
  particleDensity (rho_p) lb/ft^3   fuel-particle weight per unit volume
  packingRatio (dimensionless)      bulkDensity / particleDensity
  sigma ft^-1                       surface area to volume ratio
  optimalPacking                    optimal packing ratio for this fuel
  maxPotentialVelocity              maximum potential reaction velocity
  exponentA                         The exponent in Rothermel eqn 38
  heatingEfficiency                 efficiency of heat transfer to fuel
  extMoisture %                     moisture of extinction
  fuelMoisture %                    fuel moisture
  totMineralContent (fraction)      total mineral content
  effMineralContent (fraction)      silica free mineral content
  ovendryLoading lb/ft^2            ovendry fuel loading
  netFuelLoading                    net fuel loading
  heatContent  BTU / lb             fuel heat content 
  heatOfIgnition (BTU / lb)         heat of ignition for this fuel
  """
  
  #
  # These must be set by the class definitions of derived classes.
  #
  calcNetFuelLoading = None   # Method to calculate net fuel loading
  calcExponentA      = None   # Method to calculate the "A" exponent

  def __init__(self, 
               sigma=None, 
               loading=None) : 
    """
    Initializes a new "Fuel" object with reasonable values.  Such an 
    object is NOT ready to use.  One must call the setDensity,
    setSigma, setFuelMoisture, and setLoading methods prior to use.
    Default values are provided for total and effective mineral content and 
    heat content.
    """
    self.ovendryLoading  = loading
    self.bulkDensity     = None
    self.extMoisture     = None
    self.fuelMoisture    = None

    if sigma != None :
      self.setSigma(sigma)
    else:
      self.sigma = None

    # Default fuel characteristics
    self.particleDensity = 32.
    self.setMineralContent(0.0555, 0.01)
    self.setHeatContent(8000.0)



  def setDensity(self, bulk, particle=32.) : 
    """
    Sets both the bulk and particle fuel densities as well as computes
    the packing ratio.
    """
    self.bulkDensity = bulk
    self.particleDensity = particle
    self.packingRatio = bulk / particle

  def setSigma(self, sigma) : 
    """
    Sets the surface-area to volume ratio of the fuel.  This method also 
    calculates the optimal packing ratio and the maximum potential 
    reaction velocity.  See Rothermel's eqns 36 and 37.  The exponent "A" 
    (eqn 39) also needs to be recalculated, but the method by which 
    this occurs may be overridden by the user to reflect Albini's modification
    in appendix III of the referenced paper.
    In addition, the efficiency of heat transfer is also calculated
    (Rothermel eqn 14)
    """
    self.sigma = sigma
    self.optimalPacking = 3.348 * math.pow(sigma, -0.8189)
    
    sigma15 = math.pow(sigma, 1.5)
    self.maxPotentialVelocity = sigma15/(495 + 0.0594*sigma15)
    
    self.calcExponentA()
    self.heatingEfficiency = math.exp(-138/sigma)

  def setFuelMoisture(self, fuel, extinction=None) :
    """
    Sets the fuel moisture and the moisture of extinction for this fuel.
    Both moistures are fractions of water weight to dry fuel weight.
    Also calculates the heatOfIgnition parameter (Rothermel eqn 12).
    """
    self.extMoisture = extinction
    self.fuelMoisture = fuel
    self.heatOfIgnition = 250. + 1116 * self.fuelMoisture
  
  def setMineralContent(self, total, eff) :
    """
    Sets the total and effective mineral content of the fuel.  These are 
    fractions.
    """
    self.totMineralContent = total
    self.effMineralContent = eff

  def setHeatContent(self, heat) :
    """
    Sets the heat content of the fuel.  This is in BTU/lb.
    """
    self.heatContent = heat

  def setLoading(self, loading) : 
    """
    Sets the ovendry loading of the fuel in lb / ft^2
    """
    self.ovendryLoading = loading


class RothermelFuel (Fuel) : 
  """
  This is a concrete class which can be used to represent fuels.
  Loading and potential reaction velocity are calculated by the method of 
  Rothermel.
  """
  calcNetFuelLoading = RothermelNetFuelLoading
  calcExponentA      = RothermelExponentA
  


class RothermelModel : 
  """
  Contains the interim and final calculations produced by the Rothermel
  fire spread model.

  Attributes:
  fuel                            Characteristics of the fuel
  dampMoisture                    Moisture damping coefficient
  dampMineral                     Mineral damping coefficient
  potReactionVelocity             Potential reaction velocity
  reactionIntensity               Reaction intensity.
  propFluxRatio                   propagating flux / reaction intensity
  noWindRos     ft/min            ROS with no wind or slope
  midflameWind  ft/min            wind speed for this calculation
  windMultiplier                  calculated wind multiplier
  slopeRad   radians              slope for this calculation
  slopeMultiplier                 calculated slope multiplier
  ros           ft/min            rate of spread 
  """
  def __init__(self, fuel) : 
    self.fuel = fuel
    self.windSpeed = 0 
    self.windMultiplier = 0
    self.slopeRad = 0
    self.slopeMultiplier = 0 
  
  def calcMoistureDamping(self) : 
    """
    Calculates the moisture damping coefficient according to Rothermel, 
    eqn. 29.  Requires that the "fuel" attribute be set and that it contain
    the fuelMoisture and extMoisture attributes.  Produces the "dampMoisture"
    attribute.
    """
    ratio = self.fuel.fuelMoisture / self.fuel.extMoisture
    self.dampMoisture = 1 - 2.59 * ratio

    ratio2 = ratio * ratio
    self.dampMoisture += 5.11 * ratio2

    ratio3 = ratio2 * ratio
    self.dampMoisture -= 3.52 * ratio3
  
  def calcMineralDamping(self) : 
    """
    Calculates the mineral damping coefficient according to Rothermel, 
    eqn. 30.  
    Requires: 
      self.fuel.effMineralContent
    Produces: 
      self.dampMineral
    """
    self.dampMineral = math.pow(self.fuel.effMineralContent, -0.19) * 0.174
  
  def calcPotReactionVelocity(self) :
    """
    Calculates the potential reaction velocity as given by Rothermel, eqn
    38.  
    Requires:
      self.fuel.exponentA
      self.fuel.maxPotentialVelocity
      self.fuel.packingRatio
      self.fuel.optimalPacking
    Produces:
      self.potReactionVelocity
    """
    ratio = self.fuel.packingRatio / self.fuel.optimalPacking
    self.potReactionVelocity = self.fuel.maxPotentialVelocity * \
      math.pow(ratio, self.fuel.exponentA) * \
      math.exp(self.fuel.exponentA * (1-ratio))
    
  def calcReactionIntensity(self) : 
    """
    Calculates the reaction intensity according to Rothermel, eqn. 27.  
    Requires:
      self.dampMoisture
      self.dampMineral
      self.fuel.netFuelLoading
      self.potReactionVelocity
      self.fuel.heatContent

    Produces: 
      self.reactionIntensity
    """
    self.reactionIntensity = self.fuel.netFuelLoading * self.fuel.heatContent*\
      self.potReactionVelocity * self.dampMineral * self.dampMoisture
    
  def calcPropFluxRatio(self)  : 
    """
    Calculates the propagating flux ratio (Rothermel eqn 42)
    Requires:
      self.fuel.sigma
      self.fuel.packingRatio
    Produces: 
      self.propFluxRatio attribute
    """
    exponential = (0.792+0.681*math.sqrt(self.fuel.sigma)) * \
      (self.fuel.packingRatio + 0.1)
    self.propFluxRatio = math.exp(exponential) / (192 + 0.259*self.fuel.sigma)
  
  def calcNoWindRos(self):
    """
    Calculates the no-wind rate of spread via Rothermel's eqn 43.
    Requires:
      self.fuel.heatOfIgnition
      self.fuel.heatingEfficiency
      self.fuel.bulkDensity
      self.propFluxRatio
      self.reactionIntensity
    Produces:
      self.noWindRos 
    """
    self.noWindRos = self.reactionIntensity * self.propFluxRatio / \
      (self.fuel.bulkDensity * self.fuel.heatingEfficiency * \
       self.fuel.heatOfIgnition )

  def setWind(self, midflameWind) : 
    """
    Sets the "midflameWind" attribute of this model in ft/min.  Also calculates
    and records the windMultiplier via Rothermel's eqns (47-50).
    Requires: 
      self.fuel.sigma
      self.fuel.packingRatio
      self.fuel.optimalPacking
    Produces:
      self.midflameWind
      self.windMultiplier
    """
    
    self.midflameWind = midflameWind
    C = 7.47 * math.exp(-0.133 * math.pow(self.fuel.sigma, 0.55))
    B = 0.02526 * math.pow(self.fuel.sigma, 0.54)
    E = 0.715 * math.exp(-3.59e-4 * self.fuel.sigma)
    self.windMultiplier = C * math.pow(midflameWind,B) *\
      math.pow((self.fuel.packingRatio / self.fuel.optimalPacking),-E)

  def setSlope(self, slope) :
    """
    Sets the slope for this calculation (in radians).  Records this slope
    in the "slopeRad" attribute and calculates the "slopeMultiplier" 
    attribute via Rothermel's eqn 51.
    Requires:
      self.fuel.packingRatio
    Produces:
      self.slopeRad
      self.slopeMultiplier
    """
    self.slopeRad = slope
    tanSlope2 = math.tan(slope)
    tanSlope2 = tanSlope2*tanSlope2
    self.slopeMultiplier = 5.275 * math.pow(self.fuel.packingRatio, -0.3) *\
      tanSlope2

  def calcRos(self) : 
    """
    Calculates the rate of spread in (blah) via Rothermel's equation 52.
    This value is also returned.
    Requires:
      self.noWindRos
      self.windMultiplier
      self.slopeMultiplier
    Produces:
      self.ros
    """
    self.ros = self.noWindRos * \
        (1. + self.windMultiplier + self.slopeMultiplier)
    return self.ros

  def evaluate(self) : 
    """
    Assuming that everything has been "set", this method runs through the
    entire rate of spread calculation, calling the component methods
    in the correct order.  It then returns the rate of spread.
    """
    self.fuel.calcNetFuelLoading()
    self.calcPropFluxRatio()
    self.calcMineralDamping()
    self.calcMoistureDamping()
    self.calcPotReactionVelocity()
    self.calcReactionIntensity()
    self.calcNoWindRos()
    self.calcRos()
    return self.ros



