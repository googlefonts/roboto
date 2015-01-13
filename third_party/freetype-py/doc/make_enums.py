import freetype

enums = [
    'ft_fstypes',
    'ft_face_flags',
    'ft_encodings',
    'ft_glyph_bbox_modes',
    'ft_glyph_formats',
    'ft_kerning_modes',
    'ft_lcd_filters',
    'ft_load_flags',
    'ft_load_targets',
    'ft_open_modes',
    'ft_outline_flags',
    'ft_pixel_modes',
    'ft_render_modes',
    'ft_stroker_borders',
    'ft_stroker_linecaps',
    'ft_stroker_linejoins',
    'ft_style_flags',
    'tt_adobe_ids',
    'tt_apple_ids',
    'tt_mac_ids',
    'tt_ms_ids',
    'tt_ms_langids',
    'tt_mac_langids',
    'tt_name_ids',
    'tt_platforms'
]

for name in enums:
    print name
    module = getattr(freetype, name)
    doc = getattr(module, '__doc__')
    doc = doc.split('\n')
    file = open( name+'.rst', 'w')

    title = name.upper()
    file.write(title+'\n')
    file.write('='*len(title)+'\n')

    for line in doc:
        if line.startswith('FT_') or line.startswith('TT_'):
            file.write( '.. data:: '+ line + '\n')
        else:
            file.write( line + '\n')
    file.close()

