class NormalizeError(Exception):
    def __init__(self, messages: list[str]):
        super().__init__(None)
        self.messages = messages

    def __str__(self) -> str:
        return "\n".join(self.messages)
