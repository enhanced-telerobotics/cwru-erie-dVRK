import time
import crtk
import dvrk
import numpy as np


ECM_CONFIG = np.deg2rad([0, -15, np.rad2deg(0.02), 0])
PSM1_CONFIG = np.deg2rad([42, 5.4, np.rad2deg(0.15), 46, -43, 0])
PSM2_CONFIG = np.deg2rad([-38, 3.5, np.rad2deg(0.145), -56, -40, 0])


def main():
    ral = crtk.ral('dvrk_python_node')
    ral.check_connections()
    ral.spin()

    console = dvrk.console(ral, 'console')

    ecm = dvrk.ecm(ral, 'ECM')
    psm1 = dvrk.psm(ral, 'PSM1')
    psm2 = dvrk.psm(ral, 'PSM2')
    mtmr = dvrk.mtm(ral, 'MTMR')
    mtml = dvrk.mtm(ral, 'MTML')

    arms = [ecm, psm1, psm2, mtmr, mtml]

    while not is_homed(arms):
        home_all(console)
        time.sleep(2)

    if is_homed(arms):
        # Move the arms to their initial positions
        while not check(arms):
            move(arms)
            time.sleep(5)
        
        # Start the teleoperation
        console.teleop_start()
        console.teleop_set_scale(0.3)

    ral.shutdown()


def home_all(console):
    console.power_on()
    console.home()

def is_homed(arms):
    return all(arm.is_homed() for arm in arms)

def move(arms):
    arms[0].move_jp(ECM_CONFIG)
    arms[1].move_jp(PSM1_CONFIG)
    arms[1].jaw.open()
    arms[2].move_jp(PSM2_CONFIG)
    arms[2].jaw.open()

def check(arms, threshold: float = 5e-2) -> bool:
    ecm_jp = arms[0].measured_jp()
    psm1_jp = arms[1].measured_jp()
    psm2_jp = arms[2].measured_jp()

    if (
        np.abs(ecm_jp - ECM_CONFIG).sum() < threshold and
        np.abs(psm1_jp - PSM1_CONFIG).sum() < threshold and
        np.abs(psm2_jp - PSM2_CONFIG).sum() < threshold
    ):
        return True

    return False


if __name__ == "__main__":
    main()
