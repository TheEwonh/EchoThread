import aiosqlite, logging
from datetime import datetime

DB_PATH = "database.db"

logger = logging.getLogger("Database")
async def setup():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bans(
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                moderator TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS appeal_cd(
                user_id INTEGER PRIMARY KEY,
                cooldown INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS appeals(
                user_id INTEGER PRIMARY KEY,
                message_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mutes(
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                time INTEGER,
                moderator TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warns(
                warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reason TEXT,
                severity INTEGER,
                time INTEGER,
                moderator_id INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS levels(
                user_id INTEGER PRIMARY KEY,
                experience INTEGER,
                exp_levelup INTEGER,
                level INTEGER,
                addition_exp INTEGER
            )
        """)
        await db.commit()
        logger.info("Tables initialized")

async def setInfo(action:str, *args):
    match action:
        case "bans":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    INSERT INTO bans(user_id, reason, moderator)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        reason = excluded.reason,
                        moderator = excluded.moderator;
                """, (int(args[0]), str(args[1]), str(args[2]))
                )
                await db.commit()
                logger.info(f"Set {int(args[0])} to ban table with reason {str(args[1])}")
        case "appeal_cd":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    INSERT INTO appeal_cd(user_id, cooldown)
                    VALUES (?, ?)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        cooldown = excluded.cooldown;
                """, (int(args[0]), int(args[1]))
                )
                await db.commit()
                logger.info(f"Set {int(args[0])} to appeal_cd table with cooldown till {int(args[1])} - {datetime.fromtimestamp(int(args[1]))}")
        case "appeals":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    INSERT INTO appeals(user_id, message_id)
                    VALUES (?, ?)
                """, (int(args[0]), int(args[1]))
                )
                await db.commit()
                logger.info(f"Set {int(args[0])} to appeals table with user_id {int(args[1])}")
        case "mutes":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    INSERT INTO mutes(user_id, reason, time, moderator)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        reason = excluded.reason,
                        time = excluded.time,
                        moderator = excluded.moderator;
                """, (int(args[0]), str(args[1]), int(args[2]), str(args[3]))
                )
                await db.commit()
                logger.info(f"Set {int(args[0])} to mutes table with reason {str(args[1])} till {str(args[2])} by {str(args[3])}")
        case "warns":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    INSERT INTO warns(user_id, reason, severity, time, moderator_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (int(args[0]), str(args[1]), int(args[2]), int(args[3]), int(args[4]))
                )
                await db.commit()
                logger.info(f"Set {int(args[0])} to warns table with reason {str(args[1])} (severity level {int(args[2])}) till {int(args[3])} by {int(args[4])}")
        case "levels":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    INSERT INTO levels(user_id, experience, exp_levelup, level, addition_exp)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        exp_levelup = excluded.exp_levelup,
                        experience = excluded.experience,
                        level = excluded.level,
                        addition_exp = excluded.addition_exp;
                """, (int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4]))
                )
                await db.commit()

async def get(action, value):
    match action:
        case "bans":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT * FROM bans
                    WHERE user_id = ?
                """, (value,))
                row = await cursor.fetchone()
                logger.info(f"Get method was fired for ban table - {row}")

                return row
        case "appeal_cd":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT * FROM appeal_cd
                    WHERE user_id = ?
                """, (value,))
                row = await cursor.fetchone()
                logger.info(f"Get method was fired for appeal_cd table - {row}")

                return row
        case "appeals":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT * FROM appeals
                    WHERE user_id = ?
                """, (value,))
                row = await cursor.fetchone()
                logger.info(f"Get method was fired for appeals table - {row}")

                return row
        case "appeals_bymessage":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT * FROM appeals
                    WHERE message_id = ?
                """, (value,))
                row = await cursor.fetchone()
                logger.info(f"Get method was fired for appeals table - {row}")

                return row
        case "mutes":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT * FROM mutes
                    WHERE user_id = ?
                """, (value,))
                row = await cursor.fetchone()
                logger.info(f"Get method was fired for mutes table - {row}")

                return row
        case "expired_mutes":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT user_id, time FROM mutes
                    WHERE time <= ?
                """, (value,))
                row = await cursor.fetchall()

                return row
        case "warns":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT * FROM warns
                    WHERE user_id = ?
                """, (value,))
                row = await cursor.fetchall()
                logger.info(f"Get method was fired for warns table - {row}")

                return row
        case "expired_warns":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT warn_id, user_id, time FROM warns
                    WHERE time <= ?
                """, (value,))
                row = await cursor.fetchall()

                return row
        case "levels":
            async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute("""
                    SELECT * FROM levels
                    WHERE user_id = ?
                """, (value,))

                return await cursor.fetchone()
            
async def delete(action, value: int):
    match action:
        case "bans":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    DELETE FROM bans
                    WHERE user_id = ?
                """, (value,))

                logger.info(f"Deleted data from ban table - user_id:{value}")
                await db.commit()
        case "appeal_cd":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    DELETE FROM appeal_cd
                    WHERE user_id = ?
                """, (value,))

                logger.info(f"Deleted data from appeal_cd table - user_id:{value}")
                await db.commit()
        case "appeals":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    DELETE FROM appeals
                    WHERE user_id = ?
                """, (value,))

                logger.info(f"Deleted data from appeals table - user_id:{value}")
                await db.commit()
        case "mutes":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    DELETE FROM mutes
                    WHERE user_id = ?
                """, (value,))

                logger.info(f"Deleted data from mutes table - user_id:{value}")
                await db.commit()
        case "warns":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    DELETE FROM warns
                    WHERE warn_id = ?
                """, (value,))

                logger.info(f"Deleted data from warns table - warn_id:{value}")
                await db.commit()
        case "levels":
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    DELETE FROM levels
                    WHERE user_id = ?
                """, (value,))

                logger.info(f"Deleted data from levels table - user_id:{value}")
                await db.commit()

async def getLeaderboard(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, level, experience
            FROM levels
            ORDER BY level DESC, experience DESC
            LIMIT ?
        """, (limit,))

        return await cursor.fetchall()

async def getLeaderboardPlace(level, experience):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
        SELECT COUNT(*)
        FROM levels
        WHERE level > ?
        OR (level = ? AND experience > ?)
        """, (level, level, experience))

        higher_players = (await cursor.fetchone())[0]

        return higher_players + 1