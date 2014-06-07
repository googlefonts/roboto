from vanillaBase import VanillaBaseObject, VanillaBaseControl, VanillaError
from vanillaBox import Box, HorizontalLine, VerticalLine
from vanillaBrowser import ObjectBrowser
from vanillaButton import Button, SquareButton, ImageButton, HelpButton
from vanillaCheckBox import CheckBox
from vanillaColorWell import ColorWell
from vanillaComboBox import ComboBox
from vanillaDrawer import Drawer
from vanillaEditText import EditText, SecureEditText
from vanillaGroup import Group
from vanillaImageView import ImageView
from vanillaList import List, CheckBoxListCell, SliderListCell, PopUpButtonListCell
from vanillaPopUpButton import PopUpButton
from vanillaProgressBar import ProgressBar
from vanillaProgressSpinner import ProgressSpinner
from vanillaRadioGroup import RadioGroup
from vanillaScrollView import ScrollView
from vanillaSearchBox import SearchBox
from vanillaSegmentedButton import SegmentedButton
from vanillaSlider import Slider
from vanillaTabs import Tabs
from vanillaTextBox import TextBox
from vanillaTextEditor import TextEditor
from vanillaWindows import Window, FloatingWindow, Sheet

__all__ = [
    "VanillaBaseObject", "VanillaBaseControl", "VanillaError",
    "Box", "HorizontalLine", "VerticalLine",
    "Button", "SquareButton", "ImageButton", "HelpButton",
    "CheckBox",
    "ColorWell",
    "ComboBox",
    "Drawer",
    "EditText",
    "Group",
    "ImageView",
    "List", "CheckBoxListCell", "SliderListCell", "PopUpButtonListCell",
    "ObjectBrowser",
    "PopUpButton",
    "ProgressBar",
    "ProgressSpinner",
    "RadioGroup",
    "ScrollView",
    "SearchBox",
    "SecureEditText",
    "SegmentedButton",
    "Slider",
    "SplitView",
    "Tabs",
    "TextBox",
    "TextEditor",
    "Window", "FloatingWindow", "Sheet"
    ]

# OS 10.4+ objects
try:
    from vanillaLevelIndicator import LevelIndicator, LevelIndicatorListCell
    __all__.append("LevelIndicator")
    __all__.append("LevelIndicatorListCell")
    from vanillaDatePicker import DatePicker
    __all__.append("DatePicker")
except (ImportError, NameError):
    pass

# OS 10.5 objects
try:
    from vanillaGradientButton import GradientButton
    __all__.append("GradientButton")
    from vanillaPathControl import PathControl
    __all__.append("PathControl")
except (ImportError, NameError):
    pass

# RBSplitView required for SplitView
class _NoRBSplitView(object):

    def __init__(self, *args, **kwargs):
        raise VanillaError("SplitView is not available because the RBSplitView framework cannot be found. Refer to the Vanilla documentation for details.")

try:
    from vanillaSplitView import SplitView
    from vanilla.externalFrameworks import RBSplitView
except (ImportError, ValueError):
    SplitView = _NoRBSplitView

