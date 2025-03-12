class InvalidExecutorTypeError(Exception):
    def __init__(self, executor, expected_type):
        self.executor = executor
        self.expected_type = expected_type
        super().__init__(
            f"Invalid executor type: {type(executor).__name__}, expected: {expected_type.__name__}"
        )
