import sqlite3


class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def post_exists(self, wall_id):
        """Проверяем, есть ли уже пост в базе"""
        with self.connection:
            try:
                result = self.cursor.execute('SELECT * FROM `posts` WHERE `wall_id` = ?', (wall_id,)).fetchall()
                return bool(len(result))
            except sqlite3.OperationalError:
                self.cursor.execute("""
                                                CREATE TABLE "posts" (
                                                    "id"	INTEGER,
                                                    "owner_id"	TEXT,
                                                    "text"	TEXT,
                                                    "attachment"	TEXT,
                                                    "date"	DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                    "post_id"	INTEGER,
                                                    "wall_id"	TEXT,
                                                    "stop_slovo"	TEXT,
                                                    PRIMARY KEY("id" AUTOINCREMENT)
                                                )""")
                return False

    def add_post(self, post_id, owner_id, text, wall_id, stop):
        """Добавляем новый пост в БД"""
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `posts` (`post_id`, `owner_id`, `text`, `wall_id`, `stop_slovo`) VALUES(?,?,?,?,?)",
                (post_id, owner_id, text, wall_id, stop))