import unittest
import os
from symfit import Fit, Eq
from test.testcase import ArrayTestCase
from colicoords import CellFit, load
from colicoords.minimizers import *


class TestCellFitting(ArrayTestCase):
    def setUp(self):
        f_path = os.path.dirname(os.path.realpath(__file__))
        self.cells = load(os.path.join(f_path, 'test_data', 'test_cells.hdf5'))

    def test_fitting_binary(self):
        resdict = {'a0': 2.004259e+01, 'a1': -2.571423e-01, 'a2': 4.944874e-03,
                   'r': 9.096484e+00, 'xl': 1.552373e+01, 'xr': 3.613869e+01}

        cell_0 = self.cells[0].copy()
        res = cell_0.optimize()
        self.assertEqual(res.objective_value, 30)
        for key, val in resdict.items():
            self.assertAlmostEqual(res.params[key], val, 5)

        cell_0 = self.cells[0].copy()
        res = cell_0.optimize(minimizer=Powell)
        self.assertEqual(res.objective_value, 30)
        for key, val in resdict.items():
            self.assertAlmostEqual(res.params[key], val, 5)

        cell_0 = self.cells[0].copy()
        res = cell_0.optimize(minimizer=DifferentialEvolution)

        self.assertLessEqual(res.objective_value, 25)

    def test_fitting_brightfield(self):
        res_dict = {'a0': 2.059920e+01, 'a1': -2.712269e-01, 'a2': 5.158162e-03,
                    'r': 9.248204e+00, 'xl': 1.522411e+01, 'xr': 3.645077e+01}

        cell_0 = self.cells[0].copy()
        res = cell_0.optimize('brightfield')
        self.assertEqual(res.objective_value, 10016887.123816863)
        for key, val in res_dict.items():
            self.assertAlmostEqual(res.params[key], val, 5)

        cell_0 = self.cells[0].copy()
        res = cell_0.optimize('brightfield', minimizer=Powell)
        self.assertEqual(res.objective_value, 10016887.123816863)
        for key, val in res_dict.items():
            self.assertAlmostEqual(res.params[key], val, 5)

        cell_0 = self.cells[0].copy()
        res_dict = {'a0': 1.780838e+01, 'a1': -3.784501e-02, 'a2':7.301865e-04,
                    'r': 9.244447e+00,'xl': 1.516948e+01, 'xr': 3.650385e+01}
        deltas = {'a0': 0.5, 'a1': 1e-2, 'a2':1e-3,
            'r': 0.05,'xl': 1e-2, 'xr': 1e-2}
        res = cell_0.optimize('brightfield', minimizer=DifferentialEvolution)
        self.assertLessEqual(res.objective_value, 8185000)
        for k, v in res_dict.items():
            self.assertAlmostEqual(v, res.params[k], delta=deltas[k])

    def test_cell_list_optimize(self):
        cells = self.cells[:8].copy()
        res_list = cells.optimize()

        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [30, 25, 26, 25, 26, 22, 37, 17]
        for r, val in zip(res_list, obj_values):
            self.assertEqual(r.objective_value, val)

        cells = self.cells[:8].copy()
        res_list = cells.optimize(minimizer=Powell)

        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [30, 25, 26, 25, 26, 22, 37, 17]
        for r, val in zip(res_list, obj_values):
            self.assertEqual(r.objective_value, val)

    def test_cell_list_optimize_pertubation(self):
        cells = self.cells[:8].copy()
        for cell in cells:
            cell.coords.xl -= 3
            cell.coords.xr += 3
            cell.coords.a0 *= 0.95
            cell.coords.a1 *= 1.05

        res_list = cells.optimize(minimizer=Powell)

        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [28, 26, 24, 53, 31, 20, 46, 11]
        for r, val in zip(res_list, obj_values):
            self.assertEqual(r.objective_value, val)

    def test_multiprocessing(self):
        cells = self.cells[:8].copy()
        res_list = cells.optimize_mp()

        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [30, 25, 26, 25, 26, 22, 37, 17]
        for r, val in zip(res_list, obj_values):
            self.assertEqual(r.objective_value, val)

        cells = self.cells[:8].copy()
        res_list = cells.optimize_mp(minimizer=Powell)

        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [30, 25, 26, 25, 26, 22, 37, 17]
        for r, val in zip(res_list, obj_values):
            self.assertEqual(r.objective_value, val)

    def test_multiprocessing_brightfield(self):
        cells = self.cells[:8].copy()
        res_list = cells.optimize_mp('brightfield')
        print([r.objective_value for r in res_list])

        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [10016887.123816863, 23617786.697511297, 8999333.084250152, 29339637.49970112,
                      62892422.65259473, 20011819.287397716, 33025293.172053672, 112600585.34296474]

        for r, val in zip(res_list, obj_values):
            self.assertAlmostEqual(r.objective_value, val, 5)

        cells = self.cells[:4].copy()
        res_list = cells.optimize_mp(minimizer=DifferentialEvolution)
        print([r.objective_value for r in res_list]) #[23.0, 17.0, 18.0, 22.0, 16.0, 17.0, 25.0, 10.0]
        #
        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [23.0, 17.0, 18.0, 22.0]
        for r, val in zip(res_list, obj_values):
            self.assertLessEqual(r.objective_value, val + 3)

    def test_temp(self):
        cells = self.cells[:4].copy()
        #perturb inital coordinate guesses
        for cell in cells:
            cell.coords.xl -= 3
            cell.coords.xr += 3
            cell.coords.a0 *= 0.9
            cell.coords.a1 *= 1.05

        res_list = cells.optimize_mp(minimizer=DifferentialEvolution)

        # Check if the result has been properly substituted in all cell objects
        for r, cell in zip(res_list, cells):
            for k, v in r.params.items():
                self.assertEqual(v, getattr(cell.coords, k))

        obj_values = [23.0, 17.0, 18.0, 22.0]
        for r, val in zip(res_list, obj_values):
            self.assertLessEqual(r.objective_value, val + 3)


if __name__ == '__main__':
    unittest.main()