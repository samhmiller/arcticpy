import numpy as np

from arctic import util


class ArcticParams(object):
    def __init__(
        self,
        parallel_ccd_volume=None,
        serial_ccd_volume=None,
        parallel_traps=None,
        serial_traps=None,
    ):
        """Sets up the arctic CTI model using parallel and serial parameters specified using a child of the
        ArcticParams.ParallelParams and ArcticParams.SerialParams abstract base classes.

        Parameters
        ----------
        parallel_ccd_volume: CCDVolume
            Class describing the state of the CCD in the parallel direction
        serial_ccd_volume: CCDVolume
            Class describing the state of the CCD in the serial direction
        parallel_traps : [ArcticParams.ParallelParams]
           The parallel parameters for the arctic CTI model
        serial_traps : [ArcticParams.SerialParams]
           The serial parameters for the arctic CTI model
        """
        self.parallel_ccd_volume = parallel_ccd_volume
        self.serial_ccd_volume = serial_ccd_volume
        self.parallel_traps = parallel_traps or []
        self.serial_traps = serial_traps or []

    @property
    def delta_ellipticity(self):
        return sum(
            [trap.delta_ellipticity for trap in self.parallel_traps]
        ) + sum([trap.delta_ellipticity for trap in self.serial_traps])


class CCDVolume(object):
    def __init__(
        self, well_max_height=1000.0, well_notch_depth=1e-9, well_fill_beta=0.58
    ):
        """Abstract base class of the cti model parameters. Parameters associated with the traps are set via a child \
        class.

        Parameters
        ----------
        well_notch_depth : float
            The CCD notch depth
        well_fill_alpha : float
            The volume-filling coefficient (alpha) of how an electron cloud fills the volume of a pixel.
        well_fill_beta : float
            The volume-filling power (beta) of how an electron cloud fills the volume of a pixel.
        well_fill_gamma : float
            The volume-filling constant (gamma) of how an electron cloud fills the volume of a pixel.
        """
        self.well_max_height = well_max_height
        self.well_notch_depth = well_notch_depth
        self.well_range = well_max_height - well_notch_depth
        self.well_fill_beta = well_fill_beta

    def __repr__(self):
        return "\n".join(
            (
                "Well Notch Depth: {}".format(self.well_notch_depth),
                "Well Fill Beta: {}".format(self.well_fill_beta),
            )
        )

    # TODO : Its good to give full names to parameters - shorthand may make code cleaer for you but for other peple it
    # TODO : Adds confusion!

    # TODO : For short functions its also more readable using the 'from' naming convention so the reader can see
    # TODO : what does in and out the calculation.

    def electron_fractional_height_from_electrons(self, electrons):
        """ Calculate the height the electrons reach within a CCD pixel well.
        """
        electron_fractional_height = (
            (electrons - self.well_notch_depth) / self.well_range
        ) ** self.well_fill_beta

        return util.set_min_max(electron_fractional_height, 0, 1)


class CCDVolumeComplex(CCDVolume):
    def __init__(
        self,
        well_max_height=1000.0,
        well_notch_depth=1e-9,
        well_fill_alpha=1.0,
        well_fill_beta=0.58,
    ):
        """Abstract base class of the cti model parameters. Parameters associated with the traps are set via a child \
        class.

        Parameters
        ----------
        well_notch_depth : float
            The CCD notch depth
        well_fill_alpha : float
            The volume-filling coefficient (alpha) of how an electron cloud fills the volume of a pixel.
        well_fill_beta : float
            The volume-filling power (beta) of how an electron cloud fills the volume of a pixel.
        well_fill_gamma : float
            The volume-filling constant (gamma) of how an electron cloud fills the volume of a pixel.
        """

        super(CCDVolumeComplex, self).__init__(
            well_max_height=well_max_height,
            well_notch_depth=well_notch_depth,
            well_fill_beta=well_fill_beta,
        )

        self.well_fill_alpha = well_fill_alpha

    def electron_fractional_height_from_electrons(self, electrons):
        """ Calculate the height the electrons reach within a CCD pixel well.
        """

        electron_fractional_height = (
            self.well_fill_alpha
            * (
                (electrons - self.well_notch_depth)
                / (self.well_range - self.well_notch_depth)
            )
        ) ** self.well_fill_beta

        return util.set_min_max(electron_fractional_height, 0, 1)


class Trap(object):
    def __init__(self, density=0.13, lifetime=0.25):
        """The CTI model parameters used for parallel clocking, using one trap of trap.

        Parameters
        ----------
        density : float
            The trap density of the trap.
        lifetime : float
            The trap lifetimes of the trap.
        """
        self.density = density
        self.lifetime = lifetime
        self.exponential_factor = 1 - np.exp(-1 / lifetime)

    def electrons_released_from_electrons(self, electrons):
        """ Calculate the number of released electrons from the trap.

            Args:
                electrons : float
                    The initial number of trapped electrons.

            Returns:
                electrons_released : float
                    The number of released electrons.
        """
        return electrons * self.exponential_factor

    @property
    def delta_ellipticity(self):

        a = 0.05333
        d_a = 0.03357
        d_p = 1.628
        d_w = 0.2951
        g_a = 0.09901
        g_p = 0.4553
        g_w = 0.4132

        return self.density * (
            a
            + d_a * (np.arctan((np.log(self.lifetime) - d_p) / d_w))
            + (
                g_a
                * np.exp(
                    -((np.log(self.lifetime) - g_p) ** 2.0) / (2 * g_w ** 2.0)
                )
            )
        )

    def __repr__(self):
        return "\n".join(
            (
                "Trap Density: {}".format(self.density),
                "Trap Lifetime: {}".format(self.lifetime),
            )
        )

    @classmethod
    def poisson_trap(cls, trap, shape, seed=0):
        """For a set of traps with a given set of densities (which are in traps per pixel), compute a new set of \
        trap densities by drawing new values for from a Poisson distribution.

        This requires us to first convert each trap density to the total number of traps in the column.

        This is used to model the random distribution of traps on a CCD, which changes the number of traps in each \
        column.

        Parameters
        -----------
        trap
        shape : (int, int)
            The shape of the image, so that the correct number of trap densities are computed.
        seed : int
            The seed of the Poisson random number generator.
        """
        np.random.seed(seed)
        total_trapss = tuple(map(lambda sp: sp.density * shape[0], trap))
        poisson_densities = [
            np.random.poisson(total_trapss) / shape[0] for _ in range(shape[1])
        ]
        poisson_trap = []
        for densities in poisson_densities:
            for i, s in enumerate(trap):
                poisson_trap.append(
                    Trap(density=densities[i], lifetime=s.lifetime)
                )

        return poisson_trap


class TrapManager(object):
    def __init__(self, traps, rows):
        """The manager for potentially multiple trap species that must use 
        watermarks in the same way as each other.

        Parameters
        ----------
        traps : [Trap]
            A list of one or more trap objects.
        rows :int
            The number of rows in the image. i.e. the maximum number of
            possible electron trap/release events.            
        """
        self.traps = traps
        self.rows = rows

        # Set up the watermarks
        self.watermarks = self.initial_watermarks_from_rows_and_total_traps(
            rows=self.rows, total_traps=len(self.traps)
        )

    def initial_watermarks_from_rows_and_total_traps(self, rows, total_traps):
        """ Initialise the watermark array of trap states.

        Parameters
        -----------
        rows :int
            The number of rows in the image. i.e. the maximum number of
            possible electron trap/release events.
        total_traps : int
            The number of trap trap being modelled.

        Returns
        --------
        watermarks : np.ndarray
            Array of watermark heights and fill fractions to describe the trap states. Lists each (active) watermark
            height_e fraction and the corresponding fill fractions of each trap trap. Inactive elements are set to 0.

            [[height_e, fill, fill, ...],
             [height_e, fill, fill, ...],
             ...                       ]
        """
        return np.zeros((rows, 1 + total_traps), dtype=float)

    def reset_traps_for_next_express_loop(self):
        """Reset the trap watermarks for the next run of release and capture.
        """
        self.watermarks.fill(0)

    def electrons_released_in_pixel(self):
        """ Release electrons from traps and update the trap watermarks.

        Returns
        -------
        electrons_released : float
            The number of released electrons.
        
        Updates
        -------
        watermarks : np.ndarray
            The updated watermarks. See initial_watermarks_from_rows_and_total_traps().
        """
        # Initialise the number of released electrons
        electrons_released = 0

        # Find the highest active watermark
        max_watermark_index = np.argmax(self.watermarks[:, 0] == 0) - 1

        # For each watermark
        for watermark_index in range(max_watermark_index + 1):
            # Initialise the number of released electrons from this watermark level
            electrons_released_watermark = 0

            # For each trap trap
            for trap_index, trap in enumerate(self.traps):
                # Number of released electrons (not yet including the trap density)
                electrons_released_from_trap = trap.electrons_released_from_electrons(
                    electrons=self.watermarks[watermark_index, 1 + trap_index]
                )

                # Update the watermark fill fraction
                self.watermarks[
                    watermark_index, 1 + trap_index
                ] -= electrons_released_from_trap

                # Update the actual number of released electrons
                electrons_released_watermark += (
                    electrons_released_from_trap * trap.density
                )

            # Multiply the summed fill fractions by the height
            electrons_released += (
                electrons_released_watermark
                * self.watermarks[watermark_index, 0]
            )

        return electrons_released

    def electrons_captured_by_traps(
        self, electron_fractional_height, watermarks, traps
    ):
        """
        Find the total number of electrons that the traps can capture.

        Parameters
        ------------
        electron_fractional_height : float
            The fractional height of the electron cloud in the pixel.

        watermarks : np.ndarray
            The initial watermarks. See initial_watermarks_from_rows_and_total_traps().

        traps : [TrapSpecies]
            An array of one or more objects describing a trap of trap.

        Returns
        ---------
        electrons_captured : float
            The number of captured electrons.
        """
        # Initialise the number of captured electrons
        electrons_captured = 0

        # The number of traps of each trap
        densities = [trap_trap.density for trap_trap in traps]

        # Find the highest active watermark
        max_watermark_index = np.argmax(watermarks[:, 0] == 0) - 1

        # Initialise cumulative watermark height
        cumulative_watermark_height = 0

        # Capture electrons above each existing watermark level below the highest
        for watermark_index in range(max_watermark_index + 1):
            # Update cumulative watermark height
            watermark_height = watermarks[watermark_index, 0]
            cumulative_watermark_height += watermark_height

            # Capture electrons all the way to this watermark (for all trap trap)
            if cumulative_watermark_height < electron_fractional_height:
                electrons_captured += watermark_height * np.sum(
                    (1 - watermarks[watermark_index, 1:]) * densities
                )

            # Capture electrons part-way between the previous and this watermark
            else:
                electrons_captured += (
                    electron_fractional_height
                    - (cumulative_watermark_height - watermark_height)
                ) * np.sum((1 - watermarks[watermark_index, 1:]) * densities)

                # No point in checking even higher watermarks
                return electrons_captured

        # Capture any electrons above the highest existing watermark
        if watermarks[max_watermark_index, 0] < electron_fractional_height:
            electrons_captured += (
                electron_fractional_height - cumulative_watermark_height
            ) * np.sum(densities)

        return electrons_captured

    def updated_watermarks_from_capture(
        self, electron_fractional_height, watermarks
    ):
        """ Update the trap watermarks for capturing electrons.

        Parameters
        -----------
        electron_fractional_height : float
            The fractional height of the electron cloud in the pixel.

        watermarks : np.ndarray
            The initial watermarks. See initial_watermarks_from_rows_and_total_traps().

        Returns
        -------
        watermarks : np.ndarray
            The updated watermarks. See initial_watermarks_from_rows_and_total_traps().
        """

        # Find the highest active watermark
        max_watermark_index = np.argmax(watermarks[:, 0] == 0) - 1
        if max_watermark_index == -1:
            max_watermark_index = 0

        # Cumulative watermark heights
        cumulative_watermark_height = np.cumsum(
            watermarks[: max_watermark_index + 1, 0]
        )

        # If all watermarks will be overwritten
        if cumulative_watermark_height[-1] < electron_fractional_height:
            # Overwrite the first watermark
            watermarks[0, 0] = electron_fractional_height
            watermarks[0, 1:] = 1

            # Remove all higher watermarks
            watermarks[1:, :] = 0

            return watermarks

        # Find the first watermark above the cloud, which won't be fully overwritten
        watermark_index_above_cloud = np.argmax(
            electron_fractional_height < cumulative_watermark_height
        )

        # If some will be overwritten
        if 0 < watermark_index_above_cloud:
            # Edit the partially overwritten watermark
            watermarks[watermark_index_above_cloud, 0] -= (
                electron_fractional_height
                - cumulative_watermark_height[watermark_index_above_cloud - 1]
            )

            # Remove the no-longer-needed overwritten watermarks
            watermarks[: watermark_index_above_cloud - 1, :] = 0

            # Move the no-longer-needed watermarks to the end of the list
            watermarks = np.roll(
                watermarks, 1 - watermark_index_above_cloud, axis=0
            )

            # Edit the new first watermark
            watermarks[0, 0] = electron_fractional_height
            watermarks[0, 1:] = 1

        # If none will be overwritten
        else:
            # Move an empty watermark to the start of the list
            watermarks = np.roll(watermarks, 1, axis=0)

            # Edit the partially overwritten watermark
            watermarks[1, 0] -= electron_fractional_height

            # Edit the new first watermark
            watermarks[0, 0] = electron_fractional_height
            watermarks[0, 1:] = 1

        return watermarks

    def updated_watermarks_from_capture_not_enough(
        self, electron_fractional_height, watermarks, enough
    ):
        """
        Update the trap watermarks for capturing electrons when not enough are available to fill every trap below the
        cloud height (rare!).

        Like update_trap_wmk_capture(), but instead of setting filled trap fractions to 1, increase them by the enough
        fraction towards 1.

        Parameters
        ----------
        electron_fractional_height : float
            The fractional height of the electron cloud in the pixel.
        watermarks : np.ndarray
            The initial watermarks. See initial_watermarks_from_rows_and_total_traps().
        enough : float
            The ratio of available electrons to traps up to this height.

        Returns
        --------
        watermarks : np.ndarray
            The updated watermarks. See initial_watermarks_from_rows_and_total_traps().
        """
        # Find the highest active watermark
        max_watermark_index = np.argmax(watermarks[:, 0] == 0) - 1
        if max_watermark_index == -1:
            max_watermark_index = 0

        # If the first capture
        if max_watermark_index == 0:
            # Edit the new watermark
            watermarks[0, 0] = electron_fractional_height
            watermarks[0, 1:] = enough

            return watermarks

        # Cumulative watermark heights
        cumulative_watermark_height = np.cumsum(
            watermarks[: max_watermark_index + 1, 0]
        )

        # Find the first watermark above the cloud, which won't be fully overwritten
        watermark_index_above_height = np.argmax(
            electron_fractional_height < cumulative_watermark_height
        )

        # If all watermarks will be overwritten
        if cumulative_watermark_height[-1] < electron_fractional_height:
            # Do the same as the only-some case (unlike update_trap_wmk_capture())
            watermark_index_above_height = max_watermark_index

        # If some (or all) will be overwritten
        if 0 < watermark_index_above_height:
            # Move one new empty watermark to the start of the list
            watermarks = np.roll(watermarks, 1, axis=0)

            # Reorder the relevant watermarks near the start of the list
            watermarks[: 2 * watermark_index_above_height] = watermarks[
                1 : 2 * watermark_index_above_height + 1
            ]

            # Edit the new watermarks' fill fractions to the original fill plus (1 -
            # original fill) * enough.
            # e.g. enough = 0.5 --> fill half way to 1.
            watermarks[: watermark_index_above_height + 1, 1:] = (
                watermarks[: watermark_index_above_height + 1, 1:]
                * (1 - enough)
                + enough
            )

            # If all watermarks will be overwritten
            if cumulative_watermark_height[-1] < electron_fractional_height:
                # Edit the new highest watermark
                watermarks[watermark_index_above_height + 1, 0] = (
                    electron_fractional_height - cumulative_watermark_height[-1]
                )
                watermarks[watermark_index_above_height + 1, 1:] = enough
            else:
                # Edit the new watermarks' heights
                watermarks[
                    watermark_index_above_height : watermark_index_above_height
                    + 2,
                    0,
                ] *= (1 - enough)

        # If none will be overwritten
        else:
            # Move an empty watermark to the start of the list
            watermarks = np.roll(watermarks, 1, axis=0)

            # Edit the partially overwritten watermark
            watermarks[1, 0] -= electron_fractional_height

            # Edit the new first watermark
            watermarks[0, 0] = electron_fractional_height
            watermarks[0, 1:] = watermarks[1, 1:] * (1 - enough) + enough

        return watermarks

    def electrons_captured_in_pixel(self, electrons_available, ccd_volume):
        """
        Capture electrons in traps and update the trap watermarks.

        Parameters
        -----------
        electrons_available : float
            The number of available electrons for trapping.
        ccd_volume : CCDVolume
            The object describing the CCD.

        Returns
        ---------
        electrons_captured : float
            The number of captured electrons.
        
        Updates
        -------
        watermarks : np.ndarray
            The updated watermarks. See initial_watermarks_from_rows_and_total_traps().
        """

        # Zero capture if no electrons are high enough to be trapped
        if electrons_available < ccd_volume.well_notch_depth:
            return 0

        # The fractional height the electron cloud reaches in the pixel well
        electron_fractional_height = ccd_volume.electron_fractional_height_from_electrons(
            electrons=electrons_available
        )

        # Find the number of electrons that should be captured
        electrons_captured = self.electrons_captured_by_traps(
            electron_fractional_height=electron_fractional_height,
            watermarks=self.watermarks,
            traps=self.traps,
        )

        # Stop if no capture
        if electrons_captured == 0:
            return electrons_captured

        # Check whether enough electrons are available to be captured
        enough = electrons_available / electrons_captured

        # Update watermark levels
        if 1 < enough:
            self.watermarks = self.updated_watermarks_from_capture(
                electron_fractional_height=electron_fractional_height,
                watermarks=self.watermarks,
            )
        else:
            self.watermarks = self.updated_watermarks_from_capture_not_enough(
                electron_fractional_height=electron_fractional_height,
                watermarks=self.watermarks,
                enough=enough,
            )
            # Reduce the final number of captured electrons
            electrons_captured *= enough

        return electrons_captured
