class RetryableAudioError(Exception):
    def __init__(self, message, backoff=15):
        super().__init__(message=message)
        self.backoff = backoff
