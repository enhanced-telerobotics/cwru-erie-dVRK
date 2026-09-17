"""Publish Classic arm mounting transforms from the actual SUJ_Fixed calibration."""
import json
import math
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def quaternion(m):
    # Stable matrix-to-quaternion conversion, xyzw order.
    t = m[0][0] + m[1][1] + m[2][2]
    if t > 0:
        s = 2 * math.sqrt(1 + t)
        return [(m[2][1]-m[1][2])/s, (m[0][2]-m[2][0])/s,
                (m[1][0]-m[0][1])/s, s/4]
    i = max(range(3), key=lambda n: m[n][n])
    j, k = (i+1) % 3, (i+2) % 3
    s = 2 * math.sqrt(1 + m[i][i] - m[j][j] - m[k][k])
    q = [0.0]*4
    q[i], q[j], q[k], q[3] = s/4, (m[j][i]+m[i][j])/s, (m[k][i]+m[i][k])/s, (m[k][j]-m[j][k])/s
    return q


def visualization_pose(z, roll_deg):
    """Approximate world placement, Tz(z) * Rx(roll); not cart calibration."""
    if not (math.isfinite(z) and math.isfinite(roll_deg)):
        raise ValueError('Visualization height and roll must be finite')
    c, s = math.cos(math.radians(roll_deg)), math.sin(math.radians(roll_deg))
    return ((1, 0, 0, 0), (0, c, -s, 0), (0, s, c, z), (0, 0, 0, 1))


def publishers(context):
    with open(LaunchConfiguration('suj_config').perform(context)) as stream:
        config = json.load(stream)
    world_pose = visualization_pose(
        float(LaunchConfiguration('ecm_world_z').perform(context)),
        float(LaunchConfiguration('ecm_mount_roll_deg').perform(context)))
    result = []
    for arm in config['arms']:
        if arm['name'] not in ['ECM', 'PSM1', 'PSM2']:
            continue
        m = arm['measured_cp']
        if (arm['name'] == 'ECM'
                and LaunchConfiguration('generation', default='Classic').perform(context) == 'Classic'):
            # Classic ECM CAD root has its mounting structure along -X;
            # the calibrated arm-base convention places it along -Y, as
            # for the PSMs. Compose on the RIGHT: this is a model-local
            # rotation, not a rotation of the measured base translation.
            # This adapts the visual mounting frame only; the Classic ECM
            # URDF joint-axis conventions need separate FK validation.
            cad_root = ((0, -1, 0, 0), (1, 0, 0, 0),
                        (0, 0, 1, 0), (0, 0, 0, 1))
            m = [[sum(m[i][k] * cad_root[k][j] for k in range(4))
                  for j in range(4)] for i in range(4)]
        # Shared LEFT transform moves/tilts the entire calibrated assembly.
        # The ECM-only CAD correction above stays on the right.
        m = [[sum(world_pose[i][k] * m[k][j] for k in range(4))
              for j in range(4)] for i in range(4)]
        q = quaternion(m)
        args = []
        for key, value in zip(['x', 'y', 'z', 'qx', 'qy', 'qz', 'qw'],
                              [m[0][3], m[1][3], m[2][3]] + q):
            args.extend(['--'+key, str(value)])
        args.extend(['--frame-id', 'world', '--child-frame-id', 'SUJ_'+arm['name']+'_RCM'])
        result.append(Node(package='tf2_ros', executable='static_transform_publisher',
                           name='fixed_base_'+arm['name'], arguments=args))
    return result


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('suj_config', default_value=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'arm', 'suj-fixed.json'))),
        DeclareLaunchArgument('ecm_world_z', default_value='0.3',
                              description='Visualization height in world Z (meters)'),
        DeclareLaunchArgument('ecm_mount_roll_deg', default_value='-45.0',
                              description='Assembly rotation about world +X (degrees, right-hand rule)'),
        OpaqueFunction(function=publishers),
    ])
