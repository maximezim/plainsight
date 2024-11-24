#!/usr/bin/env python -u
import argparse, logging, sys, textwrap
from time import time  # Removed 'clock' as it's deprecated in Python 3

from . import data, probability  # Changed to relative imports
from .model import *             # Changed to relative imports


###############################################################################
# main sequence go

def run():
    # Argument parser
    parser = argparse.ArgumentParser(description='Plainsight: a textual steganography tool to make your data look like prose.' + \
                                                 '\nHomepage and examples: http://github.com/rw/plainsight' + \
                                                 '\nAuthor: Robert Winslow (@robert_winslow)',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent('''\
                                             Example invocations:
                                             Encipher:
                                                echo "the meeting place is Union Square at 5pm" | plainsight --mode=encipher -f a-book.txt > ciphertext
                                             Decipher:
                                                cat ciphertext | plainsight --mode=decipher -f a-book.txt
                                             '''))
    parser.add_argument('-m', '--mode', metavar='MODE', type=str, nargs=1, required=True,
                        choices=['encipher', 'decipher'],
                       help='Operating mode. Valid options are: encipher, decipher.')
    parser.add_argument('-c', '--context', metavar='N', type=int, nargs='?', default=3, choices=range(11),
                       help='The number of tokens to use as context. ' + \
                            'Choose a number from 0 through 10. Default is 3. ' + \
                            'The time to build a model increases [superlinearly] with this, but so does similarity to the source texts.')
    parser.add_argument('-f', '--model-file', metavar='FILE', type=argparse.FileType('rb'), nargs='+',
                        required=True,
                       help='One or more files to use when creating the lingustic model. ' + \
                            'The data from the file will be used verbatim. ' + \
                            'Example input: a downloaded a Project Guttenberg book.')
    parser.add_argument('-u', '--model-url', metavar='URL', type=str, nargs='*',
                       help='(Not implemented.) One or more URLs to use when creating the lingustic model. ' + \
                            'The data at the URL will be stripped of markup. ' + \
                            'Example input: http://www.gutenberg.org/ebooks/1661.txt.utf8 (Sherlock Holmes).')

    # Parse the arguments
    args = parser.parse_args()
    MODEL_FILES = args.model_file
    MODE = args.mode[0]
    CONTEXT = max(0, args.context - 1)
    INPUT, OUTPUT, LOGGING = sys.stdin, sys.stdout, sys.stderr

    # generate model from input text
    model = Model(CONTEXT)

    # load files for language model:
    if MODEL_FILES is not None:
        sys.stderr.write('Adding models:\n')
        for f in MODEL_FILES:
            start = time()
            model_text = data.take_char_input(f)
            model.add_text(model_text, CONTEXT)
            sys.stderr.write('Model: %s added in %.02fs (context == %d)\n' \
                             % (f.name, time() - start, CONTEXT))

    sys.stderr.write('input is "%s", ' % INPUT.name)
    sys.stderr.write('output is "%s"\n' % OUTPUT.name)
    sys.stderr.write('\n')

    # Adjust INPUT and OUTPUT based on MODE
    if MODE == 'encipher':
        INPUT = sys.stdin.buffer  # Read binary data
        OUTPUT = sys.stdout       # Write text data
    elif MODE == 'decipher':
        INPUT = sys.stdin         # Read text data
        OUTPUT = sys.stdout.buffer  # Write binary data
    else:
        INPUT = sys.stdin
        OUTPUT = sys.stdout


    # encipher or decipher the input
    if MODE == 'encipher':
        cleartext = data.take_binary_input(INPUT)
        ciphertext = cipher(model, CONTEXT, cleartext, 'encipher')
        sys.stderr.write('\n')
        OUTPUT.write(ciphertext)

    elif MODE == 'decipher':
        ciphertext = data.to_words(data.take_char_input(INPUT))
        cleartext = cipher(model, CONTEXT, ciphertext, 'decipher')
        sys.stderr.write('\n')
        OUTPUT.write(cleartext.tobytes())


if __name__ == '__main__':
    run()
