"""
This module extends the concepts introduced in the basic Rothermel model
by permitting the fuel array to be inhomogeneous.  It's conceptual 
basis lies in the definition of a Unit Fuel Cell.  A unit fuel cell may
have many size classes of fuel (1, 10, 100, and even 1000 hr fuels), and 
these size classes may be grouped by category (e.g., alive or dead).  The 
two primary fuel models for the US (NFFL and NFDRS) specify fuel in terms of 
loadings by category and size class.  However, it is the _weighting_ of 
these individual terms to provide a single input to Rothermel's fire spread
equation which differs among these systems.  

This module implements the method of weighting introduced in Rothermel's
1972 paper.

Author: Bryce Nordgren / USDA Forest Service
References :
Rothermel, R. C. A mathematical model for predicting fire spread in 
  wildland fuels.  General Technical Report INT-115, USDA Forest Service.
  1972. 40 p.
"""

import model
import math

# Fuel categories
DEAD = 'dead'
LIVE = 'live'

# Size classes
ONEHR = '1 hr'
TENHR = '10 hr'
HUNDREDHR = '100 hr'


class RothermelFuelComplex (model.RothermelFuel) : 
  """
  As listed in Rothermel, the input parameters to the weighting functions
  are one of the following: 
    1] Specific to the individual category/class combination.
      + ovendryLoading
      + sigma
      + totMineralContent
      + effMineralContent
      + heatContent
      + fuelMoisture
      + particleDensity
    2] A mean over all the classes in a category.
      + extMoisture
    3] A mean over the entire fuel array.
      + depth

  This fuel model needs to aggregate as follows
    1] A mean over all size classes in a category:
      + netFuelLoading
      + heatContent
      + effMineralContent
      + fuelMoisture
    2] A mean over the entire fuel array:
      + sigma
      + packingRatio
      + bulkDensity
  """

  def __init__(self) :
    model.Fuel.__init__(self)
    # Fuel parameters under #1 above
    self.fuelParameters = {}

    # Extinction moisture (#2 above)
    self.extMoisture = {}

    # fuel bed depth (#3 above)
    self.depth = 0.0

    # the A sub ij's in Rothermel eqn 53
    self.classAreas = {}
    # the A sub i's in Rothermel eqn 54
    self.categoryAreas = {}

    # A sub T in Rothermel eqn 55
    self.totalArea = 0. 

    # f sub ij in Rothermel eqn 56
    self.classWeighting = {}

    # f sub i in Rothermel eqn 57
    self.categoryWeighting = {}


  def setFuelParams(self, category, fuelClass, fuel) : 
    """
    Sets the fuel parameter information for the given category and 
    fuel class.  The caller is expected to provide a "fuel" instance
    with all the parameters appropriately set.
    """
    if not (category in self.fuelParameters) :
      self.fuelParameters[category] = {}

    classes = self.fuelParameters[category]
    classes[fuelClass] = fuel

  def setExtMoisture(self, category, moisture) : 
    """
    Set the extinction moisture averaged over all the classes in a given 
    category.
    """
    self.extMoisture[category] = moisture

  def setDepth(self, depth) : 
    """
    Set the depth of the fuel bed.  This one value applies to the entire 
    fuel array.  (ft)
    """
    self.depth = depth

  def setFuelMoisture(self, category, sizeClass, moisture) : 
    """
    Sets the fuel moisture of the particular size class/category 
    combination.  Moisture is a fraction of water weight to dry wood
    weight.  This is just a convenience method to store a value in the 
    fuelParameters attribute.
    """
    self.fuelParameters[category][sizeClass].setFuelMoisture(moisture)

  def calcLivingExtMoisture(self) : 
    """
    Calculates the moisture of extinction for living fuel given the 
    mass ratio of fine live to total fine fuels and the moisture 
    content of the fine dead fuels.  Rothermel eqn 88
    Requires:
      + dead and live one hour fuel loadings
      + fine dead fuel moisture
    Produces:
      + live fine fuel moisture
    """
    totalMass = self.fuelParameters[DEAD][ONEHR].ovendryLoading+ \
                self.fuelParameters[LIVE][ONEHR].ovendryLoading
    massRatio = self.fuelParameters[LIVE][ONEHR].ovendryLoading / totalMass
    ext = 2.9 * ( (1-massRatio) / massRatio)
    ext *= 1. - (10./3.) * self.fuelParameters[DEAD][ONEHR].fuelMoisture
    ext -= 0.226

    self.setExtMoisture(LIVE, ext)

  def calcMeanSurfaceAreaOneClass(self, fuel) : 
    """
    Calculates the mean total surface area of a single size class entry
    per Rothermel equation 53.  Returns the result.
    """
    return (fuel.sigma * fuel.ovendryLoading) / fuel.particleDensity

  def calcMeanSurfaceAreaOneCategory(self, category) : 
    """
    Calculates the mean total surface area of a category via Rothermel
    equation 54
    """
    # clear out whatever was there before.
    curClass = {}
    self.classAreas[category] = curClass

    total = 0.
    for fuelClass in self.fuelParameters[category].items() : 
      curArea = self.calcMeanSurfaceAreaOneClass(fuelClass[1])
      total += curArea
      curClass[fuelClass[0]] = curArea

    self.categoryAreas[category] = total

  def calcMeanSurfaceArea(self) : 
    """
    Calculates the total surface area as given in Rothermel eqn 55
    """
    self.totalArea = 0.
    self.categoryAreas = {}
    self.classAreas = {}
    for cat in self.fuelParameters.keys() : 
      self.calcMeanSurfaceAreaOneCategory(cat)
      self.totalArea += self.categoryAreas[cat]

  def calcWeightingParameters(self) :
    """
    Calculates the weighting parameters by Rothermel equations 56 and 57.
    This method ensures the calculations for surface area are brought 
    up-to-date with the current fuel class descriptions, then calculates
    the weightings.
    """
    self.calcMeanSurfaceArea()

    # wipe out previous values
    self.categoryWeighting = {}
    self.classWeighting    = {}

    # loop over categories
    for cat in self.classAreas.keys() :

      # eqn 57 ; total category weight
      self.categoryWeighting[cat] = self.categoryAreas[cat] / self.totalArea

      # initialize per class values with empty dictionary
      catClassWeights = {}
      self.classWeighting[cat] = catClassWeights

      # loop over fuel size classes
      for curClass in self.classAreas[cat].items() :
        # eqn 56 ; weighting for an individual fuel size class
        catClassWeights[curClass[0]] = curClass[1] / self.categoryAreas[cat] 

  def calcNetFuelLoading(self) :
    "To prevent parent's method from screwing up the aggregate value"
    pass
    
  def aggregateIntoCategories(self) : 
    """
    Aggregates fuel complex parameters by category, producing dictionaries
    for each parameter.
    """
    self.heatContent = {}
    self.netFuelLoading  = {}
    self.effMineralContent = {} 
    self.fuelMoisture = {}
    for cat in self.categoryWeighting.keys() : 
      
      # initialize to 0
      self.heatContent[cat] = 0.
      self.netFuelLoading[cat]  = 0.
      self.effMineralContent[cat] = 0.
      self.fuelMoisture[cat]      = 0.

      classWgts = self.classWeighting[cat]
      for j in classWgts.items() :
        className = j[0]
        curFuel   = self.fuelParameters[cat][className]
        curWgt    = j[1]

        #eqn 59
        curFuel.calcNetFuelLoading()
        self.netFuelLoading[cat] += curWgt * curFuel.netFuelLoading

        #eqn 61
        self.heatContent[cat]+= curWgt * curFuel.heatContent

        #eqn 63
        self.effMineralContent[cat] += curWgt * curFuel.effMineralContent

        #eqn 66
        self.fuelMoisture[cat] += curWgt * curFuel.fuelMoisture

  def aggregateIntoComplex(self) : 
    """
    Aggregates the parameters into the once-per-complex descriptors.
    """

    # initialize
    sigma = 0.
    packingRatio = 0.
    bulkDensity  = 0.

    # loop over categories
    for i in self.categoryWeighting.items() :
      cat = i[0]
      catWeight = i[1]

      # reset the per-category sums.
      catSigma = 0.

      classWgts = self.classWeighting[cat]
      for j in classWgts.items() : 
        className= j[0]
        curFuel  = self.fuelParameters[cat][className]
        curWgt   = j[1]

        # eqn 72
        catSigma += curWgt * curFuel.sigma

        # eqn 73
        packingRatio  += curWgt * curFuel.ovendryLoading / \
                          curFuel.particleDensity

        # eqn 74
        bulkDensity   += curWgt * curFuel.ovendryLoading

      sigma += catWeight * catSigma

    # eqn 74
    self.bulkDensity = bulkDensity / self.depth
    # eqn 73
    self.packingRatio = packingRatio / self.depth

    self.setSigma(sigma)

  def compute(self) : 
    """
    Call this method once all the fuel components have been set.  This 
    method calculates all the per-category and per-complex values from
    the components.  If you later change anything, you must call this 
    method again.  You may change component fuel moistures and 
    category moistures of extinction without invalidating these 
    computations.
    """
    self.calcWeightingParameters()
    self.aggregateIntoCategories()
    self.aggregateIntoComplex()
        

class WeightedRothermelModel (model.RothermelModel) : 
  """
  Computes those components of the Rothermel model which are affected by the
  classification of the fuel complex into categories and size classes.  
  Functions which can be inherited from the base model are.
  These functions are redefined here:
    + calcMineralDamping
    + calcMoistureDamping
    + calcReactionIntensity
  """

  def calcMineralDamping(self) : 
    """
    Calculates a vector of the mineral damping coefficients by category.
    eqn. 62.
    Requires:
      self.fuel.effMineralContent (vector)
    Produces:
      self.dampMineral (vector)
    """
    self.dampMineral = {}
    for i in self.fuel.effMineralContent.items() :
      self.dampMineral[i[0]] = math.pow(i[1], -0.19) * 0.174


  def calcMoistureDamping(self) :
    """
    Calculates the moisture damping coefficient according to Rothermel,
    eqn. 64.  
    Requires: 
      self.fuel.fuelMoisture (grouped into "category")
      self.fuel.extMoisture  (grouped into "category")
    Produces:
      self.dampMoisture      (grouped into "category")
    """
    self.dampMoisture = {}
    for i in self.fuel.fuelMoisture.items() : 
      category = i[0]
      fuelMoisture = i[1]
      extMoisture  = self.fuel.extMoisture[category]
      ratio = fuelMoisture / extMoisture
      self.dampMoisture[category] = 1 - 2.59 * ratio

      ratio2 = ratio * ratio
      self.dampMoisture[category] += 5.11 * ratio2

      ratio3 = ratio2 * ratio
      self.dampMoisture[category] -= 3.52 * ratio3

  def calcReactionIntensity(self) :
    """
    Calculates the reaction intensity according to Rothermel, eqn. 58.
    Requires:
      self.dampMoisture       (grouped into category)
      self.dampMineral        (grouped into category)
      self.potReactionVelocity (single value)
      self.fuel.categoryWeighting (grouped into category)
      self.fuel.netFuelLoading (grouped into category)
      self.fuel.heatContent   (grouped into category)

    Produces:
      self.reactionIntensity  (single value)
    """
    sum = 0.
    for category in self.dampMoisture.keys() :
      sum +=  self.fuel.categoryWeighting[category] * \
              self.fuel.netFuelLoading[category] * \
              self.fuel.heatContent[category] * \
              self.dampMoisture[category] * \
              self.dampMineral[category]

    self.reactionIntensity = sum * self.potReactionVelocity

  def calcNoWindRos(self):
    """
    Calculates the no-wind rate of spread via Rothermel's eqn 75.
    Requires:
      heatOfIgnition              (per category per size class)
      heatingEfficiency           (per category per size class)
      (both the above are in self.fuel.fuelParameters)

      fuel.categoryWeighting      (per category)

      self.fuel.bulkDensity       (single value)
      self.propFluxRatio          (single value)
      self.reactionIntensity      (single value)

    Produces:
      self.noWindRos              (single value)
    """
    sources = self.propFluxRatio * self.reactionIntensity
    sinks = 0.
    # loop over the categories
    for i in self.fuel.fuelParameters.items() : 
      category = i[0]
      innerSum = 0.

      # loop over the size classes
      for j in i[1].items() : 
        sizeClass = j[0]
        fuel = j[1]
        innerSum += self.fuel.classWeighting[category][sizeClass] * \
                    fuel.heatOfIgnition * fuel.heatingEfficiency

      sinks += self.fuel.categoryWeighting[category] * innerSum

    # compute and save the result
    self.noWindRos = sources / sinks
