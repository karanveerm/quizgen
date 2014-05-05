# Quizgen: Html Quiz Generator

Description: Dead simple way to create HTML quizzes with LaTeX support. Can be used to generate quizzes like: http://stanford.edu/~kvmohan/quizgen/sample.html. Problems with multiple correct answers are supported and images can also be embedded. Tested with Python 2.6/2.7. Shoot me an email at kvmohan [at] stanford [dot] edu if it doesn't work for newer versions.

## Table of Contents
[Setup](#setup)   
[Quiz Structure](#structure)   
[Creating Quizzes](#create)   
[Samples](#samples)   
[Getting Started](#start)   
[Feature Requests / Contributing changes / Issues](#issues)   
[FAQ](#faq)   
[Credits](#credits)   
[MIT License](#license)   

<a name="setup"/>
## Project Setup

How do I start using Quizgen?

1. Copy over the file [quizgen.py](https://raw.githubusercontent.com/karanveerm/quizgen/master/quizgen.py).
2. Everything you need is in the file!
3. Run `python quizgen.py` to get help on usage. 
4. You might want to alias it or `sudo cp quizgen.py /usr/bin/quizgen` so you can simply type in quizgen. 
5. Remember to `sudo chmod +x /usr/bin/quizgen` to make the file executable.

<a name="structure"/>
## Quiz Structure

The source for a quiz is a text file (saved with a .quiz extension) with the following quiz components:
- A quiz consists of a quiz title and one or more problem groups.
- A problem group contains an optional title, an optional introduction text that will be common to all the problems in the problem group, and a set of problems.
- Each problem consists of the text that poses the problem and two or more options. The students will click on one or more of these options.
- An option consists of text that is displayed, an optional '=' sign that indicates that the option is correct, and an optional explanation that is displayed when the option is selected.

<a name="create"/>
## Creating Quizzes

- Run `python quizgen.py -c` to get a starter quiz template saved as 'sample.quiz'.
- A quiz would look like this:

```
== Sample Quiz Title
[Problem Group 1 Title]
This is the statement for problem group one.
You can add a link to websites like this: ||LINK: http://www.google.com||.
You can add images like this:
||IMG:http://upload.wikimedia.org/wikipedia/commons/9/9b/Carl_Friedrich_Gauss.jpg||
The image source can either be a local path, or some URL. Images can be embedded
anywhere: within problem groups, problems or options.
Quizgen supports LaTeX:
\[
a = \begin{pmatrix} 1 \\ 3 \\ 2 \end{pmatrix} , \quad
b = \begin{pmatrix} 2 \\ 6 \\ 4 \end{pmatrix} , \quad
c = \begin{pmatrix} 1 \\ 3 \\ 0 \end{pmatrix} .
\]
A blank line marks the end of this problem group introduction text and the
beginning of the first problem.

This is the first problem in the problem group with some LaTeX: $a_3$.
* This is an option. :: You can add an explanation for an option after the double
colon to explain why it is correct/incorrect.
* This is another option. Observe that explanations are optional.
*= This option is the correct option since it is marked with an equal to sign.

Again, a blank line marks the end of the options. Here's another problem in
this problem group with more inline latex $c$ and $d$.
Quizgen supports displayed equations as well:
\[
x=Zy + a - c.
\]
* Yes.
*= No.

You can also have problems with multiple correct responses.
Students will be asked to select all that apply, and then submit their
responses.
*= Option 1.
* Option 2.
* Option 3.
*= Option 4. :: This is another correct option.

[]
This problem group has no title and has no introduction.
When the text following the start of a new problem group is immediately followed by the options,
it is inferred to be a problem.
*= Yes I understand. :: Great! Here's some latex $\|a + b + c\|.$
* No. :: Please email me and I'll try to help!

This is another problem in this problem group.
* This is a great tutorial!
*= This tutorial can be improved. I'm going to email you with suggestions so you can do a better job.

```

<a name="samples"/>
## Samples

sample.quiz is a great place to get started. A list of samples can also be found in the ee103/ and ee364a/ directory.

<a name="start"/>
## Getting started

1. Run `python quizgen.py filename.quiz` or `python quizgen.py filename`.
2. This will generate a file called filename.html and a CSS file called quiz.css (if it did not already exist).
3. Open filename.html to see what your quiz looks like. You can edit quiz.css if you’d like to modify the appearance of the quiz.


<a name="issues"/>
## Feature Requests / Contributing changes / Issues

- Feel free to make a pull request; I'll review the code and merge.
- Or just file an issue.
- Alternatively, email kvmohan [at] stanford [dot] edu and I'll try to help you ASAP!

<a name="faq"/>
## FAQ

1. Can we keep track of how students perform on the quizzes?

   No. Quizgen generates quizzes that are only for self-assessment; it does not support logging of responses.
   
2. Why did you work on this?

   I was hoping to create simple, lightweight method for instructors to generate quizzes that can be easily incorporated into a course website, allowing students to quickly get some feedback on how well they understand the basic material in a class.
   
<a name="credits"/>
## Credits
Designed and implemented by Karanveer Mohan, with design input from [Stephen Boyd](http://www.stanford.edu/~boyd/). Partly based on a simple quiz generator developed by Eric Chu, that was used in Stanford’s EE263 and EE364a classes since 2012, but was never made public.

<a name="license"/>
## The MIT License

Copyright (c) 2014 Karanveer Mohan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
