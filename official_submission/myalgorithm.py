# myalgorithm.py
# OGC 2026 official-safe fallback.
#
# The first official email evaluation rejected the portfolio candidate with
# "Tried to use unavailable Python package or function" on every problem.
# This version intentionally follows the organizer baseline template closely:
# one public entry point, no top-level imports, and only the official
# baseline_greedy module imported inside algorithm().


def algorithm(prob_info, timelimit=60):
    """Return a valid official-baseline solution."""
    import baseline_greedy

    return baseline_greedy.greedyalgorithm(prob_info, timelimit)
