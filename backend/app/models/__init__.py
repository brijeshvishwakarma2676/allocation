# Read models — Mavis tables, queried but not owned by this system
from app.models.tower import Tower
from app.models.unit import Unit

# Allocation tables — owned and managed by this system
from app.models.customer import Customer
from app.models.unit_allocation import UnitAllocation
from app.models.cancellation import Cancellation, CancellationStageLog
