ALLOCATE_LUA = """
local node_key = KEYS[1]
if redis.call('EXISTS', node_key) == 0 then
    return -3
end
local healthy = redis.call('HGET', node_key, 'healthy')
if healthy ~= 'true' then
    return -1
end
local capacity = tonumber(redis.call('HGET', node_key, 'capacity'))
local used = tonumber(redis.call('HGET', node_key, 'used'))
if used >= capacity then
    return -2
end
redis.call('HINCRBY', node_key, 'used', 1)
return 0
"""
