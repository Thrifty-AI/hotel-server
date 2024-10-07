import logging
import codecs
import sys

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a UTF-8 encoded stream wrapper for stdout
utf8_stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

console_handler = logging.StreamHandler(utf8_stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# get root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

openai_logger = logging.getLogger("Assitant")
openai_logger.setLevel(logging.ERROR)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# logger.addHandler(openai_logger)

logging.info("logger is ready !")
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# Set the logging level to WARNING to ignore INFO and DEBUG logs

urllib3_logger = logging.getLogger("urllib3")
urllib3_logger.setLevel(logging.CRITICAL)
