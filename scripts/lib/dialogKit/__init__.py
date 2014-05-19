"""
dialogKit: easy bake dialogs
"""

# determine the environment
haveFL = False
haveVanilla = False
try:
    import FL
    haveFL = True
except ImportError:
    pass
if not haveFL:
    try:
        import vanilla
        haveVanilla = True
    except ImportError:
        pass
# perform the environment specific import
if haveFL:
    from _dkFL import *
elif haveVanilla:
    from _dkVanilla import *
else:
    raise ImportError, 'dialogKit is not available in this environment'

numberVersion = (0, 0, "beta", 1)
version = "0.0.1b"
