import threading

from mini_framework.databases.config import DatabaseConfig
from mini_framework.databases.conn_managers.conn_metrics import SlaveMetrics
from mini_framework.databases.conn_managers.utilities import create_db_session_factory


class LoadBalancer:
    def __init__(self, slaves_dbs_config: list[DatabaseConfig]):
        """
        Initialize the load balancer with a list of slave sessions.
        """
        self._slaves = []
        for slave_db_config in slaves_dbs_config:
            db_session_factory = create_db_session_factory(slave_db_config)
            self._slaves.append(SlaveMetrics(db_session_factory))
        self._lock = threading.Lock()

    def get_session_factory(self):
        """
        Select the slave session with the lowest current load.
        """
        with self._lock:
            # 选择当前负载最小的从库
            # 可以根据连接数或响应时间来选择
            least_loaded_slave = min(self._slaves, key=lambda x: x.connection_count)
            least_loaded_slave.increment_connections()
            return least_loaded_slave.session_factory

    def release_session(self, session):
        """
        Release a session by decrementing its connection count.
        """
        with self._lock:
            # 找到对应的会话并减少连接数
            for slave in self._slaves:
                if slave.session_factory == session:
                    slave.decrement_connections()
                    break
