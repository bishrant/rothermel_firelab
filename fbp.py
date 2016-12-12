"""
Contains routines for unifying the components of the fire behavior 
prediction model coded in this package.
"""

import math
import nffl
from model import RothermelFuel
from rothweights import WeightedRothermelModel, RothermelFuelComplex, \
                        LIVE, DEAD
from albini import WeightedAlbiniModel, AlbiniFuelComplex, AlbiniFuel
from common.fbp import FireBehaviorPrediction

class RothermelFBP(FireBehaviorPrediction) :
  """
  Configures a "fire behavior prediction" element using the 
  Rothermel weighting scheme.
  """
  fuelModelMethods = { '1' : nffl.nffl1,   '2' : nffl.nffl2,
                       '3' : nffl.nffl3,   '4' : nffl.nffl4,
                       '5' : nffl.nffl5,   '6' : nffl.nffl6,
                       '7' : nffl.nffl7,   '8' : nffl.nffl8,
                       '9' : nffl.nffl9,   '10' : nffl.nffl10,
                       '11' : nffl.nffl11, '12' : nffl.nffl12,
                       '13' : nffl.nffl13 }
  fuelModelNames = fuelModelMethods.keys()


  # Produce Rothermel-weighted fuel classes
  _fbpFireModelClass = WeightedRothermelModel
  _fbpFuelModelClass = RothermelFuelComplex
  _fbpFuelComponentClass = RothermelFuel

  # represents the fuel complex and the fire model
  fuelComplex    = None
  fireModel      = None

  def _setFuelModel(self) : 
    if self.fireModel == None : 
      self.fireModel = self._fbpFireModelClass(self.fuelComplex)
    else : 
      self.fireModel.fuel = self.fuelComplex

  def setNamedFuelModel(self, modelName) : 
    # let the parent do it's thing
    FireBehaviorPrediction.setNamedFuelModel(self, modelName)

    # create a named NFFL fuel model
    nffl.FuelComponent = self._fbpFuelComponentClass
    nffl.FuelComplex   = self._fbpFuelModelClass
    self.fuelComplex = (self.fuelModelMethods[modelName])()
    self._setFuelModel()


  def setCustomFuelModel(self, model) : 
    # let the parent do it's thing
    FireBehaviorPrediction.setCustomFuelModel(self, model)

    # retain the reference
    self.fuelComplex = model
    self._setFuelModel()


  def setDeadFuelMoistures(self, moistures) : 
    # let the parent do it's thing
    FireBehaviorPrediction.setDeadFuelMoistures(self, moistures)

    # user MUST have selected a fuel model first!
    if self.fireModel == None :
      raise AttributeError("Set the fuel model before setting fuel moistures!")

    for i in moistures.items() :
      sizeClass = i[0]
      moisture  = i[1]
      if not (sizeClass in self.fuelComplex.fuelParameters[DEAD]) : 
        raise ValueError("Size class: " + sizeClass + " not in fuel model.")

      self.fuelComplex.setFuelMoisture(DEAD, sizeClass, moisture)


  def setLiveFuelMoistures(self, moistures) : 
    # let the parent do it's thing
    FireBehaviorPrediction.setLiveFuelMoistures(self, moistures)

    # user MUST have selected a fuel model first!
    if self.fireModel == None :
      raise AttributeError("Set the fuel model before setting fuel moistures!")

    # user MUST have selected a fuel model with LIVE fuels!
    if not LIVE in self.fuelComplex.fuelParameters : 
      raise ValueError("This fuel model does not have live fuels!!")

    for i in moistures.items() :
      sizeClass = i[0]
      moisture  = i[1]
      if not sizeClass in self.fuelComplex.fuelParameters[LIVE] : 
        raise ValueError("Size class: " + sizeClass + " not in fuel model.")

      self.fuelComplex.setFuelMoisture(LIVE, sizeClass, moisture)

  def getRateOfSpread(self) : 
    # check to see if the value is cached.
    if self.rateOfSpread != None : 
      return self.rateOfSpread

    self.evaluate()
    if self.rateOfSpread < 0. : 
      self.rateOfSpread = 0.
    return self.rateOfSpread

  def getHeatPerArea(self) : 
    # check to see if the value is cached.
    if self.rateOfSpread != None : 
      return self.heatPerArea

    self.evaluate()
    if self.heatPerArea < 0. : 
      self.heatPerArea = 0.
    return self.heatPerArea
    
  def evaluate(self) : 
    # only recompute if BOTH rateOfSpread and heatPerArea are null
    if (self.rateOfSpread == None) and (self.heatPerArea == None) :
      # aggregate the components into category and complex values
      self.fuelComplex.compute()

      # if there are live fuels, compute the live fuel moisture of 
      # extinction
      if LIVE in self.fuelComplex.fuelParameters : 
        self.fuelComplex.calcLivingExtMoisture()

      # set the slope and the wind now
      self.fireModel.setSlope(math.radians(self.slope))
      self.fireModel.setWind(self.midflameWindSpeed * (5280. / 60.))

      # compute the fire behavior
      self.fireModel.evaluate()

      # store the results
      self.heatPerArea = self.fireModel.reactionIntensity
      self.rateOfSpread = self.fireModel.ros

class AlbiniFBP(RothermelFBP) : 
  """
  Configures a fire behavior prediction element utilizing the Albini
  weighting scheme.
  """
  # Produce Albini-weighted fuel classes
  _fbpFireModelClass = WeightedAlbiniModel
  _fbpFuelModelClass = AlbiniFuelComplex
  _fbpFuelComponentClass = AlbiniFuel
