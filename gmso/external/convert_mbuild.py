from warnings import warn

import numpy as np
import unyt as u

from gmso.core.topology import Topology
from gmso.core.subtopology import SubTopology
from gmso.core.site import Site
from gmso.core.bond import Bond
from gmso.core.box import Box
from gmso.utils.io import has_mbuild
from gmso.core.element import (element_by_symbol,
                                   element_by_name,
                                   element_by_atomic_number,
                                   element_by_mass)

if has_mbuild:
    import mbuild as mb


def from_mbuild(compound, box=None, search_method=element_by_symbol):
    """Convert an mbuild.Compound to a gmso.Topology

    Parameters
    ----------
    compound : mbuild.Compound
        mbuild.Compound instance that need to be converted
    box : mbuild.Box, optional, default=None
        Box information to be loaded to a gmso.Topologly
    search_method : element_by_symbol, element_by_name,
                    element_by_atomic_number, element_by_mass,
                    optional, default=element_by_symbol
        Searching method used to assign element from periodic table to particle site

    Returns
    -------
    top : gmso.Topology
    """
    msg = ("Provided argument that is not an mbuild Compound")
    assert isinstance(compound, mb.Compound), msg

    top = Topology()
    top.typed = False

    # Keep the name if it is not the default mbuild Compound name
    if compound.name != mb.Compound().name:
        top.name = compound.name

    site_map = dict()
    for child in compound.children:
        if len(child.children) == 0:
            continue
        else:
            subtop = SubTopology(name=child.name)
            top.add_subtopology(subtop)
            for particle in child.particles():
                pos = particle.xyz[0] * u.nanometer
                ele = search_method(particle.name)
                site = Site(name=particle.name, position=pos, element=ele)
                site_map[particle] = site
                subtop.add_site(site)
    top.update_topology()

    for particle in compound.particles():
        already_added_site = site_map.get(particle, None)
        if already_added_site:
            continue

        pos = particle.xyz[0] * u.nanometer
        ele = search_method(particle.name)
        site = Site(name=particle.name, position=pos, element=ele)
        site_map[particle] = site

        # If the top has subtopologies, then place this particle into
        # a single-site subtopology -- ensures that all sites are in the
        # same level of hierarchy.
        if len(top.subtops) > 0:
            subtop = SubTopology(name=particle.name)
            top.add_subtopology(subtop)
            subtop.add_site(site)
        else:
            top.add_site(site)

    for b1, b2 in compound.bonds():
        new_bond = Bond(connection_members=[site_map[b1], site_map[b2]],
                connection_type=None)
        top.add_connection(new_bond)
    top.update_topology()

    if box:
        top.box = from_mbuild_box(box)
    # Assumes 2-D systems are not supported in mBuild
    # if compound.periodicity is None and not box:
    else:
        if np.allclose(compound.periodicity, np.zeros(3)):
            box = from_mbuild_box(compound.boundingbox)
            if box:
                box.lengths += [0.5, 0.5, 0.5] * u.nm
            top.box = box
        else:
            top.box = Box(lengths=compound.periodicity)

    return top


def to_mbuild(topology):
    """ Convert a gmso.Topology to mbuild.Compound

    Parameters
    ----------
    topology : gmso.Topology
        topology instance that need to be converted

    Returns:
    --------
    compound : mbuild.Compound
    """
    msg = ("Provided argument that is not a topology")
    assert isinstance(topology, Topology), msg

    compound = mb.Compound()
    if topology.name is None:
        compound.name = 'Compound'
    else:
        compound.name = topology.name

    particle_map = dict()
    for site in topology.sites:
        particle = mb.Compound(name=site.name, pos=site.position[0])
        particle_map[site] = particle
        compound.add(particle)

    for connect in topology.connections:
        if isinstance(connect, Bond):
            compound.add_bond((
                particle_map[connect.connection_members[0]],
                particle_map[connect.connection_members[1]]))

    return compound

def from_mbuild_box(mb_box):
    """Convert an mBuild box to a gmso.box.Box"""
    # TODO: Unit tests

    if not isinstance(mb_box, mb.Box):
        raise ValueError('Argument mb_box is not an mBuild Box')

    if np.allclose(mb_box.lengths, [0, 0, 0]):
        warn(
            'No box or boundingbox information detected, setting box to None'
        )
        return None

    box = Box(
        lengths=np.asarray(mb_box.lengths)*u.nm,
        angles=np.asarray(mb_box.angles)*u.degree,
    )

    return box