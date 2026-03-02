# pytest-dev\_\_pytest-10356   
## Issue to solve (rough breakdown)   
When inheriting from two base classes which have pytest markers, the class will loose one of the markers.   
Expected difficulty: 1 - 4 hour   
## LMM performance   
It seems like no LLM could handle the given issue, as the markers from the actual and expected values differ.   
The tests all failed like this:   
```
from _pytest.mark.structures import get_unpacked_marks
    
        all_marks = get_unpacked_marks(C)
    
>       assert all_marks == [xfail("c").mark, xfail("a").mark, xfail("b").mark]
E       AssertionError: assert <generator ob...x7f499de3e6d0> == [Mark(name='x...), kwargs={})]
E         Use -v to get more diff

testing/test_mark.py:1133: AssertionError
```
