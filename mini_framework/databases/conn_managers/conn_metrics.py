class SlaveMetrics:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.connection_count = 0
        self.average_response_time = 0

    def update_metrics(self, response_time):
        # 调用此方法来更新每次请求的响应时间
        # 这里简单使用移动平均来计算平均响应时间
        self.average_response_time = (self.average_response_time + response_time) / 2

    def increment_connections(self):
        self.connection_count += 1

    def decrement_connections(self):
        if self.connection_count > 0:
            self.connection_count -= 1
