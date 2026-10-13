import sqlite3

DB_PATH = "data/vexora.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def setup_database():
    conn = get_connection()

    # ═════════════════════════════════════════════
    # WARNINGS
    # ═════════════════════════════════════════════

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

    # ═════════════════════════════════════════════
    # GUILD SETTINGS
    # ═════════════════════════════════════════════

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

    # ═════════════════════════════════════════════
    # AUTOMOD FORBIDDEN WORDS
    # ═════════════════════════════════════════════

    conn.execute("""
        CREATE TABLE IF NOT EXISTS automod_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(guild_id, word)
        )
    """)

    # ═════════════════════════════════════════════
    # COUNTING
    # ═════════════════════════════════════════════

    conn.execute("""
        CREATE TABLE IF NOT EXISTS counting_settings (
            guild_id INTEGER PRIMARY KEY,

            channel_id INTEGER,
            correct_emoji TEXT,
            wrong_emoji TEXT,
            daily_goal INTEGER DEFAULT 0,

            current_number INTEGER DEFAULT 0,
            last_user_id INTEGER,
            goal_reached_date TEXT,

            high_score INTEGER DEFAULT 0,
            high_score_user_id INTEGER,

            total_correct INTEGER DEFAULT 0,
            total_resets INTEGER DEFAULT 0
        )
    """)

    # ═════════════════════════════════════════════
    # SAFE DATABASE UPGRADES
    # ═════════════════════════════════════════════

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

    counting_columns = {
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(counting_settings)"
        ).fetchall()
    }

    counting_new_columns = {
        "high_score": "INTEGER DEFAULT 0",
        "high_score_user_id": "INTEGER",
        "total_correct": "INTEGER DEFAULT 0",
        "total_resets": "INTEGER DEFAULT 0",
    }

    for column, definition in counting_new_columns.items():

        if column not in counting_columns:

            conn.execute(
                f"""
                ALTER TABLE counting_settings
                ADD COLUMN {column} {definition}
                """
            )

    conn.commit()
    conn.close()


# ═════════════════════════════════════════════
# WARNINGS
# ═════════════════════════════════════════════

def add_warning(
    guild_id,
    user_id,
    moderator_id,
    reason
):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO warnings
        (
            guild_id,
            user_id,
            moderator_id,
            reason
        )
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


def get_warnings(
    guild_id,
    user_id
):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            moderator_id,
            reason,
            created_at
        FROM warnings
        WHERE guild_id = ?
          AND user_id = ?
        ORDER BY id DESC
        """,
        (
            guild_id,
            user_id
        )
    ).fetchall()

    conn.close()

    return rows


def clear_warnings(
    guild_id,
    user_id
):
    conn = get_connection()

    cursor = conn.execute(
        """
        DELETE FROM warnings
        WHERE guild_id = ?
          AND user_id = ?
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


# ═════════════════════════════════════════════
# GUILD SETTINGS
# ═════════════════════════════════════════════

def ensure_guild(guild_id):

    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO guild_settings
        (guild_id)
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

            updates.append(
                f"{column} = ?"
            )

            values.append(value)

    if updates:

        values.append(guild_id)

        conn.execute(
            f"""
            UPDATE guild_settings
            SET {', '.join(updates)}
            WHERE guild_id = ?
            """,
            values
        )

    conn.commit()
    conn.close()


# ═════════════════════════════════════════════
# AUTOMOD SETTINGS
# ═════════════════════════════════════════════

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

            updates.append(
                f"{column} = ?"
            )

            values.append(value)

    if updates:

        values.append(guild_id)

        conn.execute(
            f"""
            UPDATE guild_settings
            SET {', '.join(updates)}
            WHERE guild_id = ?
            """,
            values
        )

    conn.commit()
    conn.close()


def set_automod_role(
    guild_id,
    role_id
):
    ensure_guild(guild_id)

    conn = get_connection()

    conn.execute(
        """
        UPDATE guild_settings
        SET automod_role_id = ?
        WHERE guild_id = ?
        """,
        (
            role_id,
            guild_id
        )
    )

    conn.commit()
    conn.close()


def clear_automod_role(guild_id):

    set_automod_role(
        guild_id,
        None
    )


# ═════════════════════════════════════════════
# AUTOMOD FORBIDDEN WORDS
# ═════════════════════════════════════════════

def add_automod_word(
    guild_id,
    word
):
    """
    Add a forbidden word for a guild.

    Returns:
        True  -> word added
        False -> word already exists
    """

    word = word.strip().lower()

    if not word:
        return False

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO automod_words
            (
                guild_id,
                word
            )
            VALUES (?, ?)
            """,
            (
                guild_id,
                word
            )
        )

        added = cursor.rowcount > 0

        conn.commit()

    finally:

        conn.close()

    return added


def remove_automod_word(
    guild_id,
    word
):
    """
    Remove a forbidden word.

    Returns:
        True  -> removed
        False -> word wasn't found
    """

    word = word.strip().lower()

    conn = get_connection()

    cursor = conn.execute(
        """
        DELETE FROM automod_words
        WHERE guild_id = ?
          AND word = ?
        """,
        (
            guild_id,
            word
        )
    )

    removed = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return removed


def get_automod_words(guild_id):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT word
        FROM automod_words
        WHERE guild_id = ?
        ORDER BY word ASC
        """,
        (guild_id,)
    ).fetchall()

    conn.close()

    return [
        row[0]
        for row in rows
    ]


def clear_automod_words(guild_id):

    conn = get_connection()

    cursor = conn.execute(
        """
        DELETE FROM automod_words
        WHERE guild_id = ?
        """,
        (guild_id,)
    )

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted


# ═════════════════════════════════════════════
# COUNTING
# ═════════════════════════════════════════════

def ensure_counting(guild_id):

    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO counting_settings
        (guild_id)
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
            goal_reached_date,
            high_score,
            high_score_user_id,
            total_correct,
            total_resets
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

            updates.append(
                f"{column} = ?"
            )

            values.append(value)

    if updates:

        values.append(guild_id)

        conn.execute(
            f"""
            UPDATE counting_settings
            SET {', '.join(updates)}
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
            goal_reached_date = ?,
            total_correct = total_correct + 1
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


def update_high_score(
    guild_id,
    score,
    user_id
):
    ensure_counting(guild_id)

    conn = get_connection()

    conn.execute(
        """
        UPDATE counting_settings
        SET
            high_score = ?,
            high_score_user_id = ?
        WHERE guild_id = ?
        """,
        (
            score,
            user_id,
            guild_id
        )
    )

    conn.commit()
    conn.close()


def increment_counting_reset(guild_id):

    ensure_counting(guild_id)

    conn = get_connection()

    conn.execute(
        """
        UPDATE counting_settings
        SET total_resets = total_resets + 1
        WHERE guild_id = ?
        """,
        (guild_id,)
    )

    conn.commit()
    conn.close()


def get_counting_leaderboard(
    guild_id,
    limit=10
):
    ensure_counting(guild_id)

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            high_score_user_id,
            high_score
        FROM counting_settings
        WHERE guild_id = ?
          AND high_score > 0
          AND high_score_user_id IS NOT NULL
        ORDER BY high_score DESC
        LIMIT ?
        """,
        (
            guild_id,
            limit
        )
    ).fetchall()

    conn.close()

    return rows


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