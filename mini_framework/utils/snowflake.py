import base64
import time

from mini_framework.design_patterns.singleton import singleton
from mini_framework.utils.math import decimal_to_base

lua_script = """
local key = KEYS[1] -- Redis key for the snowflake ID node
local current_timestamp = tonumber(ARGV[1]) -- Current timestamp in milliseconds
local epoch = tonumber(ARGV[2]) -- Custom epoch (starting point for the timestamp)
local sequence_bits = tonumber(ARGV[3]) -- Number of bits for the sequence
local sequence_mask = tonumber(ARGV[4]) -- Sequence mask for ensuring the sequence wraps within its bounds

-- Fetch the last timestamp and sequence from Redis
local last_timestamp = redis.call('hget', key, 'last_timestamp')
local sequence = redis.call('hget', key, 'sequence')

-- Initialize the values if they are not present
if not last_timestamp then
    last_timestamp = -1
else
    last_timestamp = tonumber(last_timestamp)
end

if not sequence then
    sequence = 0
else
    sequence = tonumber(sequence)
end

-- Ensure the current timestamp is not less than the last timestamp
if current_timestamp < last_timestamp then
    return redis.error_reply("System clock moved backwards. Refusing to generate ID.")
end

-- If the current timestamp equals the last timestamp, increment the sequence
if last_timestamp == current_timestamp then
    sequence = bit.band((sequence + 1), sequence_mask)
    if sequence == 0 then
        -- Sequence exhausted for this millisecond, wait for the next millisecond
        current_timestamp = current_timestamp + 1
    end
else
    -- If the timestamp has changed, reset the sequence
    sequence = 0
end

-- Store the new timestamp and sequence in Redis
redis.call('hset', key, 'last_timestamp', current_timestamp)
redis.call('hset', key, 'sequence', sequence)

-- Return the new timestamp and sequence for further processing in the application
return {current_timestamp, sequence}
"""

@singleton
class SnowflakeConfig:
    def __init__(self):
        """
        雪花ID生成器配置
        """
        self.__service_id = -1
        self.__worker_id = -1
        self.__snowflake_bits = 12

    def __init_config(self):
        """
        初始化配置
        """
        from mini_framework.configurations import config_injection

        manager = config_injection.get_config_manager()
        snowflake_conf_dict = manager.get_domain_config("snowflake")
        if not snowflake_conf_dict:
            return
        self.__service_id = snowflake_conf_dict.get("service_id", -1)
        self.__worker_id = snowflake_conf_dict.get("worker_id", -1)
        self.__snowflake_bits = snowflake_conf_dict.get("snowflake_bits", 12)
        if self.__service_id == -1 or self.__worker_id == -1:
            raise ValueError("service_id and worker_id must be provided")

    @property
    def service_id(self):
        """
        服务ID
        """
        if self.__service_id == -1:
            self.__init_config()
        return self.__service_id

    @property
    def worker_id(self):
        """
        工作ID
        """
        if self.__worker_id == -1:
            self.__init_config()
        return self.__worker_id

    @property
    def snowflake_bits(self):
        """
        雪花ID位数
        """
        return self.__snowflake_bits

@singleton
class SnowflakeIdGenerator:
    def __init__(self):
        """
        初始化雪花ID生成器
        """
        self.redis_client = None

    def __initialize(self):
        from mini_framework.cache.manager import redis_client_manager
        snowflake_config = SnowflakeConfig()
        service_id = snowflake_config.service_id
        worker_id = snowflake_config.worker_id
        sequence_bits = snowflake_config.snowflake_bits
        if service_id is None or worker_id is None:
            raise ValueError("service_id and worker_id must be provided")
        if sequence_bits is None:
            sequence_bits = 12
        self.redis_client = redis_client_manager.get_client("snowflake")
        self.data_center_id = service_id
        self.worker_id = worker_id
        self.sequence_bits = sequence_bits
        self.sequence_bits = self.sequence_bits
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)
        self.tw_epoch = int(time.mktime(time.strptime('2020-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')))
        self.timestamp_left_shift = 22  # Example shift value
        self.data_center_id_shift = 17  # Example shift value
        self.worker_id_shift = 12  # Example shift value

        # Lua 脚本，用于 Redis 上生成雪花ID
        self.lua_script = lua_script

        self.script = self.redis_client.register_script(self.lua_script)
        # return sequence_bits, service_id, worker_id

    def generate_id(self):
        """
        生成雪花ID
        """
        if self.redis_client is None:
            self.__initialize()
        if self.redis_client is None:
            raise ValueError("Redis client not initialized")
        timestamp = int(time.time() * 1000)
        result = self.script(keys=[f"snowflake:{self.data_center_id}:{self.worker_id}"],
                             args=[timestamp, self.tw_epoch, self.sequence_bits, self.sequence_mask])

        timestamp, sequence = result
        new_id = ((int(timestamp) - self.tw_epoch) << self.timestamp_left_shift) | \
                 (self.data_center_id << self.data_center_id_shift) | \
                 (self.worker_id << self.worker_id_shift) | int(sequence)
        return new_id

    def generate_short_id(self):
        """
        生成短雪花ID
        :return:
        """
        long_id = self.generate_id()
        short_id = decimal_to_base(long_id, 36)
        if len(short_id) < 13:
            short_id = short_id.zfill(13)
        return short_id

snowflake_id_generator = SnowflakeIdGenerator()