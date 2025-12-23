class LessonsDAL:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def insert_word(self, lesson):
        query = "INSERT INTO lessons (provider,url,slug,status,task,lesson_id, title,level,hash_code, storage_path, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        return self.db_manager.execute_write_query(
            query,
            (
                lesson.provider,
                lesson.url,
                lesson.slug,
                lesson.status,
                lesson.task,
                lesson.lesson_id,
                lesson.title,
                lesson.level,
                lesson.hash_code,
                lesson.storage_path,
                lesson.created_at,
                lesson.updated_at,
            ),
        )
