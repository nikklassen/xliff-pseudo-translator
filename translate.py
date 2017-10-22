import xml.etree.ElementTree as ET
import random as r
from argparse import ArgumentParser
import sys

REPLACEMENTS = {
    'a': 'дàáâäå', 'b': 'ß', 'c': 'ç', 'd': 'ð', 'e': 'êéëè', 'f': 'ƒ', 'g': 'ĝ', 'h': 'ĥ',
    'i': 'ïíîì', 'j': 'ĵ', 'k': 'ꝁ𐤊', 'l': 'ł', 'm': 'ɱ', 'n': 'ñ', 'o': 'ôöòõóø', 'p': 'Þþ',
    'q': 'ꝙʠɋq̃', 'r': 'я', 's': 'š', 't': 'ŧť', 'u': 'úüûù', 'v': 'ᶌʋ', 'w': 'ʍⱳ', 'x': 'ẍẋᶍ',
    'y': 'ÿý', 'z': 'ž', 'A': 'ДÀÁÂÃ', 'B': 'ß', 'C': 'Ç', 'D': 'Ð', 'E': 'ÊËÉÈ', 'F': 'ƒ',
    'G': 'Ĝ', 'H': 'Ĥ', 'I': 'ÍÌÎÏ', 'J': 'Ĵ', 'K': 'Ꝁ₭', 'L': 'Ł', 'M': 'Ɱ', 'N': 'Ñ',
    'O': 'ÓÔÕØÖÒ', 'P': 'Þþ', 'Q': 'ɊꝖ', 'R': 'Я', 'S': 'Š', 'T': 'ŦŤ', 'U': 'ÙÚÜÛ', 'V': 'ṼṾ',
    'W': '₩', 'X': 'ẌẊ', 'Y': 'ŸÝ', 'Z': 'Ž'
}

def translate(text, pad, nesting):
    if not text:
        return text, nesting
    # Counter for the number of translatable characters in the text
    entity = False
    n = 0
    tmp = ''
    for (i, c) in enumerate(text):
        if c == ';':
            entity = False
        elif c == '&':
            entity = True
        elif c == '{':
            nesting += 1
        elif c == '}':
            nesting -= 1

        if nesting % 2 == 1:
            tmp += c
            continue

        if not entity and c in REPLACEMENTS:
            # Only count when nesting is 0 because multiple alternatives will
            # artificially increase the apparent length of the text
            if nesting == 0:
                n += 1
            # Replace approximately half of all characters also always
            # translate the first character, to ensure that in a short word at
            # least one thing gets translated. If nesting is even then we're
            # not in an ICU expression
            if r.randint(0, 1) == 0 or n == 0:
                tmp += r.choice(REPLACEMENTS[c])
            else:
                tmp += c
        else:
            # Not translatable, but counts toward the length of the text
            if nesting == 0 and c == ' ':
                n += 1
            tmp += c
    if pad:
        padding = '_' * int(n * 0.30 / 2)
    else:
        padding = ''
    return padding + tmp + padding, nesting

def main():
    parser = ArgumentParser()
    parser.add_argument('file', default='', help='The xliff source file')
    parser.add_argument(
        '-u', '--update', help='Update the pseudo-translations instead of recreating all of them',
        action='store_true')
    parser.add_argument('-o', '--output', help='The output translation file')
    parser.add_argument('-p', '--pad', action='store_true',
                        help='Pad out translation strings to emulate languages like German')
    args = parser.parse_args()

    output_file = args.output
    if not output_file:
        output_file = args.file.replace('.xlf', '.pseudo.xlf')

    ns = {'xlf': 'urn:oasis:names:tc:xliff:document:1.2'}
    ET.register_namespace('', ns['xlf'])

    if args.update:
        input_file = output_file
    elif args.file:
        input_file = args.file
    else:
        sys.stderr.write('An input file must be specified if update is false\n')
        sys.exit(1)

    tree = ET.parse(input_file)
    root = tree.getroot()
    trans_units = root.findall('.//xlf:trans-unit', ns)
    for trans_unit in trans_units:
        target = trans_unit.find('xlf:target', ns)
        if args.update and target is not None and (target.text or target):
            continue
        if target is not None:
            trans_unit.remove(target)

        source = trans_unit.find('xlf:source', ns)
        target = ET.SubElement(trans_unit, 'target')
        nesting = 0
        target.text, nesting = translate(source.text, args.pad, nesting)
        children = source.iter()
        # Skip the root
        next(children)
        for node in children:
            new_node = ET.SubElement(target, node.tag, node.attrib)
            new_node.tail, nesting = translate(node.tail, args.pad, nesting)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    main()
