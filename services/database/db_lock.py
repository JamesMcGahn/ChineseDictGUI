from PySide6.QtCore import QMutex

import services.logger.logger

global_db_mutex = QMutex()
services.logger.logger.Logger().insert(
    f"Created global mutex: {id(global_db_mutex)}", "INFO", True
)
