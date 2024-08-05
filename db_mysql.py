# db_mysql.py
import logging
from aiomysql import create_pool
from environs import Env
import datetime

env = Env()
env.read_env()

logging.basicConfig(level=logging.INFO)

pool = None

async def init_pool():
    try:
        logging.info("Connecting to MySQL database...")
        global pool
        pool = await create_pool(
            user=env.str("DB_USER"),
            password=env.str("DB_PASS"),
            db=env.str("DB_NAME"),
            host=env.str("DB_HOST"),
            port=env.int("DB_PORT", 3306)  # Default to 3306 if not specified
        )
        logging.info("Successfully connected to the database.")
    except Exception as e:
        logging.error(f"Failed to connect to MySQL database: {e}")
        raise

async def setup():
    await init_pool()


async def get_mahallas_by_id_tuman(id_tuman):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM mahallas WHERE id_tuman = %s", (id_tuman,))
            result = await cur.fetchall()
            return result

from aiomysql import Pool


async def get_mahalla_text(id):
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT mahalla_nomi FROM mahallas WHERE id = %s", (id,))
                result = await cur.fetchone()
                if result:
                    return result[0]
                return "Noma'lum mahalla"
    except Exception as e:
        logging.error(f"Error fetching mahalla name: {e}")
        return "Xatolik yuz berdi"

async def show_tadbirkors_columns():
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tadbirkors' AND TABLE_SCHEMA = %s", (env.str("DB_NAME"),))
            result = await cur.fetchall()
            logging.info(f"Tadbirkors columns: {result}")
            return result

# db_mysql.py

async def get_tadbirkor_by_phone(phone_number):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            query = """
            SELECT 
                ariza_raqam, created_at, familiya, holat_id, id, ilova, inn, ism, javob_sanasi,
                korxona_nomi, mahalla_id, murojat_mazmuni, murojat_sanasi, sharif, tel, tuman_id, updated_at
            FROM tadbirkors
            WHERE tel = %s
            """
            await cur.execute(query, (phone_number,))
            results = await cur.fetchall()
            return results






async def insert_tadbirkor(data):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Generate id in the format id_24
            await cur.execute("SELECT MAX(id) FROM tadbirkors")
            max_id_result = await cur.fetchone()
            if max_id_result[0] is not None:
                new_id = max_id_result[0] + 1
            else:
                new_id = 1  # Start with 1 if no rows exist

            # File path
            ilova_path = f".././upload/files/{data['ilova']}" if data['ilova'] else None

            # Insert data into tadbirkors
            await cur.execute(
                """
                INSERT INTO tadbirkors (
                    id, ariza_raqam, created_at, familiya, ilova, inn, ism,
                    korxona_nomi, mahalla_id, murojat_mazmuni, murojat_sanasi,
                    sharif, tel, tuman_id, holat_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    new_id,
                    f"{new_id}/24",
                    datetime.datetime.now(),
                    data['last_name'],
                    ilova_path,
                    data['inn'],
                    data['first_name'],
                    data['korxona_nomi'],
                    data['mahalla_id'],
                    data['mazmun'],
                    datetime.datetime.now(),
                    data['fathers_name'],
                    data['phone'],
                    data['region_id'],
                    1
                )
            )
            await conn.commit()


async def get_tadbirkors_column_info():
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT 
                    COLUMN_NAME,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    DATA_TYPE
                FROM 
                    INFORMATION_SCHEMA.COLUMNS 
                WHERE 
                    TABLE_NAME = 'tadbirkor_javobs' 
                    AND TABLE_SCHEMA = %s;
                """, (env.str("DB_NAME"),)
            )
            result = await cur.fetchall()
            logging.info(f"Tadbirkors column info: {result}")
            return result

# Call this function to get the table schema info
# await get_tadbirkors_column_info()
