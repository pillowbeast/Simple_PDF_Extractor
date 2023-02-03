"""
Usage: python main.py [-h] [-m MODE] [-n FILE_NAME] [-o OUTPUT_PATH] [-f FLAGS] [-l LANGUAGE] [-s SPEED] [-i ACCESS_KEY_ID] [-k SECRET_ACCESS_KEY]

-m, --mode: Mode (generate text or mp3), one of [txt, mp3]
-n, --file_name: path to file, format: no whitespaces, e.g. "decolonising-peacebuilding_schirch.pdf"
-o, --output_path: name of output file, e.g. "decolonising-peacebuilding_schirch.txt" or "decolonising-peacebuilding_schirch.mp3"
-f, --flags: Additional flags to be removed from the text
-l, --language: Language of the text (default: en)
-s, --speed: Speed of the text (default: 1.0)
-i, --access_key_id: Access key id for AWS
-k, --secret_access_key: Secret access key for AWS
"""
import subprocess

# Steps:
# 1. Create a file with name usage_ind.py
# 2. Copy the following code into the file
# 3. Replace the file_path and output_path with your own inputs
# 4. Run the file

file_path = r'C:\Users\user\input\example.pdf'
output_path = r'C:\Users\user\output\example.txt'
mode = 'txt'                                                            # 'txt' or 'mp3'
language = 'en'                                                         # 'en' or 'de'
speed = 1.0                                                             # 1.0
aws_key_id = ''                                                         
secret_access_key = ''                                                  # AWS key id and secret key

subprocess.run(['python', 'main.py', '-m', mode, '-n', file_path, '-o', output_path, '-l', language, '-s', str(speed), '-i', aws_key_id, '-k', secret_access_key])