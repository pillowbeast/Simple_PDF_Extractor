"""
Generates text from pdf and converts it to mp3.

Example usage:
python main.py -m txt -n decolonising-peacebuilding_schirch.pdf
python main.py -m mp3 -n decolonising-peacebuilding_schirch.pdf

More specific information can be added with the following arguments:
-m, --mode: Mode (generate text or mp3), one of [txt, mp3]
-n, --file_name: path to file, format: no whitespaces, e.g. "decolonising-peacebuilding_schirch.pdf"
-o, --output_path: name of output file, e.g. "decolonising-peacebuilding_schirch.txt" or "decolonising-peacebuilding_schirch.mp3"
-f, --flags: Additional flags to be removed from the text
-l, --language: Language of the text (default: en)
-s, --speed: Speed of the text (default: 1.0)
-i, --access_key_id: Access key id for AWS
-k, --secret_access_key: Secret access key for AWS
"""
import argparse
import boto3
import time
import sys

from src.pdfextractor.extraction import Reader

def extract_text(path, output_file='undefined.txt', flags=[]):
    file = Reader()
    pdf = file.read_file(path, flags)
    with open(output_file, 'w+', encoding="utf-8") as f:
        f.write(pdf)

def convert_to_mp3(access_key_id, secret_access_key, path, output_file, language='en', speed=1.0):

    # Create a Boto3 session
    polly = boto3.client('polly', region_name='eu-central-1',  ## specify the server region here
    aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    s3 = boto3.client('s3', region_name='eu-central-1',  ## specify the server region here
    aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    # Define the S3 bucket name
    bucket_name = 'iheid4' ## specify the bucket name (mine is iheid4)

    # Construct the key prefix using the input file name
    key_prefix = f'Audiobook/{path[12:]}'

    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    sequences = split_body_into_sequences(text)
    #print(sequences)
    print(f'Converting {len(sequences)} sequences')
    for i, sequence in enumerate(sequences):
        print(f'Converting sequence {i+1} of {len(sequences)}')
        print(f'Length of sequence: {len(sequence[0])} characters')
        
        # Asynchronous Method
        # Synthesize the speech (upper limit 100'000 characters)
        # TODO: add speed and language
        response = polly.start_speech_synthesis_task(OutputS3BucketName=bucket_name, OutputS3KeyPrefix=key_prefix, Text=sequence[0], VoiceId='Matthew', LanguageCode='en-US', Engine='neural', TextType='text', OutputFormat='mp3')
        task_id = response['SynthesisTask']['TaskId']
        # Wait for the task to complete
        while True:
            response = polly.get_speech_synthesis_task(TaskId=task_id)
            if response['SynthesisTask']['TaskStatus'] == 'completed':
                break
            time.sleep(1)
        # Save the synthesized speech to an audio file
        output_uri = response['SynthesisTask']['OutputUri']
        # Extract the bucket name
        bucket_name = output_uri.split('/')[3]
        print(bucket_name)
        # Extract the file name
        file_name = output_uri.split('/', 4)[4]
        print(file_name)
        # Download the file
        s3.download_file(bucket_name, file_name, output_file)
        # with open(output_file, 'w+') as f:
            
        #     f.write(response['SynthesisTask']['OutputUri'])
        #     f.close()
        print('-------------- Text converted to mp3. ----------------')

        # # Synchronous Method
        # # Synthesizes the speech (upper limit 15'000 characters)
        # response = polly.synthesize_speech(Text=sequence, VoiceId='Matthew', LanguageCode='en-US', Engine='neural', TextType='text', OutputFormat='mp3')

        # with open('speech.wav', 'wb') as f:
        #     f.write(response['AudioStream'].read())
        #     f.close()
    return

def split_body_into_sequences(text):
    """
    Max length 14000 characters, otherwise Amazon Polly will not work.
    Split strings always at .,!,? or \n
    """
    sequences = []
    sequence = []
    sentence = ''
    for i, char in enumerate(text):
        sentence += char
        if sum(len(s) for s in sequence) + len(sentence) > 14000:
            sequences.append([' '.join(sequence)])
            sequence = []
        else:
            if char in ['.', '!', '?', '\n']:
                sequence.append(sentence)
                sentence = ''
    sequence.append(sentence)
    sequences.append([' '.join(sequence)])
    return sequences

def mode_selection(aws_key_id, aws_secret_key, mode, filename, output_file, flags, language, speed):
    if filename == None:
        print('Please provide the name of the inputfile.')
        return
    if mode == 'txt': 
        path = filename[:-4] + '.' + 'pdf'
        extract_text(path, output_file, flags)
    elif mode == 'mp3':
        if aws_key_id is None or aws_secret_key is None:
            print('Please add a valid aws_key_id and aws_secret_key')
            return
        path = filename[:-4] + '.' + 'txt'
        print(path)
        convert_to_mp3(aws_key_id, aws_secret_key, path, output_file, language, speed)
    else:
        print('Please select a valid mode.')

def _setup_args():
    parser = argparse.ArgumentParser(description='Extract text from pdf and convert to mp3')
    parser.add_argument('-m', '--mode', type=str, help='Mode (generate text or mp3), one of [txt, mp3]')
    parser.add_argument('-n', '--file_name', type=str, help='path to file, e.g. "decolonising-peacebuilding_schirch.pdf"')
    parser.add_argument('-o', '--output_path', type=str, help='name of output file, e.g. "decolonising-peacebuilding_schirch.txt" or "decolonising-peacebuilding_schirch.mp3"')
    parser.add_argument('-f', '--flags', type=str, nargs='+', help='Additional flags to be removed from the text')
    parser.add_argument('-l', '--language', type=str, help='Language of the text (default: en)')
    parser.add_argument('-s', '--speed', type=float, help='Speed of the text (default: 1.0)')
    parser.add_argument('-i', '--aws_key_id', type=str, help='AWS key id')
    parser.add_argument('-k', '--aws_secret_key', type=str, help='AWS secret key')
    return parser.parse_args()

if __name__ == '__main__':
    # Add the following:
    aws_key_id = ''
    aws_secret_key = ''

    # Additional flags to be removed from the text. Can be iteratively maintained
    with open('assets/flags.txt', 'r') as f:
        flags = f.read().splitlines()
        flags = [flag for flag in flags if flag != '']

    args = _setup_args()

    # prompt for right usage
    if args.mode is None or args.file_name is None:
        # print the description of module
        print(__doc__)
        # break the execution
        print('Please provide the mode and the filename in the form of the above descirption.')
        sys.exit(1)
    args.file_name = args.file_name
    
    if args.mode == 'mp3' and (args.aws_key_id is None or args.aws_secret_key is None):
        print('Please provide a aws_key_id and aws_secret_key to convert to mp3.')
        args.aws_key_id = aws_key_id
        args.aws_secret_key = aws_secret_key
        #sys.exit(1)

    # define defaults for non-required arguments
    if args.output_path is None:
        args.output_path = args.file_name[:-4] + '.' + args.mode
        print(args.output_path)
    else:
        args.output_path = args.output_path[:-4] + '.' + args.mode
    if args.flags is None:
        args.flags = flags
    else:
        args.flags.append(flags)
    if args.language is None:
        args.language = 'en'
    if args.speed is None:
        args.speed = 1.0

    for key in args.__dict__:
        print(key, args.__dict__[key])
    
    mode_selection(args.aws_key_id, args.aws_secret_key, mode=args.mode, filename=args.file_name, output_file=args.output_path, flags=args.flags, language=args.language, speed=args.speed)
    #extract_text(path=args.path, output_file=args.output_path)