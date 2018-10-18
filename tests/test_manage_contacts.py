#!/usr/bin/env python3


import vobject
import unittest
import os

from manage_contacts import manage_contacts


class TestObservedVcardToOrg(unittest.TestCase):
    '''
    There be some wild VCards out there...
    '''
    def test_observed_vcard_to_org(self):
        vcf_list = manage_contacts.read_vcf_file(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'tests.vcf'))
        vcard = next(manage_contacts.parse_vcf_file(vcf_list))
        org = manage_contacts.vcard_to_org(vcard)
        print(org)
        self.assertIsInstance(org[1], str)


class TestRemovePhotoAndParse(unittest.TestCase):
    def test_remove_photo(self):
        vcf_list = manage_contacts.read_vcf_file(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'photo-test.vcf'))
        vcard = next(manage_contacts.parse_vcf_file(vcf_list))
        self.assertIsInstance(vcard, vobject.base.Component)


class TestParseVcfFile(unittest.TestCase):
    def test_parse_vcf_file(self):
        vcf_list = [
            'BEGIN:VCARD\nVERSION:2.1\nN:Oney;Brian;;;\nFN:Brian Oney\nTEL;CELL;PREF:+123456789\nTEL;CELL:+123456789\nEMAIL;HOME:brian.j.oney@gmail.com\nEND:VCARD'
        ]
        vcard = next(manage_contacts.parse_vcf_file(vcf_list))
        self.assertIsInstance(vcard, vobject.base.Component)


class TestVcardToOrg(unittest.TestCase):
    def test_vcard_to_org(self):
        vcf_list = [
            'BEGIN:VCARD\nVERSION:2.1\nN:Oney;Brian;;;\nFN:Brian Oney\nTEL;CELL;PREF:+123456789\nTEL;CELL:+123456789\nEMAIL;HOME:brian.j.oney@gmail.com\nEND:VCARD'
        ]
        vcard = next(manage_contacts.parse_vcf_file(vcf_list))
        title, org = manage_contacts.vcard_to_org(vcard)
        # print(org)
        res = \
              '* Brian Oney\n  :PROPERTIES:\n  :EMAIL: brian.j.oney@gmail.com\n  :FN: Brian Oney\n  :N: Oney;Brian;;;\n  :PHONE: +123456789\n  :PHONE: +123456789\n  :END:'

        self.assertEqual(org.strip(), res)




# class TestVcardToOrg(unittest.TestCase):
#     def test_vcard_to_org(self):
#         vcf_list = [
#             'BEGIN:VCARD\nVERSION:2.1\nN:Oney;Brian;;;\nFN:Brian Oney\nTEL;CELL;PREF:+123456789\nTEL;CELL:+123456789\nEMAIL;HOME:brian.j.oney@gmail.com\nEND:VCARD'
#         ]
#         vcard = next(manage_contacts.parse_vcf_file(vcf_list))
#         res = \
#               '* Brian Oney\n  :PROPERTIES:\n  :EMAIL: brian.j.oney@gmail.com\n  :N: Oney;Brian;;;\n  :PHONE: +123456789\n  :PHONE: +123456789\n  :END:'
#         self.assertEqual(vcard, res)
