import warnings

import numpy as np
import unyt as u
from boltons.setutils import IndexedSet

from gmso.core.bond import Bond
from gmso.core.angle import Angle
from gmso.core.dihedral import Dihedral
from gmso.core.potential import Potential
from gmso.core.atom_type import AtomType
from gmso.core.bond_type import BondType
from gmso.core.angle_type import AngleType
from gmso.core.dihedral_type import DihedralType
from gmso.utils._constants import ATOM_TYPE_DICT, BOND_TYPE_DICT, ANGLE_TYPE_DICT, DIHEDRAL_TYPE_DICT
from gmso.exceptions import GMSOError


class Topology(object):
    """A topology.

    A topology represents a chemical structure wherein lie the collection
    of sites which together form a chemical structure containing connections
    (gmso.Bond, gmso.Angle and gmso.Dihedral (along with their associated types).
    A topology is the fundamental data structure in GMSO, from which we can gather
    various information about the chemical structure and apply a forcefield
    before converting the structure into a format familiar to various simulation
    engines.

    Parameters
    ----------
    name : str, optional, default='Topology'
        A name for the Topology.
    box : gmso.Box, optional, default=None
        A gmso.Box object bounding the topology

    Attributes
    ----------
    typed : bool
        True if the topology is typed

    combining_rule : str, ['lorentz', 'geometric']
        The combining rule for the topology, can be either 'lorentz' or 'geometric'

    n_sites : int
        Number of sites in the topology

    n_connections : int
        Number of connections in the topology (Bonds, Angles, Dihedrals)

    n_bonds : int
        Number of bonds in the topology

    n_angles: int
        Number of angles in the topology

    n_dihedrals : int
        Number of dihedrals in the topology

    n_subtops : int
        Number of subtopolgies in the topology

    connections : tuple of gmso.Connection objects
        A collection of bonds, angles and dihedrals in the topology

    bonds : tuple of gmso.Bond objects
        A collection of bonds in the topology

    dihedrals : tuple of gmso.Dihedral objects
        A collection of dihedrals in the topology

    connection_types : tuple of gmso.Potential objects
        A collection of BondTypes, AngleTypes and DihedralTypes in the topology

    atom_types : tuple of gmso.AtomType objects
        A collection of AtomTypes in the topology

    bond_types : tuple of gmso.BondType objects
        A collection of BondTypes in the topology

    angle_types : tuple of gmso.AngleType objects
        A collection go AngleTypes in the topology

    dihedral_types : tuple of gmso.DihedralType objects
        A collection of DihedralTypes in the topology

    atom_type_expressions : list of gmso.AtomType.expression objects
        A collection of all the expressions for the AtomTypes in topology

    connection_type_expressions : list of gmso.Potential.expression objects
        A collection of all the expressions for the Potential objects in the topology that represent a connection type

    bond_type_expressions : list of gmso.BondType.expression objects
        A collection of all the expressions for the BondTypes in topology

    angle_type_expressions : list of gmso.AngleType.expression objects
        A collection of all the expressions for the AngleTypes in topology

    dihedral_type_expressions : list of gmso.DihedralType.expression objects
        A collection of all the expression for the DihedralTypes in the topology

    See Also
    --------
    gmso.SubTopology :
        A topology within a topology
    """
    def __init__(self, name="Topology", box=None):
        if name is not None:
            self._name = name
        else:
            self._name = "Topology"

        self._box = box
        self._sites = IndexedSet()
        self._typed = False
        self._connections = IndexedSet()
        self._bonds = IndexedSet()
        self._angles = IndexedSet()
        self._dihedrals = IndexedSet()
        self._subtops = IndexedSet()
        self._atom_types = {}
        self._connection_types = {}
        self._bond_types = {}
        self._angle_types = {}
        self._dihedral_types = {}
        self._combining_rule = 'lorentz'
        self._set_refs = {
            ATOM_TYPE_DICT: self._atom_types,
            BOND_TYPE_DICT: self._bond_types,
            ANGLE_TYPE_DICT: self._angle_types,
            DIHEDRAL_TYPE_DICT: self._dihedral_types,
        }

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = str(name) if name else None

    @property
    def box(self):
        return self._box

    @box.setter
    def box(self, box):
        self._box = box

    @property
    def typed(self):
        return self._typed

    @typed.setter
    def typed(self, typed):
        self._typed = typed

    @property
    def combining_rule(self):
        return self._combining_rule

    @combining_rule.setter
    def combining_rule(self, rule):
        if rule not in ['lorentz', 'geometric']:
            raise GMSOError('Combining rule must be `lorentz` or `geometric`')
        self._combining_rule = rule

    @property
    def positions(self):
        xyz = np.empty(shape=(self.n_sites, 3)) * u.nm
        for i, site in enumerate(self._sites):
            xyz[i, :] = site.position
        return xyz

    @property
    def n_sites(self):
        return len(self.sites)

    @property
    def n_connections(self):
        return len(self.connections)

    @property
    def n_bonds(self):
        return len(self.bonds)

    @property
    def n_angles(self):
        return len(self.angles)

    @property
    def n_dihedrals(self):
        return len(self.dihedrals)

    @property
    def subtops(self):
        return self._subtops

    @property
    def n_subtops(self):
        return len(self._subtops)

    @property
    def sites(self):
        return tuple(self._sites)

    @property
    def connections(self):
        return tuple(self._connections)

    @property
    def bonds(self):
        return tuple(self._bonds)

    @property
    def angles(self):
        return tuple(self._angles)

    @property
    def dihedrals(self):
        return tuple(self._dihedrals)

    @property
    def atom_types(self):
        return tuple(self._atom_types.values())

    @property
    def connection_types(self):
        return tuple(self._connection_types.values())

    @property
    def bond_types(self):
        return tuple(self._bond_types.values())

    @property
    def angle_types(self):
        return tuple(self._angle_types.values())

    @property
    def dihedral_types(self):
        return tuple(self._dihedral_types.values())

    @property
    def atom_type_expressions(self):
        return list(set([atype.expression for atype in self.atom_types]))

    @property
    def connection_type_expressions(self):
        return list(set([contype.expression for contype in self.connection_types]))

    @property
    def bond_type_expressions(self):
        return list(set([btype.expression for btype in self.bond_types]))

    @property
    def angle_type_expressions(self):
        return list(set([atype.expression for atype in self.angle_types]))

    @property
    def dihedral_type_expressions(self):
        return list(set([atype.expression for atype in self.dihedral_types]))

    def add_site(self, site, update_types=True):
        """Add a site to the topology

        This method will add a site to the existing topology, since
        sites are stored in an indexed set, adding redundant site
        will have no effect. If the update_types parameter is set to
        true (default behavior), this method will also check if there
        is an gmso.AtomType associated with the site and it to the
        topology's AtomTypes collection.

        Parameters
        -----------
        site : gmso.core.Site
            Site to be added to this topology
        update_types : (bool), default=True
            If true, add this site's atom type to the topology's set of AtomTypes
        """
        self._sites.add(site)
        if update_types and site.atom_type:
            site.atom_type.topology = self
            site.atom_type = self._atom_types.get(site.atom_type, site.atom_type)
            self._atom_types[site.atom_type] = site.atom_type
            self.is_typed(updated=False)

    def update_sites(self):
        """Update the sites of the topology.

        This method will update the sites in the topology
        based on the connection members, For example- if you
        add a bond to a topology, without adding the constituent
        sites, this method can be called to add the sites which are the
        connection members of the bond as shown below.

            >>> import gmso
            >>> site1 = gmso.Site(name='MySite1')
            >>> site2 = gmso.Site(name='MySite2')
            >>> bond1 = gmso.Bond(name='site1-site2', connection_members=[site1, site2])
            >>> this_topology = gmso.Topology('TwoSitesTopology')
            >>> this_topology.add_connection(bond1)
            >>> this_topology.update_sites()

        See Also
        --------
        gmso.Topology.update_connections :
            Update the connections in the topology to reflect any added sites connections
        gmso.Topology.add_site : Add a site to the topology.
        gmso.Topology.add_connection : Add a Bond, an Angle or a Dihedral to the topology.
        gmso.Topology.update_topology : Update the entire topology.
        """
        for connection in self.connections:
            for member in connection.connection_members:
                if member not in self._sites:
                    self.add_site(member)

    def add_connection(self, connection, update_types=True):
        """Add a gmso.Connection object to the topology.

        This method will add a gmso.Connection object to the
        topology, it can be used to generically include any
        Connection object i.e. Bond or Angle or Dihedral to
        the topology. According to the type of object added,
        the equivalent collection in the topology is updated.
        For example- If you add a Bond, this method will update
        topology.connections and topology.bonds object. Additionally,
        if update_types is True (default behavior), it will also
        update any Potential objects associated with the connection.

        Parameters
        ----------
        connection : one of gmso.Connection, gmso.Bond, gmso.Angle or gmso.Dihedral object
        update_types : bool, default=True
            If True also add any Potential object associated with connection to the
            topology.
        """
        for conn_member in connection.connection_members:
            if conn_member not in self.sites:
                self.add_site(conn_member)
        self._connections.add(connection)
        if isinstance(connection, Bond):
            self._bonds.add(connection)
        if isinstance(connection, Angle):
            self._angles.add(connection)
        if isinstance(connection, Dihedral):
            self._dihedrals.add(connection)
        if update_types:
            self.update_connection_types()

    def update_connections(self, update_types=False):
        """Update the topology's connections(bonds, angles, dihedrals) from its sites.

        This method takes all the sites in the current topology and if any connection
        (Bond, Angle, Dihedral) is present in the site but not in the topology's connection
        collection, this method will add to that collection. If update_types is True (default
        behavior is False), this method will also add the Potential objects(AtomType, BondType,
        AngleType, DihedralType) to the topology's respective collection.

        Parameters
        ----------
        update_types : bool, default=False

        See Also
        --------
        gmso.Topology.update_sites :
            Update the sites in the topology to reflect any added connection's sites
        gmso.Topology.add_connection : Add a Bond, an Angle or a Dihedral to the topology.
        gmso.Topology.add_site : Add a site to the topology.
        gmso.Topology.update_connection_types :
            Update the connection types based on the connection collection in the topology.
        gmso.Topology.update_topology : Update the entire topology.

        """
        for site in self.sites:
            for conn in site.connections:
                if conn not in self.connections:
                    self.add_connection(conn, update_types=False)
        if update_types:
            self.update_connection_types()
            self.is_typed()

    def update_bonds(self, update_types=False):
        """Uses gmso.Topology.update_connections to update bonds in the topology.

        This method is an alias for gmso.Topology.update_connections.

        See Also
        --------
        gmso.Topology.update_connections : Update all the Bonds, Angles and Dihedrals in the topology.
        """
        self.update_connections(update_types)

    def update_angles(self, update_types=False):
        """Uses gmso.Topology.update_connections to update angles in the topology.

        This method is an alias for gmso.Topology.update_connections.

        See Also
        --------
        gmso.Topology.update_connections : Update all the Bonds, Angles and Dihedrals in the topology.
        """
        self.update_connections(update_types)

    def update_dihedrals(self, update_types=False):
        """Uses gmso.Topology.update_connections to update dihedrals in the topology.

        This method is an alias for gmso.Topology.update_connections.

        See Also
        --------
        gmso.Topology.update_connections : Update all the Bonds, Angles and Dihedrals in the topology.
        """
        self.update_connections(update_types)

    def update_connection_types(self):
        """Update the connection types based on the connection collection in the topology.

        This method looks into all the connection objects (Bonds, Angles, Dihedrals) to
        check if any Potential object (BondType, AngleType, DihedralType) is not in the
        topology's respective collection and will add those objects there.

        See Also
        --------
        gmso.Topology.update_atom_types : Update atom types in the topology.
        """
        for c in self.connections:
            if c.connection_type is None:
                warnings.warn('Non-parametrized Connection {} detected'.format(c))
            elif not isinstance(c.connection_type, Potential):
                raise GMSOError('Non-Potential {} found'
                                    'in Connection {}'.format(c.connection_type, c))
            elif c.connection_type not in self._connection_types:
                c.connection_type.topology = self
                self._connection_types[c.connection_type] = c.connection_type
                if isinstance(c.connection_type, BondType):
                    self._bond_types[c.connection_type] = c.connection_type
                if isinstance(c.connection_type, AngleType):
                    self._angle_types[c.connection_type] = c.connection_type
                if isinstance(c.connection_type, DihedralType):
                    self._dihedral_types[c.connection_type] = c.connection_type
            elif c.connection_type in self.connection_types:
                if isinstance(c.connection_type, BondType):
                    c.connection_type = self._bond_types[c.connection_type]
                if isinstance(c.connection_type, AngleType):
                    c.connection_type = self._angle_types[c.connection_type]
                if isinstance(c.connection_type, DihedralType):
                    c.connection_type = self._dihedral_types[c.connection_type]

    def update_atom_types(self):
        """Update atom types in the topology

        This method checks all the sites in the topology which have an
        associated AtomType and if that AtomType is not in the topology's
        AtomTypes collection, it will add it there.

        See Also:
        ---------
        gmso.Topology.update_connection_types :
            Update the connection types based on the connection collection in the topology
        """
        for site in self._sites:
            if site.atom_type is None:
                warnings.warn('Non-parametrized site detected {}'.format(site))
            elif not isinstance(site.atom_type, AtomType):
                raise GMSOError('Non AtomType instance found in site {}'.format(site))
            elif site.atom_type not in self._atom_types:
                site.atom_type.topology = self
                self._atom_types[site.atom_type] = site.atom_type
            elif site.atom_type in self._atom_types:
                site.atom_type = self._atom_types[site.atom_type]
        self.is_typed(updated=True)

    def add_subtopology(self, subtop):
        """Add a sub-topology to this topology

        This methods adds a gmso.Core.SubTopology object to the topology
        All the sites in this sub-topology are added to the collection of current
        sites in this topology.

        Parameters
        ----------
        subtop : gmso.SubTopology
            The sub-topology object to be added.

        See Also
        --------
        gmso.SubTopology : A topology within a topology
        """
        self._subtops.add(subtop)
        subtop.parent = self
        self._sites.union(subtop.sites)

    def is_typed(self, updated=False):
        if not updated:
            self.update_connection_types()
            self.update_atom_types()

        if len(self.atom_types) > 0 or len(self.connection_types) > 0:
            self._typed = True
        else:
            self._typed = False
        return self._typed

    def update_angle_types(self):
        """Uses gmso.Topology.update_connection_types to update AngleTypes in the topology.

        This method is an alias for gmso.Topology.update_connection_types.

        See Also
        --------
        gmso.Topology.update_connection_types :
            Update the connection types based on the connection collection in the topology.
        """
        self.update_connection_types()

    def update_bond_types(self):
        """Uses gmso.Topology.update_connection_types to update BondTypes in the topology.

        This method is an alias for gmso.Topology.update_connection_types.

        See Also
        --------
        gmso.Topology.update_connection_types :
            Update the connection types based on the connection collection in the topology.
        """
        self.update_connection_types()

    def update_dihedral_types(self):
        """Uses gmso.Topology.update_connection_types to update DihedralTypes in the topology.

        This method is an alias for gmso.Topology.update_connection_types.

        See Also
        --------
        gmso.Topology.update_connection_types :
            Update the connection types based on the connection collection in the topology.
        """
        self.update_connection_types()

    def update_topology(self):
        """Update the entire topology"""
        self.update_sites()
        self.update_connections()
        self.update_atom_types()
        self.update_connection_types()
        self.is_typed(updated=True)

    def __repr__(self):
        descr = list('<')
        descr.append(self.name + ' ')
        descr.append('{:d} sites, '.format(self.n_sites))
        descr.append('{:d} connections, '.format(self.n_connections))
        descr.append('id: {}>'.format(id(self)))

        return ''.join(descr)


