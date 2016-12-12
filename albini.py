"""
Contains the means of weighting individual fuel size classes and 
categories via the method of Albini, 1976.  There are four "significant" 
differences between the Albini and Rothermel methods of aggregating
individual fuel parameters into a fuel complex.  Other differences exist,
but Albini did not consider them important enough to mention.  The changes
are outlined in Appendix III of Albini, and impacts the following areas:

1] The computation of dry weight loading has changed.
2] The exponent "A" in the potential reaction velocity is computed by a 
   more numerically stable means.
3] Moisture of extinction for fine live fuels has changed.
4] Reaction intensity (Rothermel eqn 58) is changed such that the 
   summation of contribution by category is no longer multiplied by 
   the category "weight".  


"""

import math
from model import Fuel
from rothweights import WeightedRothermelModel, RothermelFuelComplex, \
                        LIVE, DEAD, ONEHR

def AlbiniNetFuelLoading(self) :
  """
  Calculates the net fuel loading given the fuel mineral content and the
  ovendry fuel loading.  This method is specified in Albini's Appendix III,
  item 1.
  Requires:
    self.totMineralContent
    self.ovendryLoading
  Produces:
    self.netFuelLoading
  """
  self.netFuelLoading = self.ovendryLoading * (1-self.totMineralContent)

def AlbiniExponentA(self) :
  """
  Calculates the exponent "A" by Albini's method.  
  Requires:
    self.sigma
  Produces:
    self.exponentA
  """
  self.exponentA = 133. * math.pow(self.sigma, -0.7913)

class AlbiniFuel(Fuel) : 
  """
  This is a concrete class which can be used to represent fuel components.  
  Loading and potential reaction velocity are calculated by the method outlined
  in Albini, Appendix III.
  """
  calcNetFuelLoading = AlbiniNetFuelLoading
  calcExponentA      = AlbiniExponentA

class AlbiniFuelComplex (RothermelFuelComplex) :
  """
  This is a concrete class capable of representing a fuel complex
  as described by Albini.  
  """
  calcExponentA      = AlbiniExponentA

  def calcNetFuelLoading(self) : 
    """
    To prevent parent's method from screwing up the aggregate value
    """
    pass

  def calcLivingExtMoisture(self) :
    """
    Calculates the moisture of extinction for living fuel given the
    mass ratio of fine live to total fine fuels and the moisture
    content of the fine dead fuels.  Albini appendix III
    Requires:
      + dead and live one hour fuel loadings
      + fine dead fuel moisture
      + dead moisture of extinction
    Produces:
      + live fine fuel moisture
    """
    # do basic sanity check: Live fuels present?
    if (not (LIVE in self.fuelParameters)) or \
       (self.fuelParameters[LIVE][ONEHR].ovendryLoading == 0) :
      return

    self.calcWPrime()
    self.calcMPrime()
    ext = 2.9 * self.wPrime 
    ext *= 1. - (self.mPrime / self.extMoisture[DEAD])
    ext -= 0.226

    self.setExtMoisture(LIVE, ext)

  def calcWPrime(self) : 
    """
    Calculates the weighting parameter for the live moisture computation.
    Requires:
      + ovendryLoadings       (per fuel per category)
      + sigmas                (per fuel per category)
    Produces:
      + wPrime                (single value)
    """

    # calculate the numerator
    num =0.
    for deadFuel in self.fuelParameters[DEAD].values() : 
      num += deadFuel.ovendryLoading * math.exp(-138./deadFuel.sigma)

    # calculate the denominator
    den = 0.
    for liveFuel in self.fuelParameters[LIVE].values() :
      den += liveFuel.ovendryLoading * math.exp(-500./liveFuel.sigma)

    # compute and store the result
    self.wPrime = num / den

  def calcMPrime(self) :
    """
    Calculates the weighted dead fuel moisture.  This is a component of 
    the living fuel moisture of extinction calc.
    Requires:
      + ovendryLoadings       (per fuel per category)
      + sigmas                (per fuel per category)
      + fuelMoistures         (per fuel per category)
    Produces:
      + mPrime                (single value)
    """

    # calculate the numerator & denominator sums
    num = 0.
    den = 0.
    for deadFuel in self.fuelParameters[DEAD].values() :
      term = deadFuel.ovendryLoading * math.exp(-138./deadFuel.sigma)
      den += term
      num += term * deadFuel.fuelMoisture

    # calculate and store the result.
    self.mPrime = num/den



class WeightedAlbiniModel (WeightedRothermelModel) : 
  """
  This class calculates the reaction intensity via the method of Albini.
  """

  def calcReactionIntensity(self) :
    """
    Calculates the reaction intensity according to Albini, Appendix III.
    Requires:
      self.dampMoisture       (grouped into category)
      self.dampMineral        (grouped into category)
      self.potReactionVelocity (single value)
      self.fuel.netFuelLoading (grouped into category)
      self.fuel.heatContent   (grouped into category)

    Produces:
      self.reactionIntensity  (single value)
    """
    sum = 0.
    for category in self.dampMoisture.keys() :
      sum +=  self.fuel.netFuelLoading[category] * \
              self.fuel.heatContent[category] * \
              self.dampMoisture[category] * \
              self.dampMineral[category]

    self.reactionIntensity = sum * self.potReactionVelocity


