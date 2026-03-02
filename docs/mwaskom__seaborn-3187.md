---
# yaml-language-server: $schema=schemas\page.schema.json
Object type:
    - Page
Backlinks:
    - Reports
    - Failure Checklist With Sonnet
Creation date: "2026-03-02T09:51:09Z"
Created by:
    - Philip
id: bafyreibh7rbb5spo3z5fidayi3wha7lqnild2katvrhdzhhba7zrtibfsu
---
# mwaskom\_\_seaborn-3187   
## Issue to solve (rough breakdown)   
In the legend of a plot, some numbers were inaccurately not scaled with a multiplicator (i.e., it said 3 instead of 3000, 4 instead of 4000 and so on).   
Difficulty estimation: 15 min - 1 hour   
## LLM Performance   
All three tested models had exactly the same testing outcome, where two FailToPass tests weren't fixed, but nothing else was effected.   
The tests all failed like this:   
Failing Test 1   
```
def test_legend_has_no_offset(self, xy):
    
        color = np.add(xy["x"], 1e8)
        p = Plot(**xy, color=color).add(MockMark()).plot()
        legend = p._figure.legends[0]
        assert legend.texts
        for text in legend.texts:
>           assert float(text.get_text()) > 1e7
E           AssertionError: assert 1.0 > 10000000.0
E            +  where 1.0 = float('1')
E            +    where '1' = get_text()
E            +      where get_text = Text(0, 0, '1').get_text
```
Failing Test 2   
```
def test_legend_has_no_offset(self, long_df):
    
        g = relplot(data=long_df, x="x", y="y", hue=long_df["z"] + 1e8)
        for text in g.legend.texts:
>           assert float(text.get_text()) > 1e7
E           AssertionError: assert 2.5 > 10000000.0
E            +  where 2.5 = float('2.5')
E            +    where '2.5' = get_text()
E            +      where get_text = Text(0, 0, '2.5').get_text
```
   
Both failures indicate that basically, the models simply didn't produce a patch that would append the desired zeros, while keeping everything else in tact.   
