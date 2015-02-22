def decomposeGlyph(glyph):
    """Moves the components of a glyph to its outline."""

    font = glyph.getParent()
    for component in glyph.components:
        componentGlyph = font[component.baseGlyph]
        for contour in componentGlyph:
            contour = contour.copy()
            contour.scale(component.scale)
            contour.move(component.offset)
            glyph.appendContour(contour)
    glyph.clear(contours=False, anchors=False, guides=False)
