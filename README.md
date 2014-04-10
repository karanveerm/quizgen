# QGen: Html Quiz Generator

Description: Dead simple way to create HTML quizzes with LaTeX support. Can be used to generate quizzes like: http://stanford.edu/~kvmohan/QGen/sample.html. Tested with Python 2.6/2.7. Shoot me an email if it doesn't work for newer versions.

## Table of Contents
[Setup](#setup)   
[Quiz Structure](#structure)   
[Creating Quizzes](#create)   
[Samples](#samples)   
[Getting Started](#start)   
[What the files in the directory do](#files)   
[Feature Requests / Contributing changes / Issues](#issues)   
[FAQ](#faq)   
[MIT License](#license)   

<a name="setup"/>
## Project Setup

How do I start using QGen?

1. git clone the repository
2. Everything you need is in the directory!

<a name="structure"/>
## Quiz Structure

- A quiz consists of a quiz title and problem groups.
- A problem group is a set of problems related in some way, where the relation is usually a common introduction.
- For example, if you wish to specify some values that are to be used for the next 2-3 questions, these 2-3 questions should be part of the same problem group.

### Problem Groups

- A problem group consists of a title, an intro (that will be common to all questions in this group) and the questions themselves.
- Each question will consist of a description of the question, and a set of options. Each option will have an explanation(optional) and whether or not it is correct.
- Note that it is not necessary for a problem group to have a title and an introduction. If you simply wish to group a few questions together, you can just put them in the same problem group, as explanined below.

<a name="create"/>
## Creating Quizzes

- `cp sample.quiz your_quiz_name.quiz` to get a starter template.
- A quiz would look like this:

```
== Sample Quiz Title
[Problem Group 1 Title]
This is the statement for problem group one.
I can add a link to ||LINK: www.google.com||.
Here's an image of a famous mathematician ||IMG:http://upload.wikimedia.org/wikipedia/commons/9/9b/Carl_Friedrich_Gauss.jpg||
Of course, we support LaTeX:
$
a = \begin{pmatrix} 1 \\ 3 \\ 2 \end{pmatrix} \text{ , }
b = \begin{pmatrix} 2 \\ 6 \\ 4 \end{pmatrix} \text{ , }
c = \begin{pmatrix} 1 \\ 3 \\ 0 \end{pmatrix} \text{ , }
d = \begin{pmatrix} 2 \\ 6 \end{pmatrix} \text{ , }
\text{and }
e = \begin{pmatrix} 0 \\ 0 \\ 4 \end{pmatrix}
$
A blank line marks the end of this problem group intro and beginning of the first question.

This is the first question in the problem group with some latex: $a_3$. ?
* This is an option. :: You can add an explanation for an option after the double colon to explain why it is correct/incorrect.
* This is another option. Observe that explanations are optional.
*= This option is the correct option since it has an equal to sign.

Again, a blank line marks the end of the options. Here's another question in this problem group with more latex $c$ and $d$?
* Yes
*= No

[]
This problem group has no title and has no introduction. When the text following the start of a new problem group is immediately followed by the options, it is inferred to be a question?
*= Yes I understand :: Great! Here's some latex $\|a + b + c\| $
* No :: Please email me and I'll help!

This is another question in this problem group?
* This is a great tutorial!
*= This is a terrible tutorial, I'm going to email you with suggestions so you can do a better job.
```

<a name="samples"/>
## Samples

sample.quiz is a great place to get started. A list of samples can also be found in the ee103/ directory.

<a name="start"/>
## Getting started

1. Run `python generate_quiz.py filename.quiz`
2. This will generate a file called filename.html
3. Open filename.html to see what your quiz looks like. It only depends on quiz.css which you can edit as felt necessary for a prettier quiz.

<a name="files"/>
## What the files in the directory do

- quiz.css: This containts the css for the html files you create.
- template.html: This is the template used to generate the HTML pages.
- quiz_parser.py: This parses the .quiz file and stores it in a python dictionary.
- generate_quiz.py: Calls quiz_parser.py to get the dictionary data of the quiz and then creates DOM elements for it so that it can be shown as an HTML page.

<a name="issues"/>
## Feature Requests / Contributing changes / Issues

- Feel free to make a pull request, I'll review the code and merge.
- Or just file an issue.
- Alternatively, email kvmohan [at] stanford [dot] edu and I'll try to help you ASAP!

<a name="faq"/>
## FAQ

1. Why did you work on this?

   Often professors want short, ungraded quizzes at the end of lectures where students can quickly decide how well they understood the material in the class. For example: I have heard several students really like Coursera's in-video quizzes. I could not find any light-weight way of doing this anywhere, so I hacked one up myself in a few hours.

2. Are there any classes using this?

   Stanford's EE263 and EE364A use something similar to generate quizzes like this: http://www.stanford.edu/class/ee364a/quizzes/unconstrained.html. QGen is fully compatible with the .quiz files used to create the 263 and 364A quizzes.
   Hopefully, they/other classes will be using QGen soon.


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
