import sqlite3

DB_PATH = "data/vexora.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# =========================================================
# DATABASE SETUP
# =========================================================

def setup_database():

    conn = get_connection()

    # =====================================================
    # WARNINGS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # =====================================================
    # SERVER SETTINGS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id INTEGER PRIMARY KEY,

            welcome_enabled INTEGER DEFAULT 0,
            welcome_channel_id INTEGER,
            welcome_message TEXT,

            welcome_title TEXT,
            welcome_description TEXT,
            welcome_color INTEGER DEFAULT 9844011,
            welcome_thumbnail TEXT,
            welcome_image TEXT,
            welcome_footer TEXT,

            leave_enabled INTEGER DEFAULT 0,
            leave_channel_id INTEGER,
            leave_message TEXT,

            automod_enabled INTEGER DEFAULT 1,
            automod_role_id INTEGER,
            automod_timeout INTEGER DEFAULT 5,
            automod_spam_enabled INTEGER DEFAULT 1,
            automod_repeat_enabled INTEGER DEFAULT 1,
            automod_mention_enabled INTEGER DEFAULT 1
        )
    """)

    # =====================================================
    # COUNTING GAME
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS counting_settings (
            guild_id INTEGER PRIMARY KEY,

            channel_id INTEGER,

            correct_emoji TEXT,
            wrong_emoji TEXT,

            daily_goal INTEGER DEFAULT 0,

            current_number INTEGER DEFAULT 0,
            last_user_id INTEGER,

            goal_reached_date TEXT
        )
    """)

    # =====================================================
    # UPGRADE OLDER DATABASES
    # =====================================================

    columns = {
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(guild_settings)"
        ).fetchall()
    }

    new_columns = {
        "welcome_title": "TEXT",
        "welcome_description": "TEXT",
        "welcome_color": "INTEGER DEFAULT 9844011",
        "welcome_thumbnail": "TEXT",
        "welcome_image": "TEXT",
        "welcome_footer": "TEXT",

        "automod_enabled": "INTEGER DEFAULT 1",
        "automod_role_id": "INTEGER",
        "automod_timeout": "INTEGER DEFAULT 5",
        "automod_spam_enabled": "INTEGER DEFAULT 1",
        "automod_repeat_enabled": "INTEGER DEFAULT 1",
        "automod_mention_enabled": "INTEGER DEFAULT 1",
    }

    for column, definition in new_columns.items():

        if column not in columns:

            conn.execute(
                f"""
                ALTER TABLE guild_settings
                ADD COLUMN {column} {definition}
                """
            )

    conn.commit()
    conn.close()


# =========================================================
# WARNING SYSTEM
# =========================================================

def add_warning(guild_id, user_id, moderator_id, reason):

    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO warnings
        (guild_id, user_id, moderator_id, reason)
        VALUES (?, ?, ?, ?)
        """,
        (
            guild_id,
            user_id,
            moderator_id,
            reason
        )
    )

    warning_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return warning_id


def get_warnings(guild_id, user_id):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT id, moderator_id, reason, created_at
        FROM warnings
        WHERE guild_id = ? AND user_id = ?
        ORDER BY id DESC
        """,
        (
            guild_id,
            user_id
        )
    ).fetchall()

    conn.close()

    return rows


def clear_warnings(guild_id, user_id):

    conn = get_connection()

    cursor = conn.execute(
        """
        DELETE FROM warnings
        WHERE guild_id = ? AND user_id = ?
        """,
        (
            guild_id,
            user_id
        )
    )

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted


# =========================================================
# GUILD SETTINGS
# =========================================================

def ensure_guild(guild_id):

    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO guild_settings (guild_id)
        VALUES (?)
        """,
        (guild_id,)
    )

    conn.commit()
    conn.close()


def get_guild_settings(guild_id):

    ensure_guild(guild_id)

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            welcome_enabled,
            welcome_channel_id,
            welcome_message,
            welcome_title,
            welcome_description,
            welcome_color,
            welcome_thumbnail,
            welcome_image,
            welcome_footer,
            leave_enabled,
            leave_channel_id,
            leave_message
        FROM guild_settings
        WHERE guild_id = ?
        """,
        (guild_id,)
    ).fetchone()

    conn.close()

    return row


def set_welcome_settings(
    guild_id,
    enabled=None,
    channel_id=None,
    message=None,
    title=None,
    description=None,
    color=None,
    thumbnail=None,
    image=None,
    footer=None
):

    ensure_guild(guild_id)

    conn = get_connection()

    updates = []
    values = []

    settings = {
        "welcome_enabled": enabled,
        "welcome_channel_id": channel_id,
        "welcome_message": message,
        "welcome_title": title,
        "welcome_description": description,
        "welcome_color": color,
        "welcome_thumbnail": thumbnail,
        "welcome_image": image,
        "welcome_footer": footer,
    }

    for column, value in settings.items():

        if value is not None:

            updates.append(f"{column} = ?")
            values.append(value)

    if updates:

        values.append(guild_id)

        conn.execute(
            f"""
            UPDATE guild_settings
            SET {", ".join(updates)}
            WHERE guild_id = ?
            """,
            values
        )

    conn.commit()
    conn.close()


# =========================================================
# AUTOMOD SETTINGS
# =========================================================

def get_automod_settings(guild_id):

    ensure_guild(guild_id)

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            automod_enabled,
            automod_role_id,
            automod_timeout,
            automod_spam_enabled,
            automod_repeat_enabled,
            automod_mention_enabled
        FROM guild_settings
        WHERE guild_id = ?
        """,
        (guild_id,)
    ).fetchone()

    conn.close()

    return row


def set_automod_settings(
    guild_id,
    enabled=None,
    role_id=None,
    timeout=None,
    spam_enabled=None,
    repeat_enabled=None,
    mention_enabled=None
):

    ensure_guild(guild_id)

    conn = get_connection()

    updates = []
    values = []

    settings = {
        "automod_enabled": enabled,
        "automod_role_id": role_id,
        "automod_timeout": timeout,
        "automod_spam_enabled": spam_enabled,
        "automod_repeat_enabled": repeat_enabled,
        "automod_mention_enabled": mention_enabled,
    }

    for column, value in settings.items():

        if value is not None:

            updates.append(f"{column} = ?")
            values.append(value)

    if updates:

        values.append(guild_id)

        conn.execute(
            f"""
            UPDATE guild_settings
            SET {", ".join(updates)}
            WHERE guild_id = ?
            """,
            values
        )

    conn.commit()
    conn.close()


def clear_automod_role(guild_id):

    ensure_guild(guild_id)

    conn = get_connection()

    conn.execute(
        """
        UPDATE guild_settings
        SET automod_role_id = NULL
        WHERE guild_id = ?
        """,
        (guild_id,)
    )

    conn.commit()
    conn.close()


# =========================================================
# COUNTING GAME
# =========================================================

def ensure_counting(guild_id):

    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO counting_settings (guild_id)
        VALUES (?)
        """,
        (guild_id,)
    )

    conn.commit()
    conn.close()


def get_counting_settings(guild_id):

    ensure_counting(guild_id)

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            channel_id,
            correct_emoji,
            wrong_emoji,
            daily_goal,
            current_number,
            last_user_id,
            goal_reached_date
        FROM counting_settings
        WHERE guild_id = ?
        """,
        (guild_id,)
    ).fetchone()

    conn.close()

    return row


def set_counting_settings(
    guild_id,
    channel_id=None,
    correct_emoji=None,
    wrong_emoji=None,
    daily_goal=None
):

    ensure_counting(guild_id)

    conn = get_connection()

    updates = []
    values = []

    settings = {
        "channel_id": channel_id,
        "correct_emoji": correct_emoji,
        "wrong_emoji": wrong_emoji,
        "daily_goal": daily_goal,
    }

    for column, value in settings.items():

        if value is not None:

            updates.append(f"{column} = ?")
            values.append(value)

    if updates:

        values.append(guild_id)

        conn.execute(
            f"""
            UPDATE counting_settings
            SET {", ".join(updates)}
            WHERE guild_id = ?
            """,
            values
        )

    conn.commit()
    conn.close()


def update_counting_progress(
    guild_id,
    current_number,
    last_user_id,
    goal_reached_date=None
):

    ensure_counting(guild_id)

    conn = get_connection()

    conn.execute(
        """
        UPDATE counting_settings

        SET
            current_number = ?,
            last_user_id = ?,
            goal_reached_date = ?

        WHERE guild_id = ?
        """,
        (
            current_number,
            last_user_id,
            goal_reached_date,
            guild_id
        )
    )

    conn.commit()
    conn.close()


def reset_counting_progress(guild_id):

    ensure_counting(guild_id)

    conn = get_connection()

    conn.execute(
        """
        UPDATE counting_settings

        SET
            current_number = 0,
            last_user_id = NULL,
            goal_reached_date = NULL

        WHERE guild_id = ?
        """,
        (guild_id,)
    )

    conn.commit()
    conn.close()