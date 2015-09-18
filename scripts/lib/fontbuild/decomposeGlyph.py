def decomposeGlyph(font, glyphName):
    """Moves the components of a glyph to its outline."""

    glyph = font[glyphName]
    for component in glyph.components:
        decompose(font, glyphName, component.baseGlyph,
                  component.offset, component.scale)
    glyph.clear(contours=False, anchors=False, guides=False)


def decompose(font, parentName, componentName, offset, scale):
    """Copy contours to parent from component, including nested components."""

    parent = font[parentName]
    component = font[componentName]

    for nested in component.components:
        decompose(font, parentName, nested.baseGlyph,
                  (offset[0] + nested.offset[0], offset[1] + nested.offset[1]),
                  (scale[0] * nested.scale[0], scale[1] * nested.scale[1]))

    for contour in component:
        contour = contour.copy()
        contour.scale(scale)
        contour.move(offset)
        parent.appendContour(contour)
