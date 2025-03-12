from typing import Callable, TypeVar, Optional, List, Dict

T = TypeVar("T")


class CommandLinePrompt:
    def __init__(
        self,
        prompt_message: str,
        validation_function: Callable[[str], T] = None,
        init_value: str = None,
        max_retries: Optional[int] = None,
        default_value: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
    ):
        """
        初始化提示器类。

        :param prompt_message: 提示用户输入信息的文本
        :param validation_function: 用于验证用户输入的函数，必须接受一个字符串参数，输出不受限制
        :param init_value: 初始值，如果不为 None，则直接返回该值
        :param max_retries: 最大重试次数，如果为 None，则允许无限次重试
        :param default_value: 当达到最大重试次数时的默认值，如果存在则使用
        :param dependencies: 依赖项的列表，只有当依赖项的值为 True 时才继续
        """
        self.__prompt_message = prompt_message
        self.__validation_function = validation_function
        self.__max_retries = max_retries
        self.__default_value = default_value
        self.__init_value = init_value
        self.__value = None
        self.__dependencies = dependencies

    @property
    def value(self):
        """
        获取用户输入的值。
        :return:
        """
        return self.__value

    @property
    def dependencies(self):
        """
        获取依赖项的值。
        :return:
        """
        return self.__dependencies

    def prompt(self):
        """
        提示用户输入信息，进行验证，直至通过验证或达到重试限制为止。
        """
        if self.__init_value is not None:
            self.__value = self.__init_value
            return self.__value

        attempts = 0  # 记录重试次数

        while self.__max_retries is None or attempts < self.__max_retries:
            user_input = input(self.__prompt_message)
            try:
                if not self.__validation_function:
                    self.__value = user_input
                    return self.__value
                self.__value = self.__validation_function(user_input)
                return self.__value
            except Exception as e:
                print(f"验证错误：{e}")
                attempts += 1

        # 如果达到最大重试次数
        if self.__default_value is not None:
            print(f"超过重试次数，使用默认值：{self.__default_value}")
            self.__value = self.__default_value
        else:
            raise ValueError("超过重试次数，操作失败。")

        return self.__value


class InputChain:
    def __init__(self, inputs: Dict[str, CommandLinePrompt]):
        """
        初始化职责链管理器。

        :param inputs: 输入步骤的列表
        """
        self.inputs = inputs
        self.__values = {}

    def run(self):
        """
        开始运行输入链条，依次执行各个步骤。
        """
        for key, step in self.inputs.items():
            # 检查依赖项，只有当依赖项的值为 True 时才继续执行此步骤
            if step.dependencies and not all(
                self.__values[dep] for dep in step.dependencies
            ):
                continue
            print(f"处理步骤：{key}")
            self._process_step(key, step)

    def _process_step(self, key, step: CommandLinePrompt):
        """
        执行单个输入步骤的处理逻辑。

        :param step: 需要处理的输入步骤
        """
        value = step.prompt()
        self.__values[key] = value
        print(f"步骤 {key} 完成，值为：{value}")

    def get_value(self, key: str):
        """
        获取输入结果。

        :return: 包含输入结果的字典
        """
        return self.__values.get(key, None)
