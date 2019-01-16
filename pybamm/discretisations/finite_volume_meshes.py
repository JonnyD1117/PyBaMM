#
# Mesh class for space and time discretisation
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals
import pybamm

import numpy as np


class FiniteVolumeMacroMesh(pybamm.BaseMesh):
    """A Finite Volumes mesh for the 1D macroscale.

    **Extends**: :class:`BaseMesh`

    """

    def __init__(self, param, target_npts=10, tsteps=100, tend=1):

        super().__init__(param, target_npts, tsteps, tend)

        # submesh class
        self.submeshclass = FiniteVolumeSubmesh

        # Space (macro)
        Ln, Ls, Lp = param["Ln"], param["Ls"], param["Lp"]
        L = Ln + Ls + Lp
        ln, ls, lp = Ln / L, Ls / L, Lp / L
        # We aim to create the grid as uniformly as possible
        targetmeshsize = min(ln, ls, lp) / target_npts

        # Negative electrode
        self.neg_mesh_points = round(ln / targetmeshsize) + 1
        self["negative electrode"] = self.submeshclass(
            np.linspace(0.0, ln, self.neg_mesh_points)
        )

        # Separator
        self.sep_mesh_points = round(ls / targetmeshsize) + 1
        self["separator"] = self.submeshclass(
            np.linspace(ln, ln + ls, self.sep_mesh_points)
        )

        # Positive electrode
        self.pos_mesh_points = round(lp / targetmeshsize) + 1
        self["positive electrode"] = self.submeshclass(
            np.linspace(ln + ls, 1.0, self.pos_mesh_points)
        )

        # Whole cell
        self.total_mesh_points = (
            self.neg_mesh_points + (self.sep_mesh_points - 2) + self.pos_mesh_points
        )
        self["whole cell"] = self.submeshclass(
            np.concatenate(
                [
                    self["negative electrode"].edges,
                    self["separator"].edges[1:-1],
                    self["positive electrode"].edges,
                ]
            )
        )


class FiniteVolumeSubmesh:
    """A submesh for finite volumes.

    The mesh is defined by its edges; then node positions, diffs and mesh size are
    calculated from the edge positions.

    Parameters
    ----------
    edges : :class:`numpy.array`
        The position of the edges of the cells

    """

    def __init__(self, edges):
        self.edges = edges
        self.nodes = (self.edges[1:] + self.edges[:-1]) / 2
        self.d_edges = np.diff(self.edges)
        self.d_nodes = np.diff(self.nodes)
        self.npts = self.nodes.size