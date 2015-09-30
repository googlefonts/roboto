# coding=UTF-8
#
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Common tests for different targets."""

import glob
from os import path
import unittest

from fontTools import ttLib
from nototools import coverage
from nototools import font_data
from nototools import noto_fonts

import freetype

import layout
import roboto_data
from glyph_area_pen import GlyphAreaPen


def get_rendered_char_height(font_filename, font_size, char, target='mono'):
    if target == 'mono':
        render_params = freetype.FT_LOAD_TARGET_MONO
    elif target == 'lcd':
        render_params = freetype.FT_LOAD_TARGET_LCD
    render_params |= freetype.FT_LOAD_RENDER

    face = freetype.Face(font_filename)
    face.set_char_size(font_size*64)
    face.load_char(char, render_params)
    return face.glyph.bitmap.rows


def load_fonts(patterns, expected_count=None, font_class=None):
    """Load all fonts specified in the patterns.

    Also assert that the number of the fonts found is exactly the same as
    expected_count."""

    if font_class is None:
        font_class = ttLib.TTFont

    all_font_files = []
    for pattern in patterns:
        all_font_files += glob.glob(pattern)
    all_fonts = [font_class(font) for font in all_font_files]
    if expected_count:
        assert len(all_font_files) == expected_count
    return all_font_files, all_fonts


class FontTest(unittest.TestCase):
    """Parent class for all font tests."""
    loaded_fonts = None


class TestItalicAngle(FontTest):
    """Test the italic angle of fonts."""

    def setUp(self):
        _, self.fonts = self.loaded_fonts

    def test_italic_angle(self):
        """Tests the italic angle of fonts to be correct."""
        for font in self.fonts:
            post_table = font['post']
            if 'Italic' in font_data.font_name(font):
                expected_angle = -12.0
            else:
                expected_angle = 0.0
            self.assertEqual(post_table.italicAngle, expected_angle)


class TestMetaInfo(FontTest):
    """Test various meta information."""

    mark_heavier_as_bold = False

    def setUp(self):
        _, self.fonts = self.loaded_fonts

    def test_mac_style(self):
        """Tests the macStyle of the fonts to be correct.

        Bug: https://code.google.com/a/google.com/p/roboto/issues/detail?id=8
        """
        for font in self.fonts:
            font_name = font_data.font_name(font)
            bold = ('Bold' in font_name) or (
                self.mark_heavier_as_bold and 'Black' in font_name)
            italic = 'Italic' in font_name
            expected_mac_style = (italic << 1) | bold
            self.assertEqual(font['head'].macStyle, expected_mac_style)

    def test_fs_type(self):
        """Tests the fsType of the fonts to be 0.

        fsType of 0 marks the font free for installation, embedding, etc.

        Bug: https://code.google.com/a/google.com/p/roboto/issues/detail?id=29
        """
        for font in self.fonts:
            self.assertEqual(font['OS/2'].fsType, 0)

    def test_vendor_id(self):
        """Tests the vendor ID of the fonts to be 'GOOG'."""
        for font in self.fonts:
            self.assertEqual(font['OS/2'].achVendID, 'GOOG')

    def test_us_weight(self):
        "Tests the usWeight of the fonts to be correct."""
        for font in self.fonts:
            weight = noto_fonts.parse_weight(font_data.font_name(font))
            expected_numeric_weight = noto_fonts.WEIGHTS[weight]
            self.assertEqual(
                font['OS/2'].usWeightClass,
                expected_numeric_weight)

    def test_version_numbers(self):
        "Tests the two version numbers of the font to be correct."""
        for font in self.fonts:
            build_number = roboto_data.get_build_number()
            expected_version = '2.' + build_number
            version = font_data.font_version(font)
            usable_part_of_version = version.split(';')[0]
            self.assertEqual(usable_part_of_version,
                             'Version ' + expected_version)

            revision = font_data.printable_font_revision(font, accuracy=5)
            self.assertEqual(revision, expected_version)


class TestNames(FontTest):
    """Tests various strings in the name table."""

    mark_heavier_as_bold = False

    def setUp(self):
        font_files, self.fonts = self.loaded_fonts
        self.font_files = [path.basename(f) for f in font_files]
        self.condensed_family_name = self.family_name + ' Condensed'
        self.names = []
        for font in self.fonts:
            self.names.append(font_data.get_name_records(font))

    def test_copyright(self):
        """Tests the copyright message."""
        for records in self.names:
            self.assertEqual(
                records[0],
                'Copyright 2011 Google Inc. All Rights Reserved.')

    def parse_filename(self, filename):
        """Parse expected name attributes from filename."""

        name_nosp = self.family_name.replace(' ', '')
        condensed_name_nosp = self.condensed_family_name.replace(' ', '')
        family_names = '%s|%s' % (condensed_name_nosp, name_nosp)

        filename_match = noto_fonts.match_filename(filename, family_names)
        family, _, _, _, _, weight, slope, _ = filename_match.groups()

        if family == condensed_name_nosp:
            family = self.condensed_family_name
        else:  # family == name_nosp
            family = self.family_name
        if not weight:
            weight = 'Regular'
        return family, weight, slope

    def build_style(self, weight, slope):
        """Build style (typographic subfamily) out of weight and slope."""

        style = weight
        if slope:
            if style == 'Regular':
                style = 'Italic'
            else:
                style += ' ' + slope
        return style

    def test_family_name(self):
        """Tests the family name.
        Bug: https://github.com/google/roboto/issues/37
        """

        for font_file, records in zip(self.font_files, self.names):

            family, weight, _ = self.parse_filename(font_file)

            # check that family name includes weight, if not regular or bold
            if weight not in ['Regular', 'Bold']:
                self.assertEqual(records[1], '%s %s' % (family, weight))

                # check typographic name, if present
                self.assertIn(16, records)
                self.assertEqual(records[16], family)

            # check that family name does not include weight, if regular or bold
            else:
                self.assertEqual(records[1], family)

    def test_subfamily_name(self):
        """Tests the subfamily name.
        Bug: https://github.com/google/roboto/issues/37
        """

        for font_file, records in zip(self.font_files, self.names):
            _, weight, slope = self.parse_filename(font_file)
            subfam = records[2]

            # check that subfamily is just a combination of bold and italic
            self.assertIn(subfam, ['Regular', 'Bold', 'Italic', 'Bold Italic'])

            # check that subfamily weight/slope are consistent with filename
            bold = (weight == 'Bold') or (
                self.mark_heavier_as_bold and
                noto_fonts.WEIGHTS[weight] > noto_fonts.WEIGHTS['Bold'])
            self.assertEqual(bold, subfam.startswith('Bold'))
            self.assertEqual(slope == 'Italic', subfam.endswith('Italic'))

            # check typographic name, if present
            if weight not in ['Regular', 'Bold']:
                self.assertIn(17, records)
                self.assertEqual(records[17], self.build_style(weight, slope))

    def test_unique_identifier_and_full_name(self):
        """Tests the unique identifier and full name."""
        for font_file, records in zip(self.font_files, self.names):
            family, weight, slope = self.parse_filename(font_file)
            style = self.build_style(weight, slope)
            expected_name = family + ' ' + style
            self.assertEqual(records[3], expected_name)
            self.assertEqual(records[4], expected_name)
            self.assertFalse(records.has_key(18))

    def test_postscript_name(self):
        """Tests the postscript name."""
        for font_file, records in zip(self.font_files, self.names):
            family, weight, slope = self.parse_filename(font_file)
            style = self.build_style(weight, slope)
            expected_name = (family + '-' + style).replace(' ', '')
            self.assertEqual(records[6], expected_name)

    def test_postscript_name_for_spaces(self):
        """Tests that there are no spaces in PostScript names."""
        for records in self.names:
            self.assertFalse(' ' in records[6])


class TestDigitWidths(FontTest):
    """Tests the width of digits."""

    def setUp(self):
        self.font_files, self.fonts = self.loaded_fonts
        self.digits = [
            'zero', 'one', 'two', 'three', 'four',
            'five', 'six', 'seven', 'eight', 'nine']

    def test_digit_widths(self):
        """Tests all decimal digits to make sure they have the same width."""
        for font in self.fonts:
            hmtx_table = font['hmtx']
            widths = [hmtx_table[digit][0] for digit in self.digits]
            self.assertEqual(len(set(widths)), 1)

    def test_superscript_digits(self):
        """Tests that 'numr' features maps digits to Unicode superscripts."""
        ascii_digits = '0123456789'
        superscript_digits = u'⁰¹²³⁴⁵⁶⁷⁸⁹'
        for font_file in self.font_files:
            numr_glyphs = layout.get_advances(
                ascii_digits, font_file, '--features=numr')
            superscript_glyphs = layout.get_advances(
                superscript_digits, font_file)
            self.assertEqual(superscript_glyphs, numr_glyphs)


class TestCharacterCoverage(FontTest):
    """Tests character coverage."""

    def setUp(self):
        _, self.fonts = self.loaded_fonts
        self.LEGACY_PUA = frozenset({0xEE01, 0xEE02, 0xF6C3})

    def test_inclusion_of_legacy_pua(self):
        """Tests that legacy PUA characters remain in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            for char in self.LEGACY_PUA:
                self.assertIn(char, charset)

    def test_non_inclusion_of_other_pua(self):
        """Tests that there are not other PUA characters except legacy ones."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            pua_chars = {
                char for char in charset
                if 0xE000 <= char <= 0xF8FF or 0xF0000 <= char <= 0x10FFFF}
            self.assertTrue(pua_chars <= self.LEGACY_PUA)

    def test_lack_of_unassigned_chars(self):
        """Tests that unassigned characters are not in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertNotIn(0x2072, charset)
            self.assertNotIn(0x2073, charset)
            self.assertNotIn(0x208F, charset)

    def test_inclusion_of_sound_recording_copyright(self):
        """Tests that sound recording copyright symbol is in the fonts."""
        for font in self.fonts:
            charset = coverage.character_set(font)
            self.assertIn(
                0x2117, charset,  # SOUND RECORDING COPYRIGHT
                'U+2117 not found in %s.' % font_data.font_name(font))


class TestLigatures(FontTest):
    """Tests formation or lack of formation of ligatures."""

    def setUp(self):
        self.fontfiles, _ = self.loaded_fonts

    def test_lack_of_ff_ligature(self):
        """Tests that the ff ligature is not formed by default."""
        for fontfile in self.fontfiles:
            advances = layout.get_advances('ff', fontfile)
            self.assertEqual(len(advances), 2)

    def test_st_ligatures(self):
        """Tests that st ligatures are formed by dlig."""
        for fontfile in self.fontfiles:
            for combination in [u'st', u'ſt']:
                normal = layout.get_glyphs(combination, fontfile)
                ligated = layout.get_glyphs(
                    combination, fontfile, '--features=dlig')
                self.assertTrue(len(normal) == 2 and len(ligated) == 1)


class TestFeatures(FontTest):
    """Tests typographic features."""

    def setUp(self):
        self.fontfiles, _ = self.loaded_fonts

    def test_smcp_coverage(self):
        """Tests that smcp is supported for our required set."""
        with open('res/smcp_requirements.txt') as smcp_reqs_file:
            smcp_reqs_list = []
            for line in smcp_reqs_file.readlines():
                line = line[:line.index(' #')]
                smcp_reqs_list.append(unichr(int(line, 16)))

        for fontfile in self.fontfiles:
            chars_with_no_smcp = []
            for char in smcp_reqs_list:
                normal = layout.get_glyphs(char, fontfile)
                smcp = layout.get_glyphs(char, fontfile, '--features=smcp')
                if normal == smcp:
                    chars_with_no_smcp.append(char)
            self.assertEqual(
                chars_with_no_smcp, [],
                ("smcp feature is not applied to '%s'" %
                    u''.join(chars_with_no_smcp).encode('UTF-8')))


EXPECTED_YMIN = -555
EXPECTED_YMAX = 2163

class TestVerticalMetrics(FontTest):
    """Test the vertical metrics of fonts."""

    def setUp(self):
        self.font_files, self.fonts = self.loaded_fonts

    def test_ymin_ymax(self):
        """Tests yMin and yMax to be equal to Roboto v1 values.

        Android requires this, and web fonts expect this.
        """
        for font in self.fonts:
            head_table = font['head']
            self.assertEqual(head_table.yMin, EXPECTED_YMIN)
            self.assertEqual(head_table.yMax, EXPECTED_YMAX)

    def test_glyphs_ymin_ymax(self):
        """Tests yMin and yMax of all glyphs to not go outside the range."""
        for font_file, font in zip(self.font_files, self.fonts):
            glyf_table = font['glyf']
            for glyph_name in glyf_table.glyphOrder:
                try:
                    y_min = glyf_table[glyph_name].yMin
                    y_max = glyf_table[glyph_name].yMax
                except AttributeError:
                    continue

                self.assertTrue(
                    EXPECTED_YMIN <= y_min and y_max <= EXPECTED_YMAX,
                    ('The vertical metrics for glyph %s in %s exceed the '
                     'acceptable range: yMin=%d, yMax=%d' % (
                         glyph_name, font_file, y_min, y_max)))

    def test_hhea_table_metrics(self):
        """Tests ascent, descent, and lineGap to be equal to Roboto v1 values.
        """
        for font in self.fonts:
            hhea_table = font['hhea']
            self.assertEqual(hhea_table.descent, -500)
            self.assertEqual(hhea_table.ascent, 1900)
            self.assertEqual(hhea_table.lineGap, 0)


class TestGlyphAreas(unittest.TestCase):
    """Tests that glyph areas between weights have the right ratios."""

    def setUp(self):
        """Determine which glyphs are intentionally unchanged."""

        self.unchanged = set()
        pen = self.pen = GlyphAreaPen()
        thin, bold = self.getFonts(self.masters[1], "Roboto", "Thin", "Bold")
        for glyph in thin:
            glyph.draw(pen)
            thin_area = pen.unload()
            bold[glyph.name].draw(pen)
            bold_area = pen.unload()
            if thin_area == bold_area:
                if thin_area:
                    self.unchanged.add(glyph.name)
            else:
                assert thin_area and bold_area

    def getFonts(self, fonts, family, *weights):
        """Extract fonts of certain family and weights from given font list."""

        fonts = dict((f.info.styleName, f) for f in fonts
                     if f.info.familyName == family)
        return [fonts[w] for w in weights]

    def test_output(self):
        """Test that only empty or intentionally unchanged glyphs are unchanged.
        """

        pen = self.pen
        thin, regular, bold = self.getFonts(
            self.loaded_fonts[1], "Roboto", "Thin", "Regular", "Bold")
        regular_areas = {}
        for glyph in regular:
            glyph.draw(pen)
            regular_areas[glyph.name] = pen.unload()

        for other in [thin, bold]:
            for name, regular_area in regular_areas.iteritems():
                other[name].draw(pen)
                other_area = pen.unload()
                if not regular_area:  # glyph probably contains only components
                    self.assertFalse(other_area)
                    continue
                unchanged = regular_area == other_area
                if unchanged:
                    msg = name + " has not changed, but should have."
                else:
                    msg = name + " has changed, but should not have."
                self.assertEqual(unchanged, name in self.unchanged, msg)
