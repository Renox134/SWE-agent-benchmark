# pylint-dev\_\_pylint-8898   
## Issue to solve (rough breakdown)   
Pylint is not able to handle regular expressions which contain commas. It crashes immediately.   
Expected difficulty: 1 - 4 hour   
## LMM performance   
In the first test, it seems like Qwen & Deepseek just split the regular expression String at the comma in half as a solution which is definitely false. In the second test, pylint could not handle the splitted regular expression as it has an unterminated subpattern and resulted into an error.   
Claude-sonnet already failed at the start of the test pipeline, where a module named '\_distutils\_hack' could not be found.   
   
Qwen & Deepseek:   
```
>       assert _template_run(in_string) == [re.compile(regex) for regex in expected]
E       AssertionError: assert [re.compile('...compile('3}')] == [re.compile('...e('bar{1,3}')]
E         At index 1 diff: re.compile('bar{1') != re.compile('bar{1,3}')
E         Left contains one more item: re.compile('3}')
E         Use -v to get more diff

tests/config/test_config.py:142: AssertionError
```
```
assert (
            r"Error in provided regular expression: (foo{1,} beginning at index 0: missing ), unterminated subpattern"
            in output.err
        )
E       AssertionError: assert 'Error in provided regular expression: (foo{1,} beginning at index 0: missing ), unterminated subpattern' in 'usage: pylint [options]\npylint: error: argument --bad-names-rgxs: Error in provided regular expression: (foo{1 beginning at index 0: missing ), unterminated subpattern\n'
E        +  where 'usage: pylint [options]\npylint: error: argument --bad-names-rgxs: Error in provided regular expression: (foo{1 beginning at index 0: missing ), unterminated subpattern\n' = CaptureResult(out='', err='usage: pylint [options]\npylint: error: argument --bad-names-rgxs: Error in provided regular expression: (foo{1 beginning at index 0: missing ), unterminated subpattern\n').err

tests/config/test_config.py:171: AssertionError
```
Claude-sonnet   
```
+ pytest -rA tests/config/test_config.py
Error processing line 1 of /opt/miniconda3/envs/testbed/lib/python3.9/site-packages/distutils-precedence.pth:

  Traceback (most recent call last):
    File "/opt/miniconda3/envs/testbed/lib/python3.9/site.py", line 177, in addpackage
      exec(line)
    File "<string>", line 1, in <module>
  ModuleNotFoundError: No module named '_distutils_hack'
```
