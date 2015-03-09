from booleanOperations import BooleanOperationManager


def removeGlyphOverlap(glyph):
    """Remove overlaps in contours from a glyph."""
    #TODO(jamesgk) verify overlaps exist first, as per library's recommendation
    manager = BooleanOperationManager()
    contours = glyph.contours
    glyph.clearContours()
    manager.union(contours, glyph.getPointPen())
