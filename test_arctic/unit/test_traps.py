import numpy as np
import pytest
from scipy import integrate
import matplotlib.pyplot as plt

import arctic as ac


class TestTrapParams:
    def test__parallel_x1__serial_x1_trap___sets_value_correctly(self):

        parallel_trap_0 = ac.Trap(density=0.1, lifetime=1.0)
        parallel_trap_1 = ac.Trap(density=0.2, lifetime=2.0)

        serial_trap_0 = ac.Trap(density=0.3, lifetime=3.0)
        serial_trap_1 = ac.Trap(density=0.4, lifetime=4.0)

        assert parallel_trap_0.density == 0.1
        assert parallel_trap_0.lifetime == 1.0
        assert parallel_trap_1.density == 0.2
        assert parallel_trap_1.lifetime == 2.0

        assert serial_trap_0.density == 0.3
        assert serial_trap_0.lifetime == 3.0
        assert serial_trap_1.density == 0.4
        assert serial_trap_1.lifetime == 4.0

    def test__ccd_volume_class___sets_value_correctly(self):

        parallel_ccd_volume = ac.CCDVolumeComplex(
            well_max_height=10000.0,
            well_notch_depth=0.01,
            well_fill_alpha=0.2,
            well_fill_beta=0.8,
        )

        serial_ccd_volume = ac.CCDVolumeComplex(
            well_max_height=1000.0,
            well_notch_depth=1.02,
            well_fill_alpha=1.1,
            well_fill_beta=1.4,
        )

        assert parallel_ccd_volume.well_max_height == 10000.0
        assert parallel_ccd_volume.well_notch_depth == 0.01
        assert parallel_ccd_volume.well_range == 9999.99
        assert parallel_ccd_volume.well_fill_alpha == 0.2
        assert parallel_ccd_volume.well_fill_beta == 0.8

        assert serial_ccd_volume.well_max_height == 1000.0
        assert serial_ccd_volume.well_notch_depth == 1.02
        assert serial_ccd_volume.well_range == 998.98
        assert serial_ccd_volume.well_fill_alpha == 1.1
        assert serial_ccd_volume.well_fill_beta == 1.4


class TestSpecies:
    def test__electrons_released_from_electrons_and_time(self):

        trap = ac.Trap(lifetime=1.0)

        assert trap.electrons_released_from_electrons_and_time(
            electrons=1.0
        ) == pytest.approx(0.6321, 1.0e-4)
        assert trap.electrons_released_from_electrons_and_time(
            electrons=2.0
        ) == pytest.approx(2.0 * 0.6321, 1.0e-4)

        trap = ac.Trap(lifetime=2.0)

        assert trap.electrons_released_from_electrons_and_time(
            electrons=1.0
        ) == pytest.approx(0.39346, 1.0e-4)
        assert trap.electrons_released_from_electrons_and_time(
            electrons=2.0
        ) == pytest.approx(2.0 * 0.39346, 1.0e-4)

    def test__delta_ellipticity_of_trap(self):

        trap = ac.Trap(density=0.5, lifetime=2.0)

        assert trap.delta_ellipticity == pytest.approx(0.047378295117617694, 1.0e-5)

    def test__delta_ellipticity_of_arctic_params(self):

        parallel_1_trap = ac.Trap(density=0.1, lifetime=4.0)
        parallel_2_trap = ac.Trap(density=0.1, lifetime=4.0)
        serial_1_trap = ac.Trap(density=0.2, lifetime=2.0)
        serial_2_trap = ac.Trap(density=0.7, lifetime=7.0)

        trap_manager = ac.TrapManager(traps=[parallel_1_trap], rows=1)
        assert trap_manager.delta_ellipticity == parallel_1_trap.delta_ellipticity

        trap_manager = ac.TrapManager(traps=[parallel_1_trap, parallel_2_trap], rows=1)
        assert (
            trap_manager.delta_ellipticity
            == parallel_1_trap.delta_ellipticity + parallel_2_trap.delta_ellipticity
        )

        trap_manager = ac.TrapManager(traps=[serial_1_trap], rows=1)
        assert trap_manager.delta_ellipticity == serial_1_trap.delta_ellipticity

        trap_manager = ac.TrapManager(traps=[serial_1_trap, serial_2_trap], rows=1)
        assert (
            trap_manager.delta_ellipticity
            == serial_1_trap.delta_ellipticity + serial_2_trap.delta_ellipticity
        )

        trap_manager = ac.TrapManager(
            traps=[parallel_1_trap, parallel_2_trap, serial_1_trap, serial_2_trap],
            rows=1,
        )

        assert trap_manager.delta_ellipticity == pytest.approx(
            parallel_1_trap.delta_ellipticity
            + parallel_2_trap.delta_ellipticity
            + serial_1_trap.delta_ellipticity
            + serial_2_trap.delta_ellipticity,
            1.0e-6,
        )


class TestParallelDensityVary:
    def test_1_trap__density_01__1000_column_pixels__1_row_pixel_so_100_traps__poisson_density_near_01(
        self,
    ):  #

        parallel_vary = ac.Trap.poisson_trap(
            trap=list(
                map(lambda density: ac.Trap(density=density, lifetime=1.0), (0.1,),)
            ),
            shape=(1000, 1),
            seed=1,
        )

        assert [trap.density for trap in parallel_vary] == [0.098]

    def test__1_trap__density_1__1000_column_pixels_so_1000_traps__1_row_pixel__poisson_value_is_near_1(
        self,
    ):
        parallel_vary = ac.Trap.poisson_trap(
            trap=list(
                map(lambda density: ac.Trap(density=density, lifetime=1.0), (1.0,),)
            ),
            shape=(1000, 1),
            seed=1,
        )

        assert [trap.density for trap in parallel_vary] == [0.992]

    def test__1_trap__density_1___2_row_pixels__poisson_value_is_near_1(self):
        parallel_vary = ac.Trap.poisson_trap(
            trap=list(
                map(lambda density: ac.Trap(density=density, lifetime=1.0), (1.0,),)
            ),
            shape=(1000, 2),
            seed=1,
        )

        assert [trap.density for trap in parallel_vary] == [0.992, 0.962]

    def test__2_trap__1_row_pixel__poisson_for_each_trap_drawn(self):
        parallel_vary = ac.Trap.poisson_trap(
            trap=list(
                map(lambda density: ac.Trap(density=density, lifetime=1.0), (1.0, 2.0),)
            ),
            shape=(1000, 1),
            seed=1,
        )

        assert [trap.density for trap in parallel_vary] == [0.992, 1.946]

    def test__2_trap__2_row_pixel__poisson_for_each_trap_drawn(self):
        parallel_vary = ac.Trap.poisson_trap(
            trap=list(
                map(lambda density: ac.Trap(density=density, lifetime=1.0), (1.0, 2.0),)
            ),
            shape=(1000, 2),
            seed=1,
        )

        assert [trap.density for trap in parallel_vary] == [
            0.992,
            1.946,
            0.968,
            1.987,
        ]

    def test__same_as_above_but_3_trap_and_new_values(self):
        parallel_vary = ac.Trap.poisson_trap(
            trap=list(
                map(
                    lambda density: ac.Trap(density=density, lifetime=1.0),
                    (1.0, 2.0, 0.1),
                )
            ),
            shape=(1000, 3),
            seed=1,
        )

        assert [trap.density for trap in parallel_vary] == [
            0.992,
            1.946,
            0.09,
            0.991,
            1.99,
            0.098,
            0.961,
            1.975,
            0.113,
        ]


class TestInitialWatermarks:
    def test__initial_watermark_array__uses_rows_and_total_traps_to_set_size(self,):
        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = trap_manager.initial_watermarks_from_rows_and_total_traps(
            rows=3, total_traps=1
        )

        assert (watermarks == np.zeros(shape=(3, 2))).all()

        watermarks = trap_manager.initial_watermarks_from_rows_and_total_traps(
            rows=3, total_traps=5
        )

        assert (watermarks == np.zeros(shape=(3, 6))).all()

        watermarks = trap_manager.initial_watermarks_from_rows_and_total_traps(
            rows=5, total_traps=2
        )

        assert (watermarks == np.zeros(shape=(5, 3))).all()


class TestElectronsReleasedAndUpdatedWatermarks:
    def test__empty_release(self):

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        electrons_released = trap_manager.electrons_released_in_pixel()

        assert electrons_released == pytest.approx(0)
        assert trap_manager.watermarks == pytest.approx(
            np.array([[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
        )

    def test__single_trap(self):

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )

        electrons_released = trap_manager.electrons_released_in_pixel()

        assert electrons_released == pytest.approx(2.5)
        assert trap_manager.watermarks == pytest.approx(
            np.array([[0.5, 0.4], [0.2, 0.2], [0.1, 0.1], [0, 0], [0, 0], [0, 0]])
        )

    def test__multiple_traps(self):

        traps = [
            ac.Trap(density=10, lifetime=-1 / np.log(0.5)),
            ac.Trap(density=8, lifetime=-1 / np.log(0.2)),
        ]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [
                [0.5, 0.8, 0.3],
                [0.2, 0.4, 0.2],
                [0.1, 0.2, 0.1],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        )

        electrons_released = trap_manager.electrons_released_in_pixel()

        assert electrons_released == pytest.approx(2.5 + 1.28)
        assert trap_manager.watermarks == pytest.approx(
            np.array(
                [
                    [0.5, 0.4, 0.06],
                    [0.2, 0.2, 0.04],
                    [0.1, 0.1, 0.02],
                    [0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0],
                ]
            )
        )

    def test__single_trap__change_time(self):

        # Half the time, half the liftime --> same result
        traps = [ac.Trap(density=10, lifetime=-0.5 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )

        electrons_released = trap_manager.electrons_released_in_pixel(time=0.5)

        assert electrons_released == pytest.approx(2.5)
        assert trap_manager.watermarks == pytest.approx(
            np.array([[0.5, 0.4], [0.2, 0.2], [0.1, 0.1], [0, 0], [0, 0], [0, 0]])
        )

    def test__single_trap__change_width(self):

        # Half the time, double the density --> same result
        traps = [ac.Trap(density=20, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )

        electrons_released = trap_manager.electrons_released_in_pixel(width=0.5)

        assert electrons_released == pytest.approx(2.5)
        assert trap_manager.watermarks == pytest.approx(
            np.array([[0.5, 0.4], [0.2, 0.2], [0.1, 0.1], [0, 0], [0, 0], [0, 0]])
        )


class TestElectronsCapturedByTraps:
    def test__first_capture(self):

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        electron_fractional_height = 0.5

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx(0.5 * 10)

    def test__new_highest_watermark(self):

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.9

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx((0.1 + 0.12 + 0.07 + 0.1) * 10)

    def test__middle_new_watermarks(self):

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.6

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx((0.1 + 0.06) * 10)

        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.75

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx((0.1 + 0.12 + 0.035) * 10)

    def test__new_lowest_watermark(self):

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.3

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx(0.3 * 0.2 * 10)

    def test__multiple_traps(self):

        traps = [
            ac.Trap(density=10, lifetime=-1 / np.log(0.5)),
            ac.Trap(density=8, lifetime=-1 / np.log(0.2)),
        ]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [
                [0.5, 0.8, 0.7],
                [0.2, 0.4, 0.3],
                [0.1, 0.3, 0.2],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        )

        electron_fractional_height = 0.6

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx(
            (0.1 + 0.06) * 10 + (0.15 + 0.07) * 8
        )


class TestUpdateWatermarks:
    def test__first_capture(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = trap_manager.initial_watermarks_from_rows_and_total_traps(
            rows=6, total_traps=1
        )
        electron_fractional_height = 0.5

        watermarks = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
        )

        assert watermarks == pytest.approx(
            np.array([[0.5, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
        )

    def test__new_highest_watermark(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.9

        watermarks = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
        )

        assert watermarks == pytest.approx(
            np.array([[0.9, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
        )

    def test__middle_new_watermark(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.6

        watermarks = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
        )

        assert watermarks == pytest.approx(
            np.array([[0.6, 1], [0.1, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]])
        )

        watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.75

        watermarks = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
        )

        assert watermarks == pytest.approx(
            np.array([[0.75, 1], [0.05, 0.3], [0, 0], [0, 0], [0, 0], [0, 0]])
        )

    def test__new_lowest_watermark(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.3

        watermarks = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
        )

        assert watermarks == pytest.approx(
            np.array([[0.3, 1], [0.2, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0]])
        )

    def test__multiple_traps(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array(
            [
                [0.5, 0.8, 0.7, 0.6],
                [0.2, 0.4, 0.3, 0.2],
                [0.1, 0.3, 0.2, 0.1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ]
        )
        electron_fractional_height = 0.6

        watermarks = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
        )

        assert watermarks == pytest.approx(
            np.array(
                [
                    [0.6, 1, 1, 1],
                    [0.1, 0.4, 0.3, 0.2],
                    [0.1, 0.3, 0.2, 0.1],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                ]
            )
        )


class TestUpdateWatermarksNotEnough:
    def test__first_capture(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        electron_fractional_height = 0.5
        enough = 0.7

        watermarks = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            enough=enough,
        )
        print(watermarks)  ###
        assert watermarks == pytest.approx(
            np.array([[0.5, 0.7], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
        )

    def test__new_highest_watermark(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array([[0.5, 0.8], [0.2, 0.4], [0, 0], [0, 0], [0, 0], [0, 0]])

        electron_fractional_height = 0.8
        enough = 0.5

        watermarks = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
            enough=enough,
        )

        assert watermarks == pytest.approx(
            np.array([[0.5, 0.9], [0.2, 0.7], [0.1, 0.5], [0, 0], [0, 0], [0, 0]])
        )

    def test__new_middle_watermark(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )

        electron_fractional_height = 0.6
        enough = 0.5

        watermarks = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
            enough=enough,
        )

        assert watermarks == pytest.approx(
            np.array([[0.5, 0.9], [0.1, 0.7], [0.1, 0.4], [0.1, 0.3], [0, 0], [0, 0]])
        )

    def test__new_lowest_watermark(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.3
        enough = 0.5

        watermarks = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
            enough=enough,
        )

        assert watermarks == pytest.approx(
            np.array([[0.3, 0.9], [0.2, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0]])
        )

    def test__multiple_traps(self):

        trap_manager = ac.TrapManager(traps=[None], rows=6)

        watermarks = np.array(
            [
                [0.5, 0.8, 0.7, 0.6],
                [0.2, 0.4, 0.3, 0.2],
                [0.1, 0.3, 0.2, 0.1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ]
        )
        electron_fractional_height = 0.6
        enough = 0.5

        watermarks = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
            enough=enough,
        )
        assert watermarks == pytest.approx(
            np.array(
                [
                    [0.5, 0.9, 0.85, 0.8],
                    [0.1, 0.7, 0.65, 0.6],
                    [0.1, 0.4, 0.3, 0.2],
                    [0.1, 0.3, 0.2, 0.1],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                ]
            )
        )


class TestElectronsCapturedInPixel:
    def test__first_capture(self):

        electrons_available = 2500  # --> electron_fractional_height = 0.5

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        ccd_volume = ac.CCDVolume(
            well_fill_beta=0.5, well_max_height=10000, well_notch_depth=1e-7
        )

        electrons_captured = trap_manager.electrons_captured_in_pixel(
            electrons_available=electrons_available, ccd_volume=ccd_volume
        )

        assert electrons_captured == pytest.approx(5)
        assert trap_manager.watermarks == pytest.approx(
            np.array([[0.5, 1], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
        )

    def test__multiple_traps(self):

        electrons_available = 3600  # --> electron_fractional_height = 0.6

        traps = [
            ac.Trap(density=10, lifetime=-1 / np.log(0.5)),
            ac.Trap(density=8, lifetime=-1 / np.log(0.2)),
        ]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [
                [0.5, 0.8, 0.7],
                [0.2, 0.4, 0.3],
                [0.1, 0.3, 0.2],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        )

        ccd_volume = ac.CCDVolume(
            well_fill_beta=0.5, well_max_height=10000, well_notch_depth=1e-7
        )

        electrons_captured = trap_manager.electrons_captured_in_pixel(
            electrons_available=electrons_available, ccd_volume=ccd_volume
        )

        assert electrons_captured == pytest.approx(
            (0.1 + 0.06) * 10 + (0.15 + 0.07) * 8
        )
        assert trap_manager.watermarks == pytest.approx(
            np.array(
                [
                    [0.6, 1, 1],
                    [0.1, 0.4, 0.3],
                    [0.1, 0.3, 0.2],
                    [0, 0, 0],
                    [0, 0, 0],
                    [0, 0, 0],
                ]
            )
        )

    def test__not_enough__first_capture(self):

        electrons_available = 2.5e-3  # --> electron_fractional_height = 4.9999e-4, enough=enough = 0.50001

        traps = [ac.Trap(density=10, lifetime=-1 / np.log(0.5))]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        ccd_volume = ac.CCDVolume(
            well_fill_beta=0.5, well_max_height=10000, well_notch_depth=1e-7
        )

        electrons_captured = trap_manager.electrons_captured_in_pixel(
            electrons_available=electrons_available, ccd_volume=ccd_volume
        )

        assert electrons_captured == pytest.approx(0.0025)
        assert trap_manager.watermarks == pytest.approx(
            np.array([[4.9999e-4, 0.50001], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]])
        )

    def test__not_enough__multiple_traps(self):

        electrons_available = 4.839e-4  # --> electron_fractional_height = 2.199545e-4, enough=enough = 0.5

        traps = [
            ac.Trap(density=10, lifetime=-1 / np.log(0.5)),
            ac.Trap(density=8, lifetime=-1 / np.log(0.2)),
        ]
        trap_manager = ac.TrapManager(traps=traps, rows=6)

        trap_manager.watermarks = np.array(
            [
                [0.5, 0.8, 0.7],
                [0.2, 0.4, 0.3],
                [0.1, 0.3, 0.2],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        )

        ccd_volume = ac.CCDVolume(
            well_fill_beta=0.5, well_max_height=10000, well_notch_depth=1e-7
        )

        electrons_captured = trap_manager.electrons_captured_in_pixel(
            electrons_available=electrons_available, ccd_volume=ccd_volume
        )

        assert electrons_captured == pytest.approx(2.199545e-4 * (0.1 * 10 + 0.15 * 8))
        assert trap_manager.watermarks == pytest.approx(
            np.array(
                [
                    [2.199545e-4, 0.9, 0.85],
                    [0.5 - 2.199545e-4, 0.8, 0.7],
                    [0.2, 0.4, 0.3],
                    [0.1, 0.3, 0.2],
                    [0, 0, 0],
                    [0, 0, 0],
                ]
            )
        )


class TestTrapManagerNonUniformHeightDistribution:
    def test__effective_non_uniform_electron_fractional_height(self):

        traps = [
            ac.TrapNonUniformHeightDistribution(
                density=10,
                lifetime=-1 / np.log(0.5),
                electron_fractional_height_min=0.95,
                electron_fractional_height_max=1,
            )
        ]
        trap_manager = ac.TrapManagerNonUniformHeightDistribution(traps=traps, rows=6,)

        assert trap_manager.effective_non_uniform_electron_fractional_height(0.9) == 0
        assert trap_manager.effective_non_uniform_electron_fractional_height(1) == 1
        assert (
            trap_manager.effective_non_uniform_electron_fractional_height(0.975) == 0.5
        )

    def test__first_capture(self):

        traps = [
            ac.TrapNonUniformHeightDistribution(
                density=10,
                lifetime=-1 / np.log(0.5),
                electron_fractional_height_min=0.95,
                electron_fractional_height_max=1,
            )
        ]
        trap_manager = ac.TrapManagerNonUniformHeightDistribution(traps=traps, rows=6,)

        electron_fractional_height = 0.5

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx(0.5 * 10)

        trap_manager = ac.TrapManagerNonUniformHeightDistribution(traps=traps, rows=6,)

        electron_fractional_height = 0.99

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx(0.99 * 10)

    def test__middle_new_watermarks(self):

        traps = [
            ac.TrapNonUniformHeightDistribution(
                density=10,
                lifetime=-1 / np.log(0.5),
                electron_fractional_height_min=0.95,
                electron_fractional_height_max=1,
            )
        ]
        trap_manager = ac.TrapManagerNonUniformHeightDistribution(traps=traps, rows=6,)

        trap_manager.watermarks = np.array(
            [[0.96, 0.8], [0.98, 0.4], [0.99, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.97

        electrons_captured = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured == pytest.approx((0.96 * 0.2 + 0.01 * 0.6) * 10)


class TestTrapManagerTrackTime:
    def test__fill_fraction_from_time_elapsed(self):

        trap = ac.Trap(density=10, lifetime=2)

        fill = trap.fill_fraction_from_time_elapsed(1)
        assert fill == np.exp(-0.5)

        time = trap.time_elapsed_from_fill_fraction(0.5)
        assert time == -2 * np.log(0.5)

        assert fill == trap.fill_fraction_from_time_elapsed(
            trap.time_elapsed_from_fill_fraction(fill)
        )
        assert time == trap.time_elapsed_from_fill_fraction(
            trap.fill_fraction_from_time_elapsed(time)
        )

    def test__electrons_released_in_pixel_using_time(self):

        trap = ac.Trap(density=10, lifetime=-1 / np.log(0.5))
        trap_manager_fill = ac.TrapManager(traps=[trap], rows=6)
        trap_manager_time = ac.TrapManagerTrackTime(traps=[trap], rows=6)

        trap_manager_fill.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )
        trap_manager_time.watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.2)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )

        electrons_released_fill = trap_manager_fill.electrons_released_in_pixel()
        electrons_released_time = trap_manager_time.electrons_released_in_pixel()

        assert electrons_released_fill == electrons_released_time

        assert trap_manager_time.watermarks == pytest.approx(
            np.array(
                [
                    [0.5, trap.time_elapsed_from_fill_fraction(0.4)],
                    [0.2, trap.time_elapsed_from_fill_fraction(0.2)],
                    [0.1, trap.time_elapsed_from_fill_fraction(0.1)],
                    [0, 0],
                    [0, 0],
                    [0, 0],
                ]
            )
        )

    def test__electrons_captured_by_traps_using_time(self):

        trap = ac.Trap(density=10, lifetime=-1 / np.log(0.5))
        trap_manager_fill = ac.TrapManager(traps=[trap], rows=6)
        trap_manager_time = ac.TrapManagerTrackTime(traps=[trap], rows=6)

        trap_manager_fill.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.3], [0, 0], [0, 0], [0, 0]]
        )
        trap_manager_time.watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.3)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.6

        electrons_captured_fill = trap_manager_fill.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager_fill.watermarks,
            traps=trap_manager_fill.traps,
        )
        electrons_captured_time = trap_manager_time.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager_time.watermarks,
            traps=trap_manager_time.traps,
        )

        assert electrons_captured_fill == electrons_captured_time

    def test__updated_watermarks_from_capture_using_time(self):

        trap = ac.Trap(density=10, lifetime=-1 / np.log(0.5))
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)

        watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.3)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.75

        watermarks = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
        )

        assert watermarks == pytest.approx(
            np.array(
                [
                    [0.75, 0],
                    [0.05, trap.time_elapsed_from_fill_fraction(0.3)],
                    [0, 0],
                    [0, 0],
                    [0, 0],
                    [0, 0],
                ]
            )
        )

    def test__updated_watermarks_from_capture_not_enough_multiple_traps_using_time(
        self,
    ):

        trap_1 = ac.Trap(density=10, lifetime=-1 / np.log(0.5))
        trap_2 = ac.Trap(density=10, lifetime=-2 / np.log(0.5))
        trap_manager = ac.TrapManagerTrackTime(traps=[trap_1, trap_2], rows=6)

        watermarks = np.array(
            [
                [
                    0.5,
                    trap_1.time_elapsed_from_fill_fraction(0.8),
                    trap_2.time_elapsed_from_fill_fraction(0.6),
                ],
                [
                    0.2,
                    trap_1.time_elapsed_from_fill_fraction(0.4),
                    trap_2.time_elapsed_from_fill_fraction(0.2),
                ],
                [
                    0.1,
                    trap_1.time_elapsed_from_fill_fraction(0.3),
                    trap_2.time_elapsed_from_fill_fraction(0.1),
                ],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        )
        electron_fractional_height = 0.6
        enough = 0.5

        watermarks = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
            enough=enough,
        )

        assert watermarks == pytest.approx(
            np.array(
                [
                    [
                        0.5,
                        trap_1.time_elapsed_from_fill_fraction(0.9),
                        trap_2.time_elapsed_from_fill_fraction(0.8),
                    ],
                    [
                        0.1,
                        trap_1.time_elapsed_from_fill_fraction(0.7),
                        trap_2.time_elapsed_from_fill_fraction(0.6),
                    ],
                    [
                        0.1,
                        trap_1.time_elapsed_from_fill_fraction(0.4),
                        trap_2.time_elapsed_from_fill_fraction(0.2),
                    ],
                    [
                        0.1,
                        trap_1.time_elapsed_from_fill_fraction(0.3),
                        trap_2.time_elapsed_from_fill_fraction(0.1),
                    ],
                    [0, 0, 0],
                    [0, 0, 0],
                ]
            )
        )


class TestTrapLifetimeContinuum:
    def test__distribution_of_traps_with_lifetime(self):

        median_lifetime = -1 / np.log(0.5)
        scale_lifetime = 0.5

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )

        # Check that the integral from zero to infinity is one
        assert integrate.quad(
            trap.distribution_of_traps_with_lifetime,
            0,
            np.inf,
            args=(trap.middle_lifetime, trap.scale_lifetime),
        )[0] == pytest.approx(1)

    def test__fill_fraction_from_time_elapsed_narrow_continuum(self):

        # Check that narrow continuum gives similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=1)
        fill_single = trap.fill_fraction_from_time_elapsed(1)

        # Narrow continuum
        median_lifetime = 1
        scale_lifetime = 0.1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        fill_continuum = trap.fill_fraction_from_time_elapsed(1)

        assert fill_continuum == pytest.approx(fill_single, rel=0.01)

    def test__time_elapsed_from_fill_fraction_narrow_continuum(self):

        # Check that narrow continuum gives similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=1)
        time_single = trap.time_elapsed_from_fill_fraction(0.5)

        # Narrow continuum
        median_lifetime = 1
        scale_lifetime = 0.1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        time_continuum = trap.time_elapsed_from_fill_fraction(0.5)

        assert time_continuum == pytest.approx(time_single, rel=0.01)

    def test__time_elapsed_from_fill_fraction_continuum(self):

        median_lifetime = 1
        scale_lifetime = 1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        time = 1

        assert (
            trap.time_elapsed_from_fill_fraction(
                trap.fill_fraction_from_time_elapsed(time)
            )
            == time
        )

    def test__electrons_released_from_time_elapsed_and_time_narrow_continuum(self):

        # Check that narrow continuum gives similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=1)
        trap_manager = ac.TrapManager(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )
        electrons_released_single = trap_manager.electrons_released_in_pixel()

        # Narrow continuum
        median_lifetime = 1
        scale_lifetime = 0.1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.2)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electrons_released_continuum = trap_manager.electrons_released_in_pixel()

        assert electrons_released_continuum == pytest.approx(
            electrons_released_single, rel=0.01
        )

    def test__electrons_released_from_time_elapsed_and_time_continuum(self):

        # Check that continuum gives somewhat similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=1)
        trap_manager = ac.TrapManager(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )
        electrons_released_single = trap_manager.electrons_released_in_pixel()

        # Continuum
        median_lifetime = 1
        scale_lifetime = 1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.2)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electrons_released_continuum = trap_manager.electrons_released_in_pixel()

        assert electrons_released_continuum == pytest.approx(
            electrons_released_single, rel=1
        )

    def test__electrons_captured_by_traps_narrow_continuum(self):

        # Check that narrow continuum gives similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=1)
        trap_manager = ac.TrapManager(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.6
        electrons_captured_single = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        # Narrow continuum
        median_lifetime = 1
        scale_lifetime = 0.1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.2)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.6
        electrons_captured_continuum = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured_continuum == pytest.approx(
            electrons_captured_single, rel=0.01
        )

    def test__electrons_captured_by_traps_continuum(self):

        # Check that continuum gives somewhat similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=1)
        trap_manager = ac.TrapManager(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [[0.5, 0.8], [0.2, 0.4], [0.1, 0.2], [0, 0], [0, 0], [0, 0]]
        )
        electron_fractional_height = 0.6
        electrons_captured_single = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        # Narrow continuum
        median_lifetime = 1
        scale_lifetime = 1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        trap_manager.watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.2)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.6
        electrons_captured_continuum = trap_manager.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=trap_manager.watermarks,
            traps=trap_manager.traps,
        )

        assert electrons_captured_single == pytest.approx(
            electrons_captured_continuum, rel=1
        )

    def test__updated_watermarks_from_capture_narrow_continuum(self):

        # Check that narrow continuum gives similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=-1 / np.log(0.5))
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.3)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.75
        watermarks_single = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height, watermarks=watermarks
        )

        # Narrow continuum
        median_lifetime = 1
        scale_lifetime = 0.1

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.2)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.75
        watermarks_continuum = trap_manager.updated_watermarks_from_capture(
            electron_fractional_height=electron_fractional_height, watermarks=watermarks
        )

        assert watermarks_continuum == pytest.approx(watermarks_single, rel=0.1)

    def test__updated_watermarks_from_capture_not_enough_narrow_continuum(self):

        # Check that narrow continuum gives similar results to single lifetime
        # Simple trap
        trap = ac.Trap(density=10, lifetime=-1 / np.log(0.5))
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.3)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.6
        enough = 0.5
        watermarks_single = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
            enough=enough,
        )

        # Narrow continuum
        median_lifetime = 1
        scale_lifetime = 0.01

        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        trap = ac.TrapLifetimeContinuum(
            density=10,
            distribution_of_traps_with_lifetime=trap_distribution,
            middle_lifetime=median_lifetime,
            scale_lifetime=scale_lifetime,
        )
        trap_manager = ac.TrapManagerTrackTime(traps=[trap], rows=6)
        watermarks = np.array(
            [
                [0.5, trap.time_elapsed_from_fill_fraction(0.8)],
                [0.2, trap.time_elapsed_from_fill_fraction(0.4)],
                [0.1, trap.time_elapsed_from_fill_fraction(0.2)],
                [0, 0],
                [0, 0],
                [0, 0],
            ]
        )
        electron_fractional_height = 0.6
        enough = 0.5
        watermarks_continuum = trap_manager.updated_watermarks_from_capture_not_enough(
            electron_fractional_height=electron_fractional_height,
            watermarks=watermarks,
            enough=enough,
        )

        assert watermarks_continuum == pytest.approx(watermarks_single, rel=0.5)

    def test__TrapLogNormalLifetimeContinuum(self):

        median_lifetime = -1 / np.log(0.5)
        scale_lifetime = 0.5

        trap = ac.TrapLogNormalLifetimeContinuum(
            density=10, middle_lifetime=median_lifetime, scale_lifetime=scale_lifetime,
        )

        # Check that the integral from zero to infinity is one
        assert integrate.quad(
            trap.distribution_of_traps_with_lifetime,
            0,
            np.inf,
            args=(trap.middle_lifetime, trap.scale_lifetime),
        )[0] == pytest.approx(1)

        # Check the automatic distribution function is set correctly
        def trap_distribution(lifetime, median, scale):
            return np.exp(
                -((np.log(lifetime) - np.log(median)) ** 2) / (2 * scale ** 2)
            ) / (lifetime * scale * np.sqrt(2 * np.pi))

        assert trap.distribution_of_traps_with_lifetime(
            1.2345, median_lifetime, scale_lifetime
        ) == trap_distribution(1.2345, median_lifetime, scale_lifetime)

    def test__trails_from_continuum_traps_compare_with_single_trap(self): 
        return 0 ###
        
        # Plotting test -- manually set True to make the plot
        # do_plot = False
        do_plot = True

        main = ac.ArcticMain(parallel_express=0)

        size = 20
        pixels = np.arange(size)
        image_orig = np.zeros((size, 1))
        image_orig[1, 0] = 1e5

        ccd_volume = ac.CCDVolume(
            well_fill_beta=0.8, well_max_height=8.47e4, well_notch_depth=1e-7
        )
        
        density = 10
        lifetime = 5

        if do_plot:
            plt.figure()

            # Single trap
            trap_single = ac.Trap(density=density, lifetime=lifetime)
            image_single = main.add_cti(
                image=image_orig,
                parallel_traps=[trap_single],
                parallel_ccd_volume=ccd_volume,
            )
            plt.plot(pixels, image_single[:, 0], c="k", label="Single")

            # Range of trap lifetime distributions
            for scale in [0.1, 0.5, 1]:
                trap = ac.TrapLogNormalLifetimeContinuum(
                    density=density, middle_lifetime=lifetime, scale_lifetime=scale,
                )
                image_continuum = main.add_cti(
                    image=image_orig,
                    parallel_traps=[trap],
                    parallel_ccd_volume=ccd_volume,
                )
                plt.plot(pixels, image_continuum[:, 0], label=r"$\sigma = %.1f$" % scale)

            plt.legend()
            plt.yscale("log")
            plt.xlabel("Pixel")
            plt.ylabel("Counts")
            plt.xlim(0, size)
            plt.ylim(0.1, 10)###

            plt.show()

    def test__trails_from_continuum_traps_compare_with_distribution_of_single_traps(self):
        return 0 ###
        
        # Normal and plotting test -- manually set True to make the plot
        # do_plot = False
        do_plot = True

        main = ac.ArcticMain(parallel_express=0)

        size = 20
        pixels = np.arange(size)
        image_orig = np.zeros((size, 1))
        image_orig[1, 0] = 1e5

        ccd_volume = ac.CCDVolume(
            well_fill_beta=0.8, well_max_height=8.47e4, well_notch_depth=1e-7
        )

        density = 10
        lifetime = 5
        scale = 0.5
        min_log_lifetime = -1
        max_log_lifetime = 3
        low_sample = 10
        mid_sample = 11
        high_sample = 1000

        # Continuum traps
        trap_continuum = ac.TrapLogNormalLifetimeContinuum(
            density=density, middle_lifetime=lifetime, scale_lifetime=scale,
        )
        image_continuum = main.add_cti(
            image=image_orig,
            parallel_traps=[trap_continuum],
            parallel_ccd_volume=ccd_volume,
        )
        
        # Equivalent distributions of single traps
        trap_single = ac.Trap(density=density, lifetime=lifetime)
        image_single = main.add_cti(
            image=image_orig,
            parallel_traps=[trap_single],
            parallel_ccd_volume=ccd_volume,
        )
        
        lifetimes_low = np.logspace(min_log_lifetime, max_log_lifetime, low_sample)
        densities_low = ac.TrapLogNormalLifetimeContinuum.log_normal_distribution(
            lifetimes_low, lifetime, scale
        )
        densities_low *= density / densities_low.sum()
        traps_low = [
            ac.Trap(density=density, lifetime=lifetime)
            for density, lifetime in zip(densities_low, lifetimes_low)
        ]
        image_singles_low = main.add_cti(
            image=image_orig,
            parallel_traps=traps_low,
            parallel_ccd_volume=ccd_volume,
        )
        
        lifetimes_mid = np.logspace(min_log_lifetime, max_log_lifetime, mid_sample)
        densities_mid = ac.TrapLogNormalLifetimeContinuum.log_normal_distribution(
            lifetimes_mid, lifetime, scale
        )
        densities_mid *= density / densities_mid.sum()
        traps_mid = [
            ac.Trap(density=density, lifetime=lifetime)
            for density, lifetime in zip(densities_mid, lifetimes_mid)
        ]
        image_singles_mid = main.add_cti(
            image=image_orig,
            parallel_traps=traps_mid,
            parallel_ccd_volume=ccd_volume,
        )
        
        lifetimes_high = np.logspace(min_log_lifetime, max_log_lifetime, high_sample)
        densities_high = ac.TrapLogNormalLifetimeContinuum.log_normal_distribution(
            lifetimes_high, lifetime, scale
        )
        densities_high *= density / densities_high.sum()
        traps_high = [
            ac.Trap(density=density, lifetime=lifetime)
            for density, lifetime in zip(densities_high, lifetimes_high)
        ]
        image_singles_high = main.add_cti(
            image=image_orig,
            parallel_traps=traps_high,
            parallel_ccd_volume=ccd_volume,
        )
        
        if do_plot:
            plt.figure()

            plt.plot(pixels, image_continuum[:, 0], ls="--", zorder=9, label="Continuum")
            plt.plot(pixels, image_single[:, 0], c="k", label="1 single")
            plt.plot(pixels, image_singles_low[:, 0], label="%d singles" % low_sample)
            plt.plot(pixels, image_singles_mid[:, 0], label="%d singles" % mid_sample)
            plt.plot(pixels, image_singles_high[:, 0], label="%d singles" % high_sample)

            plt.legend()
            plt.yscale("log")
            plt.xlabel("Pixel")
            plt.ylabel("Counts")
            plt.xlim(0, size)
            plt.ylim(0.1, 10)###
            
            # plt.figure()
            # 
            # lifetimes_plot = np.logspace(min_log_lifetime - 1, max_log_lifetime + 1, 10000)
            # densities_plot = trap_continuum.distribution_of_traps_with_lifetime(
            #     lifetimes_plot, lifetime, scale
            #     )
            # densities_plot *= density / densities_plot.sum()
            # plt.plot(lifetimes_plot, densities_plot, ls="--", zorder=9, label="Continuum")
            # 
            # plt.scatter(lifetime, density, c="k", label="1 single")
            # plt.plot(lifetimes_low, densities_low, label="%d singles" % low_sample)
            # plt.plot(lifetimes_mid, densities_mid, label="%d singles" % mid_sample)
            # plt.plot(lifetimes_high, densities_high, label="%d singles" % high_sample)
            # 
            # plt.legend()
            # plt.xscale("log")
            # plt.yscale("log")
            # plt.xlim(lifetimes_high[1], lifetimes_high[-1])
            # # plt.ylim(densities_high[-1], None)
            # plt.xlabel("Lifetime")
            # plt.ylabel("Density")

            plt.show()
