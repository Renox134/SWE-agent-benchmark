# pytest-dev\_\_pytest-6197   
## Issue to solve (rough breakdown)   
Pytest tries to import any '\_\_init\_\_.py' files in the current directory. There are some packages that are only used on windows and cannot be import on linux, which causes the problem.   
Expected difficulty: 1 - 4 hour   
## LMM performance   
Here the results were very different. All LLM's failed multiple times at different tasks, but all the the failed tasks are in the same test class 'test\_collection.py'. Most of the tasks failed entirely and some tasks failed at an assertion. This is not a surprise to us, since while working on the project, we had a lot of issues with LLM's in combination with different OS's (especially Windows - Linux).   
   
