import asyncpg, logging, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

pool = None

logger = logging.getLogger("Database")
async def setup():
    global pool

    pool = await asyncpg.create_pool(
        os.getenv("DATABASE_URL")
    )

    async with pool.acquire() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bans(
                user_id BIGINT PRIMARY KEY,
                reason TEXT,
                moderator TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS appeal_cd(
                user_id BIGINT PRIMARY KEY,
                cooldown BIGINT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS appeals(
                user_id BIGING PRIMARY KEY,
                message_id BIGINT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mutes(
                user_id BIGINT PRIMARY KEY,
                reason TEXT,
                time BIGINT,
                moderator TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warns(
                warn_id BIGSERIAL PRIMARY KEY,
                user_id BIGINT,
                reason TEXT,
                severity BIGINT,
                time BIGINT,
                moderator_id BIGINT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS levels(
                user_id BIGINT PRIMARY KEY,
                experience BIGINT,
                exp_levelup BIGINT,
                level BIGINT,
                addition_exp BIGINT
            )
        """)
        
        logger.info("Tables initialized")

async def setInfo(action:str, *args):
    match action:
        case "bans":
            async with pool.acquire() as db:
                await db.execute("""
                    INSERT INTO bans(user_id, reason, moderator)
                    VALUES ($1, $2, $3)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        reason = excluded.reason,
                        moderator = excluded.moderator;
                """, int(args[0]), str(args[1]), str(args[2])
                )
                
                logger.info(f"Set {int(args[0])} to ban table with reason {str(args[1])}")
        case "appeal_cd":
            async with pool.acquire() as db:
                await db.execute("""
                    INSERT INTO appeal_cd(user_id, cooldown)
                    VALUES ($1, $2)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        cooldown = excluded.cooldown;
                """, int(args[0]), int(args[1])
                )
                
                logger.info(f"Set {int(args[0])} to appeal_cd table with cooldown till {int(args[1])} - {datetime.fromtimestamp(int(args[1]))}")
        case "appeals":
            async with pool.acquire() as db:
                await db.execute("""
                    INSERT INTO appeals(user_id, message_id)
                    VALUES ($1, $2)
                """, int(args[0]), int(args[1])
                )
                
                logger.info(f"Set {int(args[0])} to appeals table with user_id {int(args[1])}")
        case "mutes":
            async with pool.acquire() as db:
                await db.execute("""
                    INSERT INTO mutes(user_id, reason, time, moderator)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        reason = excluded.reason,
                        time = excluded.time,
                        moderator = excluded.moderator;
                """, int(args[0]), str(args[1]), int(args[2]), str(args[3])
                )
                
                logger.info(f"Set {int(args[0])} to mutes table with reason {str(args[1])} till {str(args[2])} by {str(args[3])}")
        case "warns":
            async with pool.acquire() as db:
                await db.execute("""
                    INSERT INTO warns(user_id, reason, severity, time, moderator_id)
                    VALUES ($1, $2, $3, $4, $5)
                """, int(args[0]), str(args[1]), int(args[2]), int(args[3]), int(args[4])
                )
                
                logger.info(f"Set {int(args[0])} to warns table with reason {str(args[1])} (severity level {int(args[2])}) till {int(args[3])} by {int(args[4])}")
        case "levels":
            async with pool.acquire() as db:
                await db.execute("""
                    INSERT INTO levels(user_id, experience, exp_levelup, level, addition_exp)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT(user_id)
                    DO UPDATE SET
                        exp_levelup = excluded.exp_levelup,
                        experience = excluded.experience,
                        level = excluded.level,
                        addition_exp = excluded.addition_exp;
                """, int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4])
                )
                
async def get(action, value):
    match action:
        case "bans":
            async with pool.acquire() as db:
                row = await db.fetchrow("""
                    SELECT * FROM bans
                    WHERE user_id = $1
                """, value)
                logger.info(f"Get method was fired for ban table - {row}")

                return row
        case "appeal_cd":
            async with pool.acquire() as db:
                row = await db.fetchrow("""
                    SELECT * FROM appeal_cd
                    WHERE user_id = $1
                """, value)
                logger.info(f"Get method was fired for appeal_cd table - {row}")

                return row
        case "appeals":
            async with pool.acquire() as db:
                row = await db.fetchrow("""
                    SELECT * FROM appeals
                    WHERE user_id = $1
                """, value)
                logger.info(f"Get method was fired for appeals table - {row}")

                return row
        case "appeals_bymessage":
            async with pool.acquire() as db:
                row = await db.fetchrow("""
                    SELECT * FROM appeals
                    WHERE message_id = $1
                """, value)
                logger.info(f"Get method was fired for appeals table - {row}")

                return row
        case "mutes":
            async with pool.acquire() as db:
                row = await db.fetchrow("""
                    SELECT * FROM mutes
                    WHERE user_id = $1
                """, value)
                logger.info(f"Get method was fired for mutes table - {row}")

                return row
        case "expired_mutes":
            async with pool.acquire() as db:
                row = await db.fetch("""
                    SELECT user_id, time FROM mutes
                    WHERE time <= $1
                """, value)

                return row
        case "warns":
            async with pool.acquire() as db:
                rows = await db.fetch("""
                    SELECT * FROM warns
                    WHERE user_id = $1
                """, value)
                logger.info(f"Get method was fired for warns table - {rows}")

                return rows
        case "expired_warns":
            async with pool.acquire() as db:
                rows = await db.fetch("""
                    SELECT warn_id, user_id, time FROM warns
                    WHERE time <= $1
                """, value)

                return rows
        case "levels":
            async with pool.acquire() as db:
                row = await db.fetchrow("""
                    SELECT * FROM levels
                    WHERE user_id = $1
                """, value)

                return row
            
async def delete(action, value: int):
    match action:
        case "bans":
            async with pool.acquire() as db:
                await db.execute("""
                    DELETE FROM bans
                    WHERE user_id = $1
                """, value)

                logger.info(f"Deleted data from ban table - user_id:{value}")
                
        case "appeal_cd":
            async with pool.acquire() as db:
                await db.execute("""
                    DELETE FROM appeal_cd
                    WHERE user_id = $1
                """, value)

                logger.info(f"Deleted data from appeal_cd table - user_id:{value}")
                
        case "appeals":
            async with pool.acquire() as db:
                await db.execute("""
                    DELETE FROM appeals
                    WHERE user_id = $1
                """, value)

                logger.info(f"Deleted data from appeals table - user_id:{value}")
                
        case "mutes":
            async with pool.acquire() as db:
                await db.execute("""
                    DELETE FROM mutes
                    WHERE user_id = $1
                """, value)

                logger.info(f"Deleted data from mutes table - user_id:{value}")
                
        case "warns":
            async with pool.acquire() as db:
                await db.execute("""
                    DELETE FROM warns
                    WHERE warn_id = $1
                """, value)

                logger.info(f"Deleted data from warns table - warn_id:{value}")
                
        case "levels":
            async with pool.acquire() as db:
                await db.execute("""
                    DELETE FROM levels
                    WHERE user_id = $1
                """, value)

                logger.info(f"Deleted data from levels table - user_id:{value}")
                
async def getLeaderboard(limit=10):
    async with pool.acquire() as db:
        rows = await db.fetch("""
            SELECT user_id, level, experience
            FROM levels
            ORDER BY level DESC, experience DESC
            LIMIT $1
        """, limit)

        return rows

async def getLeaderboardPlace(level, experience):
    async with pool.acquire() as db:
        row = await db.fetchrow("""
            SELECT COUNT(*)
            FROM levels
            WHERE level > $1
                OR (level = $1 AND experience > $2)
        """, level, experience)

        higher_players = row[0]

        return higher_players + 1
