import unyt as u

from topology.core import Potential

class BondType(Potential):
    """A connection type."""

    def __init__(self,
                 name='BondType',
                 expression='0.5 * k * (r-r_eq)**2',
                 parameters={
                     'k': 1000 * u.Unit('kJ / (nm**2)'),
                     'r_eq': 0.14 * u.nm
                 },
                 independent_variables={'r'}):

        super(BondType, self).__init__(name=name, expression=expression,
                parameters=parameters, independent_variables=independent_variables)

    def __repr__(self):
        return "<BondType {}, id {}>".format(self.name, id(self))

        
