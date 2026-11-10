"""Version-pinned experimental Native scout throughput -> grid resolution.

Kept separate from v298 so sealed pre-existing v298 sessions continue to
verify the unchanged v298 source SHA. Only explicit *multiregion* sessions
use this updated 22/31/41 point selector, with its own source SHA in seal.
No fabricated wall times: ONLY verified NEW_NATIVE scout samples are input.
"""
import math
import statistics

import v298_adaptive_percent_grid as grid

SCHEMA="v300_multiregion_measured_throughput_resolution_v1"


def choose_points_from_throughput(native_scout_seconds, *,
                                   remaining_calls, seconds_available=None,
                                   confirmation_to_scout_iterations=1.0):
    """Opt-in resolution based on actual fresh-scout wall time and headroom.

    Eleven is the initial number of normalized per-stat reference points,
    not eleven Native candidates. A fast 200-call session may choose 22,
    without exhausting all lattice candidates. No measured wall time ->11.
    """
    grid._need(type(remaining_calls) is int and remaining_calls >= 0,
               "PERCENT_GRID_REMAINING_CALLS")
    grid._need(seconds_available is None or
               (type(seconds_available) in (int, float) and
                math.isfinite(seconds_available) and seconds_available > 0),
               "PERCENT_GRID_WALL_BUDGET")
    grid._need(type(confirmation_to_scout_iterations) in (int, float) and
               math.isfinite(confirmation_to_scout_iterations) and
               confirmation_to_scout_iterations >= 1,
               "PERCENT_GRID_ITERATION_RATIO")
    sample=[float(t) for t in native_scout_seconds
            if type(t) in (int,float) and math.isfinite(t) and t>0]
    if len(sample)<3 or seconds_available is None:
        return 11
    if remaining_calls<24:
        return 7
    scout_time=statistics.median(sample[-11:])
    # Reserve 20% of remaining calls for confirmation iteration requests.
    # This 20% is an experimental planning margin, not statistical certainty.
    forecast=(scout_time*remaining_calls*
              (0.8+0.2*confirmation_to_scout_iterations))
    headroom=seconds_available/max(forecast,1.e-9)
    if headroom<0.50:
        return 5
    if headroom<0.85:
        return 7
    if headroom<1.40:
        return 11
    if headroom<2.25:
        return 15
    if headroom<4.00:
        return 22
    if remaining_calls>=120 and headroom>=7.00:
        return 41
    if remaining_calls>=80:
        return 31
    return 22
