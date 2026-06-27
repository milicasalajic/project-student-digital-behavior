"""Svih 10 upita, definisani jednom (DRY) i parametrizovani po verziji šeme.

Svaki builder ima potpis `builder(version) -> (collection_name, pipeline)`:
  - version == "v1": normalizovana šema (sbp-v1) — upiti koriste $lookup join-ove
  - version == "v2": denormalizovana šema (sbp-v2) — jedna kolekcija `students`

Pristup preko `SUITES` koristi benchmark, writer rezultata i dokumentacija.
"""
from queries.psiholog import PSIHOLOG
from queries.savetnik import SAVETNIK

SUITES = {"psiholog": PSIHOLOG, "savetnik": SAVETNIK}

__all__ = ["PSIHOLOG", "SAVETNIK", "SUITES"]
