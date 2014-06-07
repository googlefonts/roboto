"""
Testing suite for dialogKit.

This should be called with

    from dialogKit.test import testAll
    testAll()

This will present a series of windows
that each have a "Run Tests" button
at the top. That button must be pressed
for the tests to be performed.
"""

from dialogKit import *

class TestCase(object):
    
    def __init__(self, posSize, title=''):
        print 'testing:', self._name
        print
        #
        self._errorCount = 0
        self._testCount = 0
        #
        self.w = ModalDialog(posSize, title=self._name, okCallback=self._userStopped, cancelCallback=self._userStopped)
        if len(posSize) == 2:
            w, h = posSize
        else:
            x, y, w, h = posSize
        self.w.runTestsButton = Button((10, 10, w-20, 20), 'Run Tests', callback=self.runTests)
    
    def assertEqual(self, value1, value2, assertionID=None):
        self._testCount += 1
        if value1 != value2:
            print 'ERROR:', self._name, assertionID
            print value1, '!=', value2
            print
            self._errorCount += 1
    
    def finish(self):
        print '-' * 70
        if not self._errorCount:
            print 'OK: Ran %d tests' % self._testCount
        else:
            print 'FAILURE: Ran %d tests. Found %d errors' % (self._testCount, self._errorCount)
        print
        print
        self.w.close()
    
    def _userStopped(self, sender):
        print 'FAILURE: user stopped test'
        print
        print


class ButtonTest(TestCase):
    
    _name = 'ButtonTest'
    
    def __init__(self):
        super(ButtonTest, self).__init__(posSize=(200, 120))
        self.w.button = Button((10, 40, 180, 20), 'foo')
        self.w.open()
    
    def runTests(self, sender):
        self.assertEqual(self.w.button.get(), 'foo', 'get')
        #
        self.finish()


class TextBoxTest(TestCase):
    
    _name = "TextBoxTest"
    
    def __init__(self):
        super(TextBoxTest, self).__init__(posSize=(200, 120))
        self.w.textBox = TextBox((10, 40, 180, 20), 'foo')
        self.w.open()
    
    def runTests(self, sender):
        self.assertEqual(self.w.textBox.get(), 'foo', 'get')
        #
        self.w.textBox.set('bar')
        self.assertEqual(self.w.textBox.get(), 'bar', 'set')
        #
        self.finish()


class PopUpButtonTest(TestCase):
    
    _name = "PopUpButtonTest"

    def __init__(self):
        super(PopUpButtonTest, self).__init__(posSize=(200, 127))
        self.w.popUpButton = PopUpButton((10, 40, 180, 27), ['foo', 'bar'])
        self.w.open()
    
    def runTests(self, sender):
        self.w.popUpButton.setSelection(0)
        self.assertEqual(self.w.popUpButton.getSelection(), 0, 'getSelection')
        #
        self.w.popUpButton.setSelection(1)
        self.assertEqual(self.w.popUpButton.getSelection(), 1, 'setSelection')
        #
        self.w.popUpButton.setSelection(None)
        self.assertEqual(self.w.popUpButton.getSelection(), None, 'setSelection None')
        #
        self.assertEqual(self.w.popUpButton.get(), ['foo', 'bar'], 'get')
        #
        self.w.popUpButton.set(['a', 'b', 'c'])
        self.assertEqual(self.w.popUpButton.get(), ['a', 'b', 'c'], 'set')
        #
        self.finish()


class CheckBoxTest(TestCase):

    _name = "CheckBoxTest"

    def __init__(self):
        super(CheckBoxTest, self).__init__(posSize=(200, 120))
        self.w.checkBox = CheckBox((10, 40, 180, 20), 'foo', value=1)
        self.w.open()

    def runTests(self, sender):
        self.assertEqual(self.w.checkBox.get(), True, 'get')
        #
        self.w.checkBox.set(False)
        self.assertEqual(self.w.checkBox.get(), False, 'get False')
        #
        self.w.checkBox.set(True)
        self.assertEqual(self.w.checkBox.get(), True, 'get True')
        #
        self.finish()


class EditTextTest(TestCase):

    _name = "EditTextTest"

    def __init__(self):
        super(EditTextTest, self).__init__(posSize=(200, 127))
        self.w.editText = EditText((10, 40, 180, 27), 'foo')
        self.w.open()

    def runTests(self, sender):
        self.assertEqual(self.w.editText.get(), 'foo', 'get')
        #
        self.w.editText.set('bar')
        self.assertEqual(self.w.editText.get(), 'bar', 'set')
        #
        self.finish()


class ListTest(TestCase):

    _name = "ListTest"

    def __init__(self):
        super(ListTest, self).__init__(posSize=(200, 200))
        self.w.list = List((10, 40, 180, 100), ['a', 'b', 'c'])
        self.w.open()

    def runTests(self, sender):
        self.assertEqual(self.w.list.get(), ['a', 'b', 'c'], 'get')
        #
        self.assertEqual(len(self.w.list), 3)
        self.assertEqual(self.w.list[0], 'a', '__getitem__')
        #
        self.w.list.set(['a', 'b', 'c'])
        self.w.list[1] = 'z'
        self.assertEqual(self.w.list.get(), ['a', 'z', 'c'], '__setitem__')
        #
        self.w.list.set(['a', 'b', 'c', 'z'])
        del self.w.list[1]
        self.assertEqual(self.w.list.get(), ['a', 'c', 'z'], '__delitem__')
        #
        self.w.list.set(['a', 'b', 'c'])
        self.assertEqual(self.w.list[:2], ['a', 'b'], '__getslice__')
        self.assertEqual(self.w.list[1:], ['b', 'c'], '__getslice__')
        #
        self.w.list.set(['a', 'b', 'c'])
        del self.w.list[1:]
        self.assertEqual(self.w.list.get(), ['a'], '__delslice__')
        #
        self.w.list.set(['a', 'b', 'c'])
        self.w.list[1:2] = ['x', 'y']
        self.assertEqual(self.w.list.get(), ['a', 'x', 'y', 'c'], '__setslice__')
        #
        self.w.list.set(['a', 'b', 'c'])
        self.w.list.append('z')
        self.assertEqual(self.w.list.get(), ['a', 'b', 'c', 'z'], 'append')
        #
        self.w.list.set(['a', 'b', 'c', 'a'])
        self.w.list.remove('a')
        self.assertEqual(self.w.list.get(), ['b', 'c', 'a'], 'remove')
        #
        self.w.list.set(['a', 'b', 'b', 'c'])
        self.assertEqual(self.w.list.index('b'), 1, 'index')
        #
        self.w.list.set(['a', 'b', 'c'])
        self.w.list.insert(1, 'z')
        self.assertEqual(self.w.list.get(), ['a', 'z', 'b', 'c'], 'insert')
        #
        self.w.list.set(['a', 'b', 'c'])
        self.w.list.extend(['x', 'y', 'z'])
        self.assertEqual(self.w.list.get(), ['a', 'b', 'c', 'x', 'y', 'z'], 'extend')
        #
        self.w.list.set(['a', 'b', 'c'])
        self.w.list.setSelection([0])
        self.assertEqual(self.w.list.getSelection(), [0], 'getSelection')
        self.w.list.setSelection([1])
        self.assertEqual(self.w.list.getSelection(), [1], 'setSelection')
        self.w.list.setSelection([])
        self.assertEqual(self.w.list.getSelection(), [], 'setSelection empty')
        #
        self.w.list.set(['x', 'y', 'z'])
        self.assertEqual(self.w.list.get(), ['x', 'y', 'z'], 'set')
        #
        self.finish()



def testAll():
    ButtonTest()
    TextBoxTest()
    PopUpButtonTest()
    CheckBoxTest()
    EditTextTest()
    ListTest()
