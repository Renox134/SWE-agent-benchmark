# pydata\_\_xarray-6992   
## Issue to solve (rough breakdown)   
There was an index refactor in xarray that caused some problems. In particular, 'xr.core.dataset.DataVariables\` assumed that everything that is in `ds.\_dataset.\_variables`  and not in `self.\_dataset.\_coord\_names`  is a "data variable". However, due to the prior refactor, this is was no longer true and produced multiple issues that needed to be fixed.   
Difficulty estimation: >4 hours   
## LLM performance   
The LLMs didn't provide a patch that solved the underlying issue, since none of the tests that were supposed to be fixed by the patch were actually fixed. Still, no PassToPass tests were effected.   
Interestingly, the exact test failure have some minor variation between the three tested LLMs.   
Example:   
Claude-Sonnet/Qwen:   
```
AssertionError: assert 'foo' not in Frozen
where Frozen({'foo': <xarray.IndexVariable 'x' (x: 4)>\narray(['a', 'a', 'b', 'b'], dtype=object), 'bar': <xarray.IndexVariable 'x' (x: 4)>\narray([1, 2, 1, 2])}) = <xarray.Dataset>
Dimensions:  (x: 4)
Coordinates:
    foo      (x) object 'a' 'a' 'b' 'b'
    bar      (x) int64 1 2 1 2
Data variables:
    *empty*.variables
```
Deepseek:   
```
AssertionError: assert 'foo' not in Frozen
where Frozen({'foo': <xarray.IndexVariable 'x' (x: 4)>\narray(['a', 'a', 'b', 'b'], dtype=object), 'bar': <xarray.IndexVariable 'x' (x: 4)>\narray([1, 2, 1, 2])}) = <[ValueError('__len__() should return >= 0') raised in repr()] Dataset object at 0x7f7479dc1000>.variables
```
   
   
