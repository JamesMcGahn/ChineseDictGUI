from PySide6.QtCore import QMutex

global_db_mutex = QMutex()
print(f"Created global mutex: {id(global_db_mutex)}")
