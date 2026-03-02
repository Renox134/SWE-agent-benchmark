---
# yaml-language-server: $schema=schemas\page.schema.json
Object type:
    - Page
Backlinks:
    - Reports
    - Failure Checklist With Sonnet
Creation date: "2026-03-02T10:34:34Z"
Created by:
    - Philip
id: bafyreifsa7r7uocfrmfslr26gc7jecowoildacucdaj7tlrewyiobagy3q
---
# pydata\_\_xarray-7229   
## Issue to solve (rough breakdown)   
A past commit to xarray made it such that coordinate attributes could be overwritten by variable attributes, while the should be preserved.   
Difficulty estimation: 15 min - 1 hour   
## LLM performance   
The patches provided by the LLMs didn't solve the issue, as the overwriting still took place.   
Interestingly, there was a slight difference in how the LLMs failed:   
Qwen/Deepseek:   
```
>       assert_identical(expected, actual)
E       AssertionError: Left and right DataArray objects are not identical
E       
E       Differing coordinates:
E       L * a        (a) int64 0 1
E           attr: x_coord
E       R * a        (a) int64 0 1
E           attr: x_da
```
Claude-Sonnet:   
```
>       assert_identical(expected, actual)
E       AssertionError: Left and right DataArray objects are not identical
E       
E       Differing coordinates:
E       L * a        (a) int64 0 1
E           attr: x_coord
E       R * a        (a) int64 0 1
E           attr: cond_coord
```
The last lines were different (attr: x\_da vs. attr: cond\_coord).   
Test setup:   
```
def test_where_attrs() -> None:
        cond = xr.DataArray([True, False], coords={"a": [0, 1]}, attrs={"attr": "cond_da"})
        cond["a"].attrs = {"attr": "cond_coord"}
        x = xr.DataArray([1, 1], coords={"a": [0, 1]}, attrs={"attr": "x_da"})
        x["a"].attrs = {"attr": "x_coord"}
        y = xr.DataArray([0, 0], coords={"a": [0, 1]}, attrs={"attr": "y_da"})
        y["a"].attrs = {"attr": "y_coord"}
    
        # 3 DataArrays, takes attrs from x
        actual = xr.where(cond, x, y, keep_attrs=True)
        expected = xr.DataArray([1, 0], coords={"a": [0, 1]}, attrs={"attr": "x_da"})
        expected["a"].attrs = {"attr": "x_coord"}
        assert_identical(expected, actual)



```
   
