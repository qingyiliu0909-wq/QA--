import logging
import os

code_file = r".\full_code.md"

output_csv = r".\output\output.csv"
if os.path.exists(output_csv):
    os.remove(output_csv)

error_log = r".\output\error.log"
if os.path.exists(error_log):
    os.remove(error_log)
logging.basicConfig(filename=error_log, level=logging.DEBUG)
logger = logging.getLogger(__name__)

