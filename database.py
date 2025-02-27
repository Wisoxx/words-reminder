import sqlite3
import os
import time
from collections import namedtuple

from logger import setup_logger

MAX_RETRIES = 3
INITIAL_DELAY = 0.5

logger = setup_logger(__name__)


class Connection:
    def __init__(self, database_name, timeout):
        db_path = os.path.expanduser(f"~/mysite/{database_name}")
        logger.info(f"Connecting to database at {db_path}...")
        self.connection = sqlite3.connect(db_path, timeout=timeout)
        self.connection.execute('PRAGMA foreign_keys=ON')

    def __del__(self):
        logger.info("Disconnecting from database...")
        self.connection.close()

    def __getattr__(self, name):
        return getattr(self.connection, name)


class CursorError:
    def __init__(self, error=None):
        self.rowcount = -1
        self.lastrowid = 0
        self.arraysize = 0
        self.description = None
        self.connection = None
        self.error = str(error)

    def execute(self, sql, parameters=()):
        pass

    def executemany(self, sql, parameters):
        pass

    def fetchone(self):
        return None

    def fetchmany(self, size=None):
        return []

    def fetchall(self):
        return []

    def close(self):
        pass

    def setinputsizes(self, sizes):
        pass

    def setoutputsize(self, size, column=None):
        pass


class Database:
    table_name = ""
    create_table_query = ""
    columns = ()

    connection = Connection('data.db', timeout=5)

    @classmethod
    def execute_query(cls, query: str, params: list or tuple = (), multiple: bool = False, retrying: bool = False):
        """Executes a given SQLite query with optional parameters. Returns number of affected rows or fetched data"""
        logger.debug(f"Executing query: {query, params}")
        connection = cls.connection
        cursor = connection.cursor()

        retry = False
        attempt = 0
        while attempt < MAX_RETRIES:
            # execute query
            try:
                if params:
                    if multiple:
                        logger.debug("Executing multiple")
                        cursor.executemany(query, params)
                    else:
                        logger.debug("Executing single")
                        cursor.execute(query, tuple(params))
                else:
                    logger.debug("Executing with no parameters")
                    cursor.execute(query)

                if not query.strip().upper().startswith("SELECT"):
                    connection.commit()
                    logger.debug(f"Query executed successfully")
                    return cursor
                else:
                    results = cursor.fetchall()  # Return results for SELECT statements
                    logger.debug(f"Query executed successfully. Results: {results}")
                    return results

            # handle errors
            except sqlite3.OperationalError as e:
                error_message = str(e)

                if "database is locked" in error_message:
                    logger.warning(f"Database is locked, retrying... Attempt {attempt + 1}/{MAX_RETRIES}")
                    time.sleep(INITIAL_DELAY * (2 ** attempt))
                    attempt += 1
                    retry = True
                    continue

                elif "no such table" in error_message and not retrying:
                    logger.warning(f"Table not found: {cls.table_name}. Attempting to create the table...")
                    try:
                        cls.create_table()  # Attempt to create the table
                        logger.info("Table created successfully. Retrying the original query...")
                    except sqlite3.Error as create_e:
                        logger.critical(f"Failed to create table: {create_e}", exc_info=True)
                        raise create_e

                    # Retry the original query after creating the table
                    return cls.execute_query(query, params, multiple, retrying=True)

                else:
                    logger.exception(f"OperationalError: {error_message}")
                    raise e

            except sqlite3.IntegrityError as e:
                logger.warning(f"IntegrityError: {str(e)}")
                return CursorError("IntegrityError")  # Handle duplicate entries and other integrity issues

            except sqlite3.DatabaseError as e:
                logger.critical(f"DatabaseError: {str(e)}", exc_info=True)
                raise e

            finally:
                if not retry:
                    cursor.close()
                retry = False

        logger.error(f"Max retries exceeded")
        return CursorError("OperationalError")

    @classmethod
    def validate_columns(cls, conditions: dict or list or tuple) -> None:
        invalid_columns = [col for col in conditions if col not in cls.columns]
        if invalid_columns:
            logger.error(f"Table {cls.table_name} has no such columns: {invalid_columns}")
            raise ValueError(f"Invalid column(s): {', '.join(invalid_columns)}")

    @classmethod
    def create_table(cls) -> None:
        """Create the table specified by class, and create indexes if defined."""
        cls.execute_query(cls.create_table_query)

    @classmethod
    def add(cls, data: dict, replace: bool = False) -> tuple[bool, int]:
        """
        Inserts a new record into the table. Column names and values are passed as a
        dictionary. Optionally, use "INSERT OR REPLACE" to handle unique constraint
        conflicts.

        :param data: dict of data to be inserted
        :param replace: bool whether to replace existing records
        :return: bool indicating success or failure
        """
        if not data:
            raise ValueError("No data provided for insertion.")
        cls.validate_columns(data)

        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))

        if replace:
            query = f"INSERT OR REPLACE INTO {cls.table_name} ({columns}) VALUES ({placeholders})"
        else:
            query = f"INSERT INTO {cls.table_name} ({columns}) VALUES ({placeholders})"

        cursor = cls.execute_query(query, data.values())

        return cursor.rowcount > 0, cursor.lastrowid

    @classmethod
    def add_bulk(cls, data: dict or list[dict], replace: bool = False) -> tuple[bool, int]:
        """
        Inserts a new record into the table. Column names and values are passed as a
        dictionary. Optionally, use "INSERT OR REPLACE" to handle unique constraint
        conflicts.

        :param data: dict of data to be inserted
        :param replace: bool whether to replace existing records
        :return: bool indicating success or failure
        """
        if not data:
            raise ValueError("No data provided for insertion.")

        if isinstance(data, dict):
            data = [data]  # Convert single dict to list for consistency

        values = []
        for row in data:
            cls.validate_columns(row)
            values.append(tuple(row.values()))

        columns = ', '.join(data[0].keys())  # assuming all rows have the same structure
        placeholders = ', '.join('?' * len(data[0]))

        if replace:
            query = f"INSERT OR REPLACE INTO {cls.table_name} ({columns}) VALUES ({placeholders})"
        else:
            query = f"INSERT INTO {cls.table_name} ({columns}) VALUES ({placeholders})"

        cursor = cls.execute_query(query, values, multiple=True)

        return cursor.rowcount > 0

    @classmethod
    def get(cls, conditions: dict = None, limit: int = None, offset: int = None,
            order_by: str = None, sort_direction: str = 'ASC', include_column_names=False, custom_select=None,
            force_2d=False) -> list or tuple or namedtuple or None:
        """
        Fetch records from the database with optional conditions, limit, offset, and ordering.

        :param conditions: A dictionary of WHERE conditions (optional)
        :param limit: The maximum number of records to retrieve (optional)
        :param offset: The number of records to skip (optional)
        :param order_by: The column to order by (optional)
        :param sort_direction: 'ASC' or 'DESC' to define sorting direction (default: 'ASC')
        :param include_column_names: Whether to return column names with values (default: False)
        :param custom_select: A custom SELECT query to override the default (SELECT * FROM cls.table_name) (optional)
        :param force_2d: When false, a singular row will be returned as tuple instead of a tuple inside a list (default:
         False)
        :return: List of fetched records
        """

        query = custom_select if custom_select else f"SELECT * FROM {cls.table_name}"
        params = []

        # Add WHERE conditions if provided
        if conditions:
            cls.validate_columns(conditions)

            where_clause = ' AND '.join([f"{key} = ?" for key in conditions.keys()])
            query += f" WHERE {where_clause}"
            params.extend(conditions.values())

        # Add ORDER BY if provided
        if order_by:
            if order_by not in cls.columns:
                raise ValueError(f"Invalid column for ordering: {order_by}")
            if sort_direction.upper() not in ['ASC', 'DESC']:
                raise ValueError("Sort direction must be either 'ASC' or 'DESC'")
            query += f" ORDER BY {order_by} {sort_direction.upper()}"

        # Add LIMIT and OFFSET if provided
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        if offset:
            query += " OFFSET ?"
            params.append(offset)

        rows = cls.execute_query(query, params)

        if include_column_names:
            if not rows:
                return []

            if not custom_select:
                Row = namedtuple('Row', cls.columns)
            else:
                columns_part = custom_select.split('FROM')[0].replace('SELECT', '').strip()
                # Split by commas and trim spaces
                column_names = [col.strip() for col in columns_part.split(',')]
                # Map each row's values to the corresponding column name
                Row = namedtuple('Row', column_names)
            rows = [Row(*row) for row in rows]

        if len(rows) == 1 and not force_2d:  # return as tuple instead of list of tuples
            return rows[0]

        return rows

    @classmethod
    def count_where(cls, conditions: dict):
        """Counts the number of records that meet the given conditions."""
        if not conditions:
            raise ValueError("No conditions provided for count.")
        cls.validate_columns(conditions)

        where_clause = ' AND '.join([f"{key} = ?" for key in conditions])
        query = f"SELECT COUNT(*) FROM {cls.table_name} WHERE {where_clause}"
        result = cls.execute_query(query, conditions.values())
        return result[0][0] if result else 0

    @classmethod
    def set(cls, conditions: dict, new_values: dict):
        """Updates records that meet the given conditions with new values."""
        if not conditions:
            raise ValueError("No conditions provided for identifying the row(s).")
        if not new_values:
            raise ValueError("No new values provided for update.")

        cls.validate_columns(conditions)
        cls.validate_columns(new_values)

        set_clause = ', '.join(f"{key} = ?" for key in new_values)
        where_clause = ' AND '.join(f"{key} = ?" for key in conditions)
        query = f"UPDATE {cls.table_name} SET {set_clause} WHERE {where_clause}"
        cursor = cls.execute_query(query, (*new_values.values(), *conditions.values()))
        return cursor.rowcount > 0

    @classmethod
    def delete(cls, conditions: dict):
        """Deletes records that meet the given conditions."""
        if not conditions:
            raise ValueError("No conditions provided for identifying the row(s) to delete.")
        cls.validate_columns(conditions)

        where_clause = ' AND '.join(f"{key} = ?" for key in conditions)
        query = f"DELETE FROM {cls.table_name} WHERE {where_clause}"
        cursor = cls.execute_query(query, tuple(conditions.values()))
        return cursor.rowcount > 0


class Users(Database):
    table_name = "users"
    columns = ["user_id", "username", "language", "timezone", "current_vocabulary_id", "hide_meaning"]
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    language TEXT,
    timezone INTEGER DEFAULT 0,
    current_vocabulary_id INTEGER,
    hide_meaning INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (current_vocabulary_id) REFERENCES vocabularies(vocabulary_id)
    );
    '''


class Vocabularies(Database):
    table_name = "vocabularies"
    columns = ["vocabulary_id", "user_id", "vocabulary_name"]

    @classmethod
    def create_table(cls) -> None:
        create_table_query = """
            CREATE TABLE IF NOT EXISTS vocabularies (
            vocabulary_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            vocabulary_name TEXT NOT NULL,
            UNIQUE(vocabulary_name, user_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """
        cls.execute_query(create_table_query)

        trigger_delete_vocabulary = """
        CREATE TRIGGER update_current_vocabulary_after_delete
        AFTER DELETE ON vocabularies
        FOR EACH ROW
        BEGIN
            -- Update current_vocabulary_id to another existing vocabulary or leave as NULL
            UPDATE users
            SET current_vocabulary_id = (
                SELECT vocabulary_id
                FROM vocabularies
                WHERE user_id = OLD.user_id
                LIMIT 1
            )
            WHERE current_vocabulary_id = OLD.vocabulary_id;
        END;
        """
        cls.execute_query(trigger_delete_vocabulary)

        trigger_insert_vocabulary = """
        CREATE TRIGGER set_current_vocabulary_after_insert
        AFTER INSERT ON vocabularies
        FOR EACH ROW
        BEGIN
            UPDATE users
            SET current_vocabulary_id = NEW.vocabulary_id
            WHERE user_id = NEW.user_id;
        END;
        """
        cls.execute_query(trigger_insert_vocabulary)


class Words(Database):
    table_name = "words"
    columns = ["word_id", "user_id", "vocabulary_id", "word", "meaning", "timestamp"]
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS words (
    word_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    vocabulary_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    meaning TEXT,
    timestamp INTEGER NOT NULL,
    UNIQUE(word, vocabulary_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (vocabulary_id) REFERENCES vocabularies(vocabulary_id) ON DELETE CASCADE
    );
    '''


class Reminders(Database):
    table_name = "reminders"
    columns = ["reminder_id", "user_id", "vocabulary_id", "time", "number_of_words"]
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS reminders (
        reminder_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        vocabulary_id INTEGER NOT NULL,
        time TEXT NOT NULL,
        number_of_words INTEGER NOT NULL,
        UNIQUE(user_id, time),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (vocabulary_id) REFERENCES vocabularies(vocabulary_id) ON DELETE CASCADE
    );
    '''


class Temp(Database):
    table_name = "temp"
    columns = ["user_id", "key", "value"]
    create_table_query = """
    CREATE TABLE IF NOT EXISTS temp (
        user_id INTEGER,
        key TEXT,
        value TEXT,
        PRIMARY KEY (user_id, key),
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """

    @classmethod
    def add(cls, data: dict, replace: bool = True):
        return super().add(data, replace=replace)
