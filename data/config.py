from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot token
ADMINS = env.list("ADMINS", subcast=int)  # Adminlar ro'yxati
DB_USER = env.str("DB_USER")  # Database foydalanuvchi nomi
DB_PASS = env.str("DB_PASS")  # Database paroli
DB_NAME = env.str("DB_NAME")  # Database nomi
DB_HOST = env.str("DB_HOST")  # Xosting ip manzili
