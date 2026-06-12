# scheduler/metrics.py
from prometheus_client import Counter, Histogram

SCHEDULER_ALLOCATIONS_TOTAL = Counter(
    'scheduler_allocations_total', 
    'Total number of successfully allocated jobs'
)

SCHEDULER_REJECTIONS_TOTAL = Counter(
    'scheduler_rejections_total', 
    'Total number of rejected allocation requests',
    ['reason']
)

ALLOCATION_LATENCY_MS = Histogram(
    'allocation_latency_ms', 
    'Latency of the allocation decision in milliseconds',
    buckets=[5, 10, 25, 50, 100, 250, 500, 1000]
)
