def decomposeGlyph(font, glyphName):
    """Moves the components of a glyph to its outline."""

    glyph = font[glyphName]
    deepCopyContours(font, glyph, glyph, (0, 0), (1, 1))
    glyph.clearComponents()


def deepCopyContours(font, parent, component, offset, scale):
    """Copy contours to parent from component, including nested components."""

    for nested in component.components:
        deepCopyContours(
            font, parent, font[nested.baseGlyph],
            (offset[0] + nested.offset[0], offset[1] + nested.offset[1]),
            (scale[0] * nested.scale[0], scale[1] * nested.scale[1]))

    if component == parent:
        return
    for contour in component:
        contour = contour.copy()
        contour.scale(scale)
        contour.move(offset)
        parent.appendContour(contour)
