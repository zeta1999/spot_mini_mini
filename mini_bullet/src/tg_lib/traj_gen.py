import numpy as np


class CyclicIntegrator():
    def __init__(self, dphi_leg=0.0):
        # Phase
        self.tprime = 2 * np.pi * dphi_leg

    def progress_tprime(self, dt, f_tg, swing_stance_speed_ratio):
        """ swing_stance_speed_ratio is Beta in the paper
            set by policy at each step, but default is 1/3
            delta_period is just dt

            This moves the phase based on delta
            (which is one parameter * delta_time_step).
            The speed of the phase depends on swing vs stance phase
            (phase > np.pi or phase < np.pi)  which has different speeds.
        """
        time_mult = dt * f_tg
        stance_speed_coef = (swing_stance_speed_ratio +
                             1) * 0.5 / swing_stance_speed_ratio
        swing_speed_coef = (swing_stance_speed_ratio + 1) * 0.5
        if self.tprime < np.pi:  # Swing
            delta_phase_multiplier = stance_speed_coef * 2.0 * np.pi
            self.tprime += time_mult * delta_phase_multiplier
        else:  # Stance
            delta_phase_multiplier = swing_speed_coef * 2.0 * np.pi
            self.tprime += time_mult * delta_phase_multiplier

        self.tprime = np.fmod(self.tprime, 2.0 * np.pi)


class TrajectoryGenerator():
    def __init__(self,
                 center_swing=0.0,
                 amplitude_extension=0.5,
                 amplitude_lift=1.0,
                 intensity=1.0,
                 dphi_leg=0.0,
                 swing_stance_speed_ratio=1.0 / 3.0):
        # Cyclic Integrator
        self.CI = CyclicIntegrator(dphi_leg)
        self.center_swing = center_swing
        self.amplitude_extension = amplitude_extension
        self.amplitude_lift = amplitude_lift
        self.intensity = intensity

    def get_state_base_on_phase(self):
        return [(np.cos(self.CI.tprime) + 1) / 2.0,
                (np.sin(self.CI.tprime) + 1) / 2.0]

    def get_swing_extend_based_on_phase(self,
                                        amplitude_swing=0.0,
                                        center_extension=0.0,
                                        theta=0.0):
        """ Eqn 2 in paper appendix

            Cs: center_swing
            Ae: amplitude_extension
            theta: extention difference between end of swing and stance (good for climbing)

            POLICY PARAMS:
                h_tg = center_extension
                alpha_th = amplitude_swing
        """
        # Set amplitude_extension
        amplitude_extension = self.amplitude_extension
        if self.CI.tprime > np.pi:
            amplitude_extension = self.amplitude_lift

        # E(t)
        extend = center_extension + (amplitude_extension * np.sin(
            self.CI.tprime)) * self.intensity + theta * np.cos(self.CI.tprime)
        # S(t)
        swing = self.center_swing + amplitude_swing * np.cos(self.CI.tprime)
        swing *= self.intensity
        return swing, extend
