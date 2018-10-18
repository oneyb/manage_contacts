#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# written by Brian J. Oney <brian.j.oney@gmail.com>
# inspired by Titus von der Malsburg <malsburg@posteo.de>

# This is a simple script for converting all vCard files to
# a single database and an org file.  The directory under which all vcf files
# reside needs to be supplied along the output file name(s) of the resulting
# vCard and org-mode file.

# Usage: python manage_contacts.py . contents.org


# import pandas as pd
import os
import sys
import io
import dateutil.parser
import vobject
from itertools import chain

# Org file structure
PREFIX = "*"
INDENTATION = len(PREFIX) * 2 * ' '
TEMPLATE = INDENTATION + ":%s: %s%s"


def get_vcf_files(d):
    '''Find all VCF-file in and below a certain directory.'''
    files = []
    for root, dirs, fnames in os.walk(d):
        for f in fnames:
            if f.lower().endswith(".vcf"):
                files.append(os.path.join(root, f))
    return files


def read_vcf_file(fname, removePhotos=True):
    '''Read the contents of a VCF-file.'''
    with open(fname, "r", encoding="utf-8") as f:
        vcf_list = f.readlines()
    # remove photos
    if removePhotos:
        vcf_list = remove_photos(vcf_list)
    return vcf_list


def remove_photos(flat_raw_list):
    '''Photos can be pretty wierd, prefer to remove them.'''
    photo_index_tuple_list = []
    photo = False
    for j, line in enumerate(flat_raw_list):
        if line.lower().startswith('photo'):
            photo = True
            start = j
            continue
        if ':' in line and photo:
            photo_index_tuple_list.append((start, j-1))
            photo = False

    if photo_index_tuple_list:
        # print('removing items')
        photo_index_tuple_list.reverse()
        for i, j in photo_index_tuple_list:
            for k in range(j, i-1, -1):
                # print(k)
                flat_raw_list.pop(k)

        # print( flat_raw_list )
    for j, line in enumerate(flat_raw_list):
        if line.lower().startswith('photo'):
            raise Exception('"remove_photos" failed')
    return flat_raw_list


def parse_vcf_file(vcf_list):
    '''
    Parse the contents of VCF-file entries
    '''
    string_buffer = io.StringIO(u''.join(vcf_list))
    try:
        vcards_raw = vobject.readComponents(
            string_buffer, validate=False, ignoreUnreadable=True)
        contacts = set(vcard.serialize(validate=False) for vcard in vcards_raw)
        stringio = io.StringIO(''.join(contacts))
        vcards = vobject.readComponents(stringio, ignoreUnreadable=True)

    except Exception as e:
        raise e
    return vcards


def vcard_to_org(vcard):
    '''
    convert vobject.vCard to list of string for writing to the output file
    '''
    org_list = []
    try:
        children = vcard.getChildren()
    except:
        return ''

    for n in ('fn', 'n', 'email'):
        fn_value = str(vcard.getChildValue(n)).strip()
        if n in ('fn', 'n'):
            fn_value = fn_value.replace(';', ' ').strip()
        if fn_value:
            break

    note = ""
    child_list = []
    for p in children:

        name = p.name
        value = p.value

        if name in ("VERSION", "PRODID") \
           or name.startswith("X-"):
            continue

        if name == "NOTE":
            note = p.value
            continue

        # Collect type attributes:
        attribs = ", ".join(p.params.get("TYPE", []))
        if attribs:
            attribs = " (%s)" % attribs

        # Special treatment for some fields:

        if name == "ORG":
            try:
                value = ", ".join(chain(*p.value))
            except:
                value = p.value

        if name == "N":
            value = "%s;%s;%s;%s;%s" % (p.value.family, p.value.given,
                                        p.value.additional, p.value.prefix,
                                        p.value.suffix)

        if name == "ADR":
            # TODO Make the formatting sensitive to X-ABADR:
            value = (p.value.street, p.value.code + " " + p.value.city,
                     p.value.region, p.value.country, p.value.extended,
                     p.value.box)
            value = ", ".join([x for x in value if x != ''])
            name = "ADDRESS"

        if name == "REV":
            value = value.split('(')[0]  # Evolution Mail Client Contacts crap
            value = dateutil.parser.parse(value)
            value = value.strftime("[%Y-%m-%d %a %H:%M]")

        if name == "TEL":
            name = "PHONE"

        # Make sure that there are no newline chars left as that would
        # break org's property format:
        value = value.replace("\n", ", ")

        child_list.append(TEMPLATE % (name, value, attribs))
        child_list.sort()

    org_list.append("%s %s" % (PREFIX, fn_value))
    org_list.append(INDENTATION + ":PROPERTIES:\n" + u'\n'.join(child_list))
    org_list.append(INDENTATION + ":END:\n")
    if note:
        org_list.append(INDENTATION + note + r'\n')

    return fn_value, u'\n'.join(org_list)


def main():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--format', default='org')
    parser.add_argument('directory', default='.')
    parser.add_argument('outputfile')
    parser.add_argument('-lf', '--list-formats', default=False,
                        dest='lf', action='store_true')
    args = parser.parse_args()

    out_formats = ['org', 'vcf']
    if args.format not in out_formats or args.lf:
        print('\nAccepted formats are:\n')
        sys.stdout.write('\t' + '\n\t'.join(out_formats) + '\n\n')
        sys.exit(1)

    if len(sys.argv) != 3:
        raise ValueError("Please specify exactly one "
                         "directory and an output file")

    d = args.directory
    outfile = args.outputfile

    files = get_vcf_files(d)

    raw_list = [read_vcf_file(f) for f in files]

    flat_raw_list = list(chain(*raw_list))

    vcards = parse_vcf_file(flat_raw_list)

    if args.format == 'org':
        contacts = {}
        for vcard in vcards:
            title, org = vcard_to_org(vcard)
            contacts[title] = org

        with open(outfile, 'w', encoding='utf-8') as f:
            for name in sorted(contacts.keys()):
                f.write(contacts[name])
            f.write('\n#+STARTUP: showeverything\n')

    if args.format == 'vcf':
        contacts = set(vcard.serialize(validate=False) for vcard in vcards)
        contacts.sort()
        # import pdb
        # pdb.set_trace()
        with open(outfile, 'w', encoding='utf-8') as f:
            for name in contacts:
                f.write(name)


def to_vcard(item):
    item = item.map(lambda s: s.strip())

    c = vobject.vCard()

    c.add('n')
    if item['Additional Name']:
        c.n.value = vobject.vcard.Name(
            family=item['Family Name'],
            given=item['Given Name'],
            additional=item['Additional Name'])
    else:
        c.n.value = vobject.vcard.Name(
            family=item['Family Name'], given=item['Given Name'])

    c.add('fn')
    c.fn.value = item['Name']

    simple_pairs = [('Nickname', 'nickname'), ('Birthday', 'bday'), ('Notes',
                                                                     'note')]

    for p1, p2 in simple_pairs:
        if item[p1]:
            c.add(p2)
            getattr(c, p2).value = item[p1]

    if item['Group Membership']:
        c.add('categories')
        c.categories.value = [
            g.lstrip('* ') for g in item['Group Membership'].split(' ::: ')
        ]

    for i in range(1, 4):
        if item['E-mail %d - Value' % i]:
            for elem in item['E-mail %d - Value' % i].split(' ::: '):
                c.add('email')
                c.contents['email'][-1].value = elem
                c.contents['email'][-1].type_param = item['E-mail %d - Type' %
                                                          i].lstrip('* ')

    for i in range(1, 6):
        if item['Phone %d - Value' % i]:
            for elem in item['Phone %d - Value' % i].split(' ::: '):
                c.add('tel')
                c.contents['tel'][-1].value = elem
                c.contents['tel'][-1].type_param = item['Phone %d - Type' %
                                                        i].lstrip('* ')

    # Doesn't work, no idea why

    # for i in range(1, 2):
    #     if item['Website %d - Value' % i]:
    #         c.add('item1.URL')
    #         print(c.contents)
    #         c.contents['item1.URL'][i - 1].value = item['Website %d - Value' % i]
    #         c.add('item1.X-ABLabel')
    #         c.contents['item1.X-ABLabel'][i - 1].type_param = item['Website %d - Type' % i]

    return c


def convert(src='google.csv', dst='contacts.vcf'):
    import pandas as pd
    df = pd.read_csv(src, encoding='utf-8')
    df.fillna(u'', inplace=True)

    with open(dst, 'w') as f:
        for i, item in df.iterrows():
            f.write(to_vcard(item).serialize())


if __name__ == '__main__':
    main()
