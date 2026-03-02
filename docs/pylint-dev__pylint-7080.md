# pylint-dev\_\_pylint-7080   
## Issue to solve (rough breakdown)   
When running pylint recursively, the 'ignore-paths' in the pyproject.toml are completely ignored.   
Expected difficulty: 15 min - 1 hour   
## LMM performance   
It seems that no LLM managed it to ignore the 'ingore-paths' in the recursive runs. Pylint was supposed to find nothing, but found 20 issues, which should be in the paths to ignore.   
The tests all failed like this:   
```
msg = f"expected output status {code}, got {pylint_code}"
        if output is not None:
            msg = f"{msg}. Below pylint output: \n{output}"
>       assert pylint_code == code, msg
E       AssertionError: expected output status 0, got 20. Below pylint output: 
E         ************* Module failing
E         ignored_subdirectory/failing.py:1:0: C0114: Missing module docstring (missing-module-docstring)
E         ignored_subdirectory/failing.py:1:0: W0611: Unused import re (unused-import)
E         
E         -----------------------------------
E         Your code has been rated at 0.00/10
E         
E         
E       assert 20 == 0

tests/test_self.py:146: AssertionError
```
   
