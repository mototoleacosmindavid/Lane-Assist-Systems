import sys
print(sys.path)
try:
    import PyQt5
except ModuleNotFoundError:
    print("The module 'module_name' is not installed. ")
    # You can include additional instruction here, such as installing the module.
else:
    # Code to run if the module  is successfully imported
    print(" Module 'module_name' is installed. ")
