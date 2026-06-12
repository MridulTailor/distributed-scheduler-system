from prometheus_client import Gauge

NODE_UTILIZATION = Gauge(
    'node_utilization_percent', 
    'Current resource utilization of a node',
    ['node_id', 'resource_type']
)

HEALTHY_NODES = Gauge(
    'healthy_nodes_total', 
    'Current number of healthy nodes available for scheduling'
)
