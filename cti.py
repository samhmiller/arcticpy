""" CTI python

    Jacob Kegerreis (2019) jacob.kegerreis@durham.ac.uk
    
    WIP...
"""
import numpy as np


# //////////////////////////////////////////////////////////////////////////// #
#                               Utility Functions                              #
# //////////////////////////////////////////////////////////////////////////// #
def set_min_max(value, min, max):
    """ Fix a value between a minimum and maximum. """
    if value < min:
        return min
    elif max < value:
        return max
    else:
        return value


# //////////////////////////////////////////////////////////////////////////// #
#                               Classes                                        #
# //////////////////////////////////////////////////////////////////////////// #
class CCD(object):
    def __init__(
        self,
        well_fill_alpha,
        well_fill_beta,
        well_fill_gamma,
        well_max_height,
        well_notch_height,
    ):
        """ Properties of the CCD.
        
            Args:
                well_fill_alpha : float
                    The volume-filling coefficient, alpha, of how an electron 
                    cloud fills the volume of a pixel.
                
                well_fill_beta : float
                    The volume-filling power, beta, of how an electron cloud 
                    fills the volume of a pixel.
                
                well_fill_gamma : float
                    The volume-filling constant, gamma, of how an electron cloud 
                    fills the volume of a pixel.
                
                well_max_height : float
                    The total depth of the CCD well, i.e. the maximum number of 
                    electrons per pixel.
                
                well_notch_height : float
                    The depth of the CCD notch, i.e. the minimum number of 
                    electrons per pixel that are relevant for trapping.
        """
        self.well_fill_alpha = well_fill_alpha
        self.well_fill_beta = well_fill_beta
        self.well_fill_gamma = well_fill_gamma
        self.well_max_height = well_max_height
        self.well_notch_height = well_notch_height
        self.well_range = self.well_max_height - self.well_notch_height

    def height_e(self, e_avai):
        """ Calculate the height the electrons reach within a CCD pixel well.
        """
        height_e = (
            (e_avai - self.well_notch_height) / self.well_range
        ) ** self.well_fill_beta

        return set_min_max(height_e, 0, 1)


class Clock(object):
    def __init__(self, A1_sequence):
        """ The clock that controls the transfer of electrons.

        Args:
            A1_sequence ([float])
                The array or single value of the time between clock shifts.
        """
        self.A1_sequence = A1_sequence


class TrapSpecies(object):
    def __init__(self, density, lifetime):
        """ A species of trap.
        
            Args:                
                density : float
                    The number of traps per pixel.
                
                lifetime : float
                    The lifetime for release of an electron from the trap,
                    in clock cycles.
        """
        # Required
        self.density = density
        self.lifetime = lifetime

        # Derived
        self.exponential_factor = 1 - np.exp(-1 / self.lifetime)

    def e_rele(self, e_init):
        """ Calculate the number of released electrons from the trap.
        
            Args:
                e_init : float
                    The initial number of trapped electrons.
                
            Returns:
                e_rele : float
                    The number of released electrons.
        """
        return e_init * self.exponential_factor


# //////////////////////////////////////////////////////////////////////////// #
#                               Support Functions                              #
# //////////////////////////////////////////////////////////////////////////// #
def init_A2_trap_wmk_height_fill(num_column, num_species):
    """ Initialise the watermark array of trap states.
    
        Args:
            num_column (int)
                The number of columns in the image. i.e. the maximum number of 
                possible electron trap/release events.
            
            num_species (int)
                The number of trap species being modelled.
    
        Returns:
            A2_trap_wmk_height_fill : [[float]]
                Array of watermark heights and fill fractions to describe the 
                trap states. Lists each (active) watermark height_e fraction and  
                the corresponding fill fractions of each trap species. Inactive 
                elements are set to 0.
                
                [[height_e, fill, fill, ...], 
                 [height_e, fill, fill, ...],
                 ...                       ]
    """
    return np.zeros((num_column, 1 + num_species), dtype=float)
