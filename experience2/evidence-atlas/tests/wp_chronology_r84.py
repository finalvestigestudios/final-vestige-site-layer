#!/usr/bin/env python3
"""R84 native WordPress Desk rail admission: photograph-date certainty.

A dated photograph is NOT a timestamp for the Apollo 1 accident. This verifier
returns only reviewed counts/booleans; untrusted browser text never leaves it.
"""
from __future__ import annotations

DATED = ('1966-10-18', '1967-01-03', '1967-01-28', '2017-01-24')
ORDERED_TARGETS = (
    '#fv-ex2-ledger-apollo1-record-03',
    '#fv-ex2-ledger-apollo1-record-02',
    '#fv-ex2-ledger-apollo1-record-05',
    '#fv-ex2-ledger-apollo1-record-04',
    '#fv-ex2-ledger-apollo1-record-06',
)
PORTRAIT = '#fv-ex2-ledger-apollo1-record-01'


def verify_chronology_r84(*, ordered_dates, ordered_targets,
                          same_day_group_count, unresolved_count,
                          unresolved_date, unresolved_target,
                          ordered_portrait_count, rail_warning,
                          unresolved_warning):
    # Fail closed on an invented ordering, dropped record, duplicate, or
    # removed historical caveat. No raw source/URL is in an exception.
    valid = (
        tuple(ordered_dates) == DATED
        and tuple(ordered_targets) == ORDERED_TARGETS
        and type(same_day_group_count) is int and same_day_group_count == 1
        and type(unresolved_count) is int and unresolved_count == 1
        and unresolved_date == '1967-01'
        and unresolved_target == PORTRAIT
        and type(ordered_portrait_count) is int and ordered_portrait_count == 0
        and isinstance(rail_warning, str)
        and 'not events during the fire' in rail_warning.lower()
        and 'their order that day is unknown' in rail_warning.lower()
        and isinstance(unresolved_warning, str)
        and 'cannot be placed before or after' in unresolved_warning.lower()
        and 'unconfirmed' in unresolved_warning.lower()
    )
    if not valid:
        raise AssertionError('R77_R84_CHRONOLOGY_INTEGRITY')
    return {'verified_dated_milestones': 4,
            'source_links_inside_dated_rail': 5,
            'same_day_2017_grouped': True,
            'month_only_crew_portrait_outside_rail': True,
            'provisional_catalog_disclosed': True,
            'reconstructed_fire_timeline': False}
