from ..mq.topic import TaskTopic
from ...design_patterns.singleton import singleton
from ...utils.log import logger


@singleton
class TaskApplication(object):
    """
    TaskApplication 类, 用于创建 App 实例
    """

    def __init__(self, *args, **kwargs):
        """
        初始化 TaskApplication
        :param args:
        :param kwargs:
        """

        self.__topic = None
        from ..config import task_service_config
        from ...message_queue.config import kafka_config

        self.__app_id = task_service_config.app_id
        if not self.__app_id:
            raise ValueError("app_id configuration is required")
        self.__config = task_service_config
        self.__kafka_config = kafka_config
        self.__task_consumer = None

        from .context import ApplicationContext

        self.__context = ApplicationContext()
        self.__context.set("app", self)
        from ..consumers.task_events import TaskEvents

        self.__task_events = TaskEvents()
        self.args = args
        self.kwargs = kwargs

    @property
    def app_id(self):
        return self.__app_id

    @property
    def context(self):
        return self.__context

    @property
    def config(self):
        return self.__config

    @property
    def kafka_config(self):
        return self.__kafka_config

    @property
    def task_consumer(self):
        return self.__task_consumer

    async def run(self):
        """
        启动 TaskApplication
        :return:
        """
        from ..consumers import TaskConsumer

        logger.info("TaskApplication starting...")
        self.__task_consumer = TaskConsumer(self)
        await self.task_consumer.consume()

    @property
    def task_topic(self) -> TaskTopic:
        if not self.__topic:
            self.__topic = TaskTopic()
        return self.__topic


task_app = TaskApplication()
