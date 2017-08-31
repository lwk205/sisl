from __future__ import print_function, division

import pytest

import math as m
import numpy as np

import sisl._numpy_scipy as ns_
from sisl import SuperCell, SuperCellChild
from sisl.geom import graphene


@pytest.fixture
def setup():
    class t():
        def __init__(self):
            alat = 1.42
            sq3h = 3.**.5 * 0.5
            self.sc = SuperCell(np.array([[1.5, sq3h, 0.],
                                          [1.5, -sq3h, 0.],
                                          [0., 0., 10.]], np.float64) * alat, nsc=[3, 3, 1])
    return t()


@pytest.mark.supercell
@pytest.mark.sc
class TestSuperCell(object):

    def test_repr(self, setup):
        repr(setup.sc)
        str(setup.sc)
        assert setup.sc != 'Not a SuperCell'

    def test_nsc1(self, setup):
        sc = setup.sc.copy()
        sc.set_nsc([5, 5, 0])
        assert np.allclose([5, 5, 1], sc.nsc)
        assert len(sc.sc_off) == np.prod(sc.nsc)

    def test_nsc2(self, setup):
        sc = setup.sc.copy()
        sc.set_nsc([0, 1, 0])
        assert np.allclose([1, 1, 1], sc.nsc)
        assert len(sc.sc_off) == np.prod(sc.nsc)
        sc.set_nsc(a=3)
        assert np.allclose([3, 1, 1], sc.nsc)
        assert len(sc.sc_off) == np.prod(sc.nsc)
        sc.set_nsc(b=3)
        assert np.allclose([3, 3, 1], sc.nsc)
        assert len(sc.sc_off) == np.prod(sc.nsc)
        sc.set_nsc(c=5)
        assert np.allclose([3, 3, 5], sc.nsc)
        assert len(sc.sc_off) == np.prod(sc.nsc)

    def test_nsc3(self, setup):
        assert setup.sc.sc_index([0, 0, 0]) == 0
        for s in range(setup.sc.n_s):
            assert setup.sc.sc_index(setup.sc.sc_off[s, :]) == s
        arng = np.arange(setup.sc.n_s)
        np.random.shuffle(arng)
        sc_off = setup.sc.sc_off[arng, :]
        assert np.all(setup.sc.sc_index(sc_off) == arng)

    @pytest.mark.xfail(raises=ValueError)
    def test_nsc4(self, setup):
        setup.sc.set_nsc(a=2)

    @pytest.mark.xfail(raises=ValueError)
    def test_nsc5(self, setup):
        setup.sc.set_nsc([1, 2, 3])

    def test_fill(self, setup):
        sc = setup.sc.swapaxes(1, 2)
        i = sc._fill([1, 1])
        assert i.dtype == np.int32
        i = sc._fill([1., 1.])
        assert i.dtype == np.float64
        for dt in [np.int32, np.int64, np.float32, np.float64, np.complex64]:
            i = sc._fill([1., 1.], dt)
            assert i.dtype == dt
            i = sc._fill(np.ones([2], dt))
            assert i.dtype == dt

    def test_add_vacuum1(self, setup):
        sc = setup.sc.copy()
        for i in range(3):
            s = sc.add_vacuum(10, i)
            ax = setup.sc.cell[i, :]
            ax += ax / np.sum(ax ** 2) ** .5 * 10
            assert np.allclose(ax, s.cell[i, :])

    def test_rotation1(self, setup):
        rot = setup.sc.rotate(180, [0, 0, 1])
        rot.cell[2, 2] *= -1
        assert np.allclose(-rot.cell, setup.sc.cell)

        rot = setup.sc.rotate(m.pi, [0, 0, 1], radians=True)
        rot.cell[2, 2] *= -1
        assert np.allclose(-rot.cell, setup.sc.cell)

        rot = rot.rotate(180, [0, 0, 1])
        rot.cell[2, 2] *= -1
        assert np.allclose(rot.cell, setup.sc.cell)

    def test_rotation2(self, setup):
        rot = setup.sc.rotatec(180)
        rot.cell[2, 2] *= -1
        assert np.allclose(-rot.cell, setup.sc.cell)

        rot = setup.sc.rotatec(m.pi, radians=True)
        rot.cell[2, 2] *= -1
        assert np.allclose(-rot.cell, setup.sc.cell)

        rot = rot.rotatec(180)
        rot.cell[2, 2] *= -1
        assert np.allclose(rot.cell, setup.sc.cell)

    def test_rotation3(self, setup):
        rot = setup.sc.rotatea(180)
        assert np.allclose(rot.cell[0, :], setup.sc.cell[0, :])
        assert np.allclose(-rot.cell[2, 2], setup.sc.cell[2, 2])

        rot = setup.sc.rotateb(m.pi, radians=True)
        assert np.allclose(rot.cell[1, :], setup.sc.cell[1, :])
        assert np.allclose(-rot.cell[2, 2], setup.sc.cell[2, 2])

    def test_swapaxes1(self, setup):
        sab = setup.sc.swapaxes(0, 1)
        assert np.allclose(sab.cell[0, :], setup.sc.cell[1, :])
        assert np.allclose(sab.cell[1, :], setup.sc.cell[0, :])

    def test_swapaxes2(self, setup):
        sab = setup.sc.swapaxes(0, 2)
        assert np.allclose(sab.cell[0, :], setup.sc.cell[2, :])
        assert np.allclose(sab.cell[2, :], setup.sc.cell[0, :])

    def test_swapaxes3(self, setup):
        sab = setup.sc.swapaxes(1, 2)
        assert np.allclose(sab.cell[1, :], setup.sc.cell[2, :])
        assert np.allclose(sab.cell[2, :], setup.sc.cell[1, :])

    def test_offset1(self, setup):
        off = setup.sc.offset()
        assert np.allclose(off, [0, 0, 0])
        off = setup.sc.offset([1, 1, 1])
        cell = setup.sc.cell[:, :]
        assert np.allclose(off, cell[0, :] + cell[1, :] + cell[2, :])

    def test_sc_index1(self, setup):
        sc_index = setup.sc.sc_index([0, 0, 0])
        assert sc_index == 0
        sc_index = setup.sc.sc_index([0, 0, None])
        assert len(sc_index) == setup.sc.nsc[2]

    def test_sc_index2(self, setup):
        sc_index = setup.sc.sc_index([[0, 0, 0],
                                     [1, 1, 0]])
        assert len(sc_index) == 2

    @pytest.mark.xfail(raises=Exception)
    def test_sc_index3(self, setup):
        setup.sc.sc_index([100, 100, 100])

    def test_cut1(self, setup):
        cut = setup.sc.cut(2, 0)
        assert np.allclose(cut.cell[0, :] * 2, setup.sc.cell[0, :])
        assert np.allclose(cut.cell[1, :], setup.sc.cell[1, :])

    def test_creation1(self, setup):
        # full cell
        tmp1 = SuperCell([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        # diagonal cell
        tmp2 = SuperCell([1, 1, 1])
        # cell parameters
        tmp3 = SuperCell([1, 1, 1, 90, 90, 90])
        tmp4 = SuperCell([1])
        assert np.allclose(tmp1.cell, tmp2.cell)
        assert np.allclose(tmp1.cell, tmp3.cell)
        assert np.allclose(tmp1.cell, tmp4.cell)

    def test_creation2(self, setup):
        # full cell
        class P(SuperCellChild):

            def copy(self):
                a = P()
                a.set_supercell(setup.sc)
                return a
        tmp1 = P()
        tmp1.set_supercell([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        # diagonal cell
        tmp2 = P()
        tmp2.set_supercell([1, 1, 1])
        # cell parameters
        tmp3 = P()
        tmp3.set_supercell([1, 1, 1, 90, 90, 90])
        tmp4 = P()
        tmp4.set_supercell([1])
        assert np.allclose(tmp1.cell, tmp2.cell)
        assert np.allclose(tmp1.cell, tmp3.cell)
        assert np.allclose(tmp1.cell, tmp4.cell)
        assert len(tmp1._fill([0, 0, 0])) == 3
        assert len(tmp1._fill_sc([0, 0, 0])) == 3
        assert tmp1.is_orthogonal()
        for i in range(3):
            t2 = tmp2.add_vacuum(10, i)
            assert tmp1.cell[i, i] + 10 == t2.cell[i, i]

    @pytest.mark.xfail(raises=ValueError)
    def test_creation3(self, setup):
        setup.sc.tocell([3, 6])

    @pytest.mark.xfail(raises=ValueError)
    def test_creation4(self, setup):
        setup.sc.tocell([3, 4, 5, 6])

    @pytest.mark.xfail(raises=ValueError)
    def test_creation5(self, setup):
        setup.sc.tocell([3, 4, 5, 6, 7, 6, 7])

    def test_rcell(self, setup):
        # LAPACK inverse algorithm implicitly does
        # a transpose.
        rcell = ns_.inv(setup.sc.cell) * 2. * np.pi
        assert np.allclose(rcell.T, setup.sc.rcell)

    def test_translate1(self, setup):
        sc = setup.sc.translate([0, 0, 10])
        assert np.allclose(sc.cell[2, :2], setup.sc.cell[2, :2])
        assert np.allclose(sc.cell[2, 2], setup.sc.cell[2, 2]+10)

    def test_center1(self, setup):
        assert np.allclose(setup.sc.center(), np.sum(setup.sc.cell, axis=0) / 2)
        for i in [0, 1, 2]:
            assert np.allclose(setup.sc.center(i), setup.sc.cell[i, :] / 2)

    def test_pickle(self, setup):
        import pickle as p
        s = p.dumps(setup.sc)
        n = p.loads(s)
        assert setup.sc == n
        s = SuperCell([1, 1, 1])
        assert setup.sc != s

    def test_orthogonal(self, setup):
        assert not setup.sc.is_orthogonal()

    def test_fit1(self, setup):
        g = graphene()
        gbig = g.repeat(40, 0).repeat(40, 1)
        gbig.xyz[:, :] += (np.random.rand(len(gbig), 3) - 0.5) * 0.01
        sc = g.sc.fit(gbig)
        assert np.allclose(sc.cell, gbig.cell)

    def test_fit2(self, setup):
        g = graphene(orthogonal=True)
        gbig = g.repeat(40, 0).repeat(40, 1)
        gbig.xyz[:, :] += (np.random.rand(len(gbig), 3) - 0.5) * 0.01
        sc = g.sc.fit(gbig)
        assert np.allclose(sc.cell, gbig.cell)

    def test_fit3(self, setup):
        g = graphene(orthogonal=True)
        gbig = g.repeat(40, 0).repeat(40, 1)
        gbig.xyz[:, :] += (np.random.rand(len(gbig), 3) - 0.5) * 0.01
        sc = g.sc.fit(gbig, axis=0)
        assert np.allclose(sc.cell[0, :], gbig.cell[0, :])
        assert np.allclose(sc.cell[1:, :], g.cell[1:, :])

    def test_fit4(self, setup):
        g = graphene(orthogonal=True)
        gbig = g.repeat(40, 0).repeat(40, 1)
        gbig.xyz[:, :] += (np.random.rand(len(gbig), 3) - 0.5) * 0.01
        sc = g.sc.fit(gbig, axis=[0, 1])
        assert np.allclose(sc.cell[0:2, :], gbig.cell[0:2, :])
        assert np.allclose(sc.cell[2, :], g.cell[2, :])

    def test_parallel1(self, setup):
        g = graphene(orthogonal=True)
        gbig = g.repeat(40, 0).repeat(40, 1)
        assert g.sc.parallel(gbig.sc)
        assert gbig.sc.parallel(g.sc)
        g = g.rotatea(90)
        assert not g.sc.parallel(gbig.sc)
