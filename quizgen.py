#!/usr/bin/python3
# -*- coding: utf-8 -*-

# The MIT License (MIT)

# Copyright (c) 2014 Karanveer Mohan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import random
from random import shuffle
from xml.dom import minidom
import sys
import re
import glob
import itertools

import gettext
import os.path
if os.path.isdir('./mo'):
  gettext.install('quizgen', './mo')
else:
  gettext.install('quizgen')

"""
Parse the Quiz to create a python dict
"""

class QuizParser():
  """Parses the quiz and returns it in a python dict"""
  def __init__(self, filename):
    if '.quiz' in filename:
      self.filename = filename
    else:
      self.filename = '%s.quiz' % filename

    self.randomize = False;


  def get_filename(self):
    return self.filename


  def _make_backwards_compatible(self, lines):
    """
    Takes care of case where there is an empty line between question and options
    that existed in EE364A.
    """
    i = 0
    while True:
      if i == len(lines) - 1: break
      if not lines[i] and lines[i + 1].startswith('*'):
        del lines[i]
      i += 1
    return lines


  def _jump_to_non_blank_line(self, lines):
    """
    Returns the list of lines starting from the first line that is not empty.
    Returns [] if no lines remain
    """
    while lines and not lines[0]:
      lines = lines[1:]
    return lines


  def _parse_title(self, lines):
    """
    The quiz must begin with a "== " followed by an optional title.
    If the title exists, it returns the title, empty string otherwise
    """
    first_line = lines[0]
    if first_line.startswith('=='):
      return first_line[2:].lstrip()
    raise Exception('Invalid format. Quiz must start with "==" followed by an optional title.')


  def _parse_new_problem_group(self, line_group):
    """
    Parses a new problem group, i.e. the title of the main problem and the statement.
    Each problem group can have multiple questions associated with it.
    """
    title_line = line_group[0]
    if title_line.rfind(']') == -1:
      raise Exception('Problem title must be in the form [TITLE] with the square brackets')
    problem_intro = line_group[1:]

    return {
      # [Sensitivity Analysis] ==> 'Sensitivity Analysis'
      'problem_title': title_line[1:title_line.rfind(']')],
      'problem_intro': '\n'.join(problem_intro),
      'questions': []
    }


  def _parse_explanation_and_description(self, line):
    """
    Find the description for an option, and an explanation (if any)
    """
    if line.find('::') != -1:
      # We have an explanation for this option
      explanation = line[line.find('::') + 2:]
      description = line[line.find(' ') + 1:line.find('::')]
      has_explanation = True
    else:
      explanation = ''
      description = line[line.find(' ') + 1:]
      has_explanation = False

    return has_explanation, explanation, description


  def _parse_new_question(self, line_group):
    """
    Parses a new question for a given problem group. A question consists of a
    description and a number of options. A correct option begins with *= and an
    incorrect option begins with *. An explanation begins with ::
    """
    question = {
      'description': '',
      'options': []
    }

    try:
      while not line_group[0].startswith('*'):
        question['description'] += '\n' + line_group[0]
        line_group = line_group[1:]
    except:
      raise Exception('ERROR: Options for question not found. \n \
          Perhaps you put a blank line in your problem group?')
    for line in line_group:
      if line[0] == '*':
        # New option
        has_explanation, explanation, description = self._parse_explanation_and_description(line)
        option = {
          'explanation': explanation,
          'description': description,
          'correct': True if line.startswith('*=') else False
        }
        question['options'].append(option)
      else:
        # Continuation of the description or explanation of the previous option
        if has_explanation:
          question['options'][-1]['explanation'] += '\n' + line
        else:
          has_explanation, explanation, description = self._parse_explanation_and_description(line)
          question['options'][-1]['description'] += '\n' + description
          question['options'][-1]['explanation'] += '\n' + explanation

    return question


  def parse(self):
    # Open the file and read in the lines
    try:
      quizfile = open(self.filename, 'r',encoding="utf8")
    except IOError:
      raise Exception('No file named %s found' % self.filename)

    lines = quizfile.readlines()
    lines = [line.strip() for line in lines]
    lines = self._make_backwards_compatible(lines)

    quiz = {
      'title': self._parse_title(lines),
      'problem_groups': []
    }
    lines = self._jump_to_non_blank_line(lines[1:])

    for is_empty_line, line_group in itertools.groupby(lines, lambda line: not line):
      if is_empty_line: continue

      line_group = list(line_group)

      if line_group[0].startswith('[') and any(line.startswith('*') for line in line_group):
        # Grotesque code needed for backwards compatibility
        # Problem groups need not have intros so a [TITLE] can be immediately followed by
        # a question. This takes care of that case
        problem_group = self._parse_new_problem_group(line_group)
        problem_group['problem_intro'] = ''
        quiz['problem_groups'].append(problem_group)
        line_group = line_group[1:]

      if line_group[0].startswith('['):
        # Marks the beginning of a new problem group
        problem_group = self._parse_new_problem_group(line_group)
        quiz['problem_groups'].append(problem_group)
      else:
        # This is a single question that corresponds to the last problem_group in the line_group
        question = self._parse_new_question(line_group)
        try:
          quiz['problem_groups'][-1]['questions'].append(question)
        except:
          raise Exception('ERROR. Are you sure you started every problem group with "[]"?')

    if self.randomize:
      for pg in quiz["problem_groups"]:
        random.shuffle(pg["questions"])
        for ql in pg["questions"]:
          random.shuffle(ql["options"])

    return quiz


def create_single_choice_dom_from_option(option):
  """
  Creates dom look for a specific option of a question
  """
  doc = minidom.Document()

  li = doc.createElement('li')
  li.attributes['class'] = 'choice'

  # Each list element has a 'selector', i.e the option that can be selected
  # and a 'response', i.e the response to be shown when that option is selected
  selector_div = doc.createElement('div')
  selector_div.attributes['class'] = 'selection'
  selector_div.attributes['name'] = 'pg%04d_q%04d' % (option['pg_num'], option['q_num'])
  selector_div.appendChild(doc.createTextNode(option['description']))

  response_div = doc.createElement('div')
  # response_div.attributes['class'] = 'response'

  span = doc.createElement('span')
  if option['correct']:
    span.attributes['class'] = 'right'
    response_div.attributes['class'] = 'response right'
    span.appendChild(doc.createTextNode(_('Correct! ')))
  else:
    span.attributes['class'] = 'wrong'
    response_div.attributes['class'] = 'response wrong'
    span.appendChild(doc.createTextNode(_('Incorrect. ')))
  response_div.appendChild(span)
  response_div.appendChild(doc.createTextNode(option['explanation']))

  li.appendChild(selector_div)
  li.appendChild(response_div)

  return li


def create_single_choice_dom_from_question(question):
  """
  If a question only has one option correct, creates the dom look for that question
  """
  doc = minidom.Document()

  ol = doc.createElement('ol')
  ol.attributes['type'] = 'a'

  for option in question['options']:
    option['pg_num'] = question['pg_num']
    option['q_num'] = question['num']
    elem = create_single_choice_dom_from_option(option)
    ol.appendChild(elem)
  return ol


def create_multiple_choice_dom_from_option(option):
  """
  Creates options with checkboxes for multiple choice responses
  """
  doc = minidom.Document()

  label = doc.createElement('label')
  checkbox = doc.createElement('input')
  checkbox.attributes['type'] = 'checkbox'

  # Each list element has a 'selector', i.e the option that can be selected
  # and a 'response', i.e the response to be shown when that option is selected
  selector_span = doc.createElement('span')
  selector_span.attributes['class'] = 'multiple-selection'
  selector_span.appendChild(doc.createTextNode(option['description']))

  # Create nodes to show the checkmark and cross mark when students get options
  # in an MCQ right/wrong.
  correct_span = doc.createElement('span')
  correct_span.attributes['class'] = 'correct-checkbox'
  correct_span.appendChild(doc.createTextNode('✓'))

  incorrect_span = doc.createElement('span')
  incorrect_span.attributes['class'] = 'incorrect-checkbox'
  incorrect_span.appendChild(doc.createTextNode('✗'))

  response_div = doc.createElement('div')

  explanation = ''
  if option['correct']:
    response_div.attributes['class'] = 'response right'
    explanation = _('This option is correct. ')
  else:
    response_div.attributes['class'] = 'response wrong'
    explanation = _('This option is incorrect. ')


  response_div.appendChild(doc.createTextNode(explanation + option['explanation']))

  label.appendChild(checkbox)
  label.appendChild(selector_span)
  label.appendChild(correct_span)
  label.appendChild(incorrect_span)

  label.appendChild(response_div)

  return label


def create_multiple_choice_dom_from_question(question):
  """
  If a question only has multiple options correct, creates the dom look for that question.
  Puts a checkbox next to each option and adds a button allowing you to see the answer
  """
  doc = minidom.Document()

  div = doc.createElement('div')
  div.attributes['class'] = 'mcq'

  for option in question['options']:
    elem = create_multiple_choice_dom_from_option(option)
    div.appendChild(elem)

  button = doc.createElement('button')
  button.attributes['name'] = 'pg%04d_q%04d' % (question['pg_num'], question['num'])
  button.appendChild(doc.createTextNode(_('Submit')))
  div.appendChild(button)

  return div


def create_dom_from_question(question):
  """
  Creates dom look for question
  """
  doc = minidom.Document()

  wrapper = doc.createElement('div')
  div = doc.createElement('div')
  div.attributes['class'] = 'description'
  div.appendChild(doc.createTextNode(question['description']))
  wrapper.appendChild(div)

  num_correct = sum(1 for option in question['options'] if option['correct'])
  if num_correct == 1:
    el = create_single_choice_dom_from_question(question)
  else:
    el = create_multiple_choice_dom_from_question(question)

  wrapper.appendChild(el)
  return wrapper


def create_dom_from_problem_group(problem_group):
  """
  Creates the dom look for a problem group
  """
  doc = minidom.Document()

  fieldset = doc.createElement('fieldset')

  if problem_group['problem_title']:
    legend = doc.createElement('legend')
    legend.appendChild(doc.createTextNode(problem_group['problem_title']))
    fieldset.appendChild(legend)

  if problem_group['problem_intro']:
    div = doc.createElement('div')
    div.attributes['class'] = 'intro'
    div.appendChild(doc.createTextNode(problem_group['problem_intro']))
    fieldset.appendChild(div)

  q_num = 0
  for question in problem_group['questions']:
    question['pg_num'] = problem_group['num']
    question['num'] = q_num
    hr = doc.createElement('hr')
    if q_num > 0 or problem_group['problem_intro']:
      fieldset.appendChild(hr)
    elem = create_dom_from_question(question)
    fieldset.appendChild(elem)
    q_num = q_num + 1

  return fieldset


def create_dom_from_quiz(quiz):
  """
  Given a quiz dictionary, generates its DOM look.
  """
  doc = minidom.Document()
  wrapper = doc.createElement('div')

  header = doc.createElement('h1')
  header.appendChild(doc.createTextNode(quiz['title']))
  wrapper.appendChild(header)

  pg_num = 0
  for problem_group in quiz['problem_groups']:
    problem_group['num'] = pg_num
    elem = create_dom_from_problem_group(problem_group)
    wrapper.appendChild(elem)
    wrapper.appendChild(doc.createElement('br'))
    pg_num = pg_num + 1

  return wrapper


def add_dom_to_template(dom, html_file_name, quiz):
  """
  Expects a template called 'template.html' with a [BODY] holder where the body
  will be added and a [TITLE] holder for title.
  """
  generated_file = open(html_file_name, 'w+')
  try:
    template_file = open('template.html')
    content = template_file.read()
  except IOError:
    content = HTML
  # Add the header.  By replacing this early, we allow the header to
  # contain IMG and LINK tags (or even CODE), though it would typically
  # be pure HTML
  content = content.replace('[STYLES_SCRIPTS]', get_head());
  content = content.replace('[SUBMIT_LABEL]', _('Submit'))
  content = content.replace('[HIDE_LABEL]', _('Hide'))
  content = content.replace('[TEX]', get_tex())
  content = content.replace('[HEADER]', get_header())
  content = content.replace('[TITLE]', quiz['title'])
  content = content.replace('[BODY]', dom.toprettyxml())
  
  # Add the footer.  By replacing this early, we allow the footer to
  # contain IMG and LINK tags (or even CODE), though it would typically
  # be pure HTML
  content = content.replace('[FOOTER]', get_footer())
  
  # For the images
  content = re.sub('\|\|IMG:\s?(\S+)\|\|', r'<div><img src="\1"></div>', content)

  # For the links
  content = re.sub('\|\|LINK:\s?(\S+)\s+(\S.*)\|\|', r'<a href="\1">\2</a>', content)
  content = re.sub('\|\|LINK:\s?(\S+)\|\|', r'<a href="\1">\1</a>', content)

  # For code blocks
  content = re.sub('\|\|CODE:(\S+):\s?(.*?)\|\|', r'<pre><code class="\1">\2</pre></code>', content,
                   flags=re.DOTALL)

  content = re.sub('&lt;br\s*/&gt;', r'<br/>', content);
  content = re.sub('&lt;hr\s*/&gt;', r'<hr/>', content);
  content = re.sub('&lt;center&gt;', r'<span style="text-align: center;">', content);
  content = re.sub('&lt;/center&gt;', r'</span>', content);
  content = re.sub('&lt;blockquote&gt;', r'<blockquote>', content);
  content = re.sub('&lt;/blockquote&gt;', r'</blockquote>', content);
  content = re.sub('&lt;p&gt;', r'<p>', content);
  content = re.sub('&lt;/p&gt;', r'</p>', content);
  content = re.sub('&lt;em&gt;', r'<em>', content);
  content = re.sub('&lt;/em&gt;', r'</em>', content);
  content = re.sub('&lt;strong&gt;', r'<strong>', content);
  content = re.sub('&lt;/strong&gt;', r'</strong>', content);
  content = re.sub('&lt;code&gt;', r'<code>', content);
  content = re.sub('&lt;/code&gt;', r'</code>', content);
  content = re.sub('&lt;span(\s+[^&]*)&gt;', r'<span\1>', content);
  content = re.sub('&lt;/span&gt;', r'</span>', content);
  content = re.sub('&lt;div(\s+[^&]*)&gt;', r'<div\1>', content);
  content = re.sub('&lt;/div&gt;', r'</div>', content);
  content = re.sub('&lt;ul&gt;', r'<ul>', content);
  content = re.sub('&lt;/ul&gt;', r'</ul>', content);
  content = re.sub('&lt;ol&gt;', r'<ol>', content);
  content = re.sub('&lt;/ol&gt;', r'</ol>', content);
  content = re.sub('&lt;li&gt;', r'<li>', content);
  content = re.sub('&lt;/li&gt;', r'</li>', content);
  content = re.sub('&lt;sub&gt;', r'<sub>', content);
  content = re.sub('&lt;/sub&gt;', r'</sub>', content);
  content = re.sub('&lt;sup&gt;', r'<sup>', content);
  content = re.sub('&lt;/sup&gt;', r'</sup>', content);
  content = re.sub('&lt;u(nderline)?&gt;', r'<span style="text-decoration: underline;">', content);
  content = re.sub('&lt;/u(nderline)?&gt;', r'</span>', content);

  generated_file.write(content)
  generated_file.close()

  # Create the CSS file if it does not exist
  try:
    css_file = open('quiz.css')
  except IOError:
    print ('No CSS file called quiz.css found in directory. Using default CSS.')
    generated_css_file = open('quiz.css', 'w+')
    generated_css_file.write(CSS)
    generated_css_file.close()


def usage():
  print ("""
  Usage: python quizgen.py [options] SOURCE_QUIZ_FILE.
  You may like to:
  sudo cp quizgen.py /usr/bin/quizgen
  so that you can simply type quizgen.
  Remember to sudo chmod +x /usr/bin/quizgen to make the file executable.

  You can use quizgen simply by typing:
  quizgen index
  which will product an index.html from index.quiz file.
  In case no CSS styling is provided, it will also create a quiz.css file.

  If you want to create sample.quiz to get started, just type:
  python quizgen.py -c and a file called sample.quiz will be created.
  This file shows all the features of quizgen along with the format.
  
  You may provide a footer and/or header to appear on your quizzes by creating
  a file named footer.html and/or header.html that contains an html fragment.

  In order to shuffle questions and options use the -r option.

  More information and a lot of sample quizzes file can be found on:
  https://github.com/karanveerm/quizgen
  """)


def create_sample():
  try:
    sample_quiz_file = open('sample.quiz')
  except IOError:
    sample_quiz_file = open('sample.quiz', 'w+')
    sample_quiz_file.write(SAMPLE)
    sample_quiz_file.close()
    print ('A file called sample.quiz has been added to your directory.')
    print ('Please take a look at it to see how to create a quiz.')
  else:
    print ('A file called sample.quiz already exists in your current directory!')

# Should a header file exist return the content of that file
# otherwise return an empty string
def get_header():
  try: 
     header_file = open('header.html')
  except IOError:
     header = ''
  else:
     header = header_file.read()
  return header

# If the HTML <head> contents file exist return the content of that
# file, otherwise return the STYLES_SCRIPTS.
custom_head = False
def get_head():
  global custom_head
  try:
     header_file = open('head.html')
  except IOError:
     header = STYLES_SCRIPTS
  else:
     header = header_file.read()
     custom_head = True
  return header

# Returns standard TeX header with standard HTML <head> and empty
# string otherwise.
def get_tex():
  if not custom_head:
    return r"""$\newcommand{\ones}{\mathbf 1}$"""
  else:
    return ''
  
# Should a footer file exist return the content of that file
# otherwise return the standard footer
def get_footer():
  try: 
     footer_file = open('footer.html')
  except IOError:
     footer = """<div id="footer_results">"""
     footer += _('<span class="heading">Your results:</span> <span class="right_counter"><span class="value">%d</span></span> right answer(s) and <span class="wrong_counter"><span class="value">%d</span></span> mistake(s)!') % (0, 0)
     footer += """
  </div>"""
     footer += _('Page generated using %s') % '<a href=\"https://github.com/karanveerm/quizgen\">Quizgen</a>'
     footer += """
  <div id="floating_results" class="results">
    <div class="right_counter">
      <span class="value">0</span>
    </div>
    <span class="delimiter">/</span>
    <div class="wrong_counter">
      <span class="value">0</span>
    </div>
  </div>"""
  else:
     footer = footer_file.read()
  return footer
  
def main():
  # TODO: Stop being lazy and use optparse.
  if len(sys.argv) < 2 or '-h' in sys.argv[1]:
    usage()
  elif '-c' in sys.argv[1]:
    create_sample()
  else:
    randomize = False
    if '-r' in sys.argv[1]:
      sys.argv.pop(1)
      randomize = True
    for filename in sys.argv[1:]:
      quiz_parser = QuizParser(filename)
      quiz_parser.randomize = randomize

      quiz = quiz_parser.parse()

      dom = create_dom_from_quiz(quiz)
      html_file_name = quiz_parser.get_filename().replace('.quiz', '.html')

      add_dom_to_template(dom, html_file_name, quiz)



SAMPLE = """== Sample Quiz Title
[Problem Group 1 Title]
This is the statement for problem group one.
You can add a link to websites like this: ||LINK: http://www.google.com||.
You can add images like this:
||IMG:http://upload.wikimedia.org/wikipedia/commons/9/9b/Carl_Friedrich_Gauss.jpg||
The image source can either be a local path, or some web URL. Images can be embedded
anywhere: within problem groups, problems or options.
Quizgen supports LaTeX:
\[
a = \\begin{pmatrix} 1 \\\\ 3 \\\\ 2 \end{pmatrix} , \quad
b = \\begin{pmatrix} 2 \\\\ 6 \\\\ 4 \end{pmatrix} , \quad
c = \\begin{pmatrix} 1 \\\\ 3 \\\\ 0 \end{pmatrix} .
\]
A blank line marks the end of this problem group introduction text and the
beginning of the first problem.

This is the first problem in the problem group with some LaTeX: $a_3$.
* This is an option. :: You can add an explanation for an option after the double colon to explain why it is correct/incorrect.
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
*= Option 1. :: This option is correct.
* Option 2. :: This option is not correct.
* Option 3.
*= Option 4. :: This is another correct option.

[]
This problem group has no title and has no introduction. When the text following the start of a new problem group is immediately followed by the options, it is inferred to be a problem.
*= Yes I understand. :: Great! Here's some latex $\|a + b + c\|.$
* No. :: Please email me and I'll try to help!

This is another problem in this problem group.
* This is a great tutorial!
*= This tutorial can be improved. I'm going to email you with suggestions so you can do a better job.
"""

# HTML template
# TODO: Don't judge, I didn't want to do this
HTML = r"""
<!DOCTYPE html>
<html>
  <head>
    <title>[TITLE]</title>
    [STYLES_SCRIPTS]
    <script type="text/javascript">
      const SUBMIT_LABEL = '[SUBMIT_LABEL]';
      const HIDE_LABEL = '[HIDE_LABEL]';
    </script>

    <script type="text/javascript">
      var results = {};
      function updateResults (name, value) {
        if (!results[name]) {
          results[name] = value;
        }

        var right = 0;
        var wrong = 0;
        for (const key in results) {
          if (results[key] > 0) {
            right = right + 1;
          } else if (results[key] < 0) {
            wrong = wrong + 1;
          }
        };

        $('.right_counter .value').each(function () {
          this.innerText = right;
        });
        $('.wrong_counter .value').each(function () {
          this.innerText = wrong;
        });

        if (right > wrong) {
          $('.wrong_counter').toggleClass('rise', false);
          $('.right_counter').toggleClass('rise', true);
        } else if (wrong > right) {
          $('.right_counter').toggleClass('rise', false);
          $('.wrong_counter').toggleClass('rise', true);
        } else {
          $('.right_counter').toggleClass('rise', false);
          $('.wrong_counter').toggleClass('rise', false);
        }
      }
    </script>

    <script type="text/javascript">
    $(document).ready(function(){
      //close all the content divs on page load
      $('.response').hide();

      // toggle slide
      $('.selection').click(function(){
        // by calling sibling, we can use same div for all demos
        var name = $(this).attr('name');
        $(this).siblings('.response').each(function () {
          $(this).slideToggle('fast');
          updateResults(name, $(this).hasClass('right') ? 1 : -1);
        });
      });

      $('button').click(function(event){
        var $target = $(event.target);
        var $checkboxes = $target.parent('.mcq').find('input');
        var name = $(this).attr('name');
        var mistakes = 0;
        for (var i = 0; i < $checkboxes.length; i++) {
          var $checkbox = $checkboxes.eq(i);
          a = $checkbox;
          if ($checkbox[0].checked && $checkbox.nextAll('.response').hasClass('right')) {
            $checkbox.nextAll('.correct-checkbox').show();
          } else if ($checkbox[0].checked &&
              $checkbox.nextAll('.response').hasClass('wrong')) {
            $checkbox.nextAll('.incorrect-checkbox').show();
            mistakes = mistakes + 1;
          } else if (!$checkbox[0].checked &&
              $checkbox.nextAll('.response').hasClass('right')) {
            $checkbox.nextAll('.incorrect-checkbox').show();
            mistakes = mistakes + 1;
          } else {
            $checkbox.nextAll('.correct-checkbox').show();
          }
        }

        updateResults(name, mistakes == 0 ? 1 : -1);

        $target.parent('.mcq').find('.response').slideToggle('fast');
        if ($target.text() == SUBMIT_LABEL) {
          $target.text(HIDE_LABEL);
        } else {
          $checkboxes.nextAll('.incorrect-checkbox').hide();
          $checkboxes.nextAll('.correct-checkbox').hide();
          $target.text(SUBMIT_LABEL);
        }
      });
    });
    </script>
  </head>

<body>
  [TEX]
  [HEADER]
  [BODY]
  <footer>
  [FOOTER]
  </footer>
</body>
</html>
"""

# CSS template
# TODO: This is not something I'm proud of
CSS = """html {
  min-height: 100%;
}

body {
  margin-left: auto;
  margin-right: auto;
  padding: 0;
  font-family: 'PT Sans', 'Helvetica Neue', Helvetica, Arial, Sans-serif;
  font-size: 16px;
  position: relative;
  min-height: 100%;
  width: 680px;
  background-color: rgb(250, 250, 250);
  color: #333;
}

img {
  height: 400px;
  display: block;
  margin-left: auto;
  margin-right: auto;
  padding: 20px;
}

div .description {
  margin-top: 30px;
}

a {
  color: #000066;
}

div .selection {
  color: #000066;
  text-decoration: none;
}

div .selection:hover {
  text-decoration: underline;
}


span.right {
  color:#008800;
}

hr {
  width: 60%;
  margin-left: 0px;
  border: 0px;
  border-bottom: 1px solid #ccc;
}

fieldset {
  border: 0px;
  border-bottom: 2.5px solid #aaa;
  padding: 10px 20px;
  padding-left: 0px;
  margin-bottom: 0px;
  margin-top: 0px;
}

ol ul {
  padding-top: 10px;
  padding-bottom: 10px;
}

.selection {
  cursor: pointer;
  margin-top: 5px;
}

.multiple-selection {
  cursor: pointer;
  margin-top: 5px;
}

.correct-checkbox {
  color: #4F8A10;
  display: none;
}

.incorrect-checkbox {
  color: #D8000C;
  display: none;
}

legend {
  font-family: Alike, 'Josefin Sans';
  font-size: 19px;
  padding-left: 0px;
}


.response.wrong{
  padding: 8px 10px;
  color: #D8000C;
  background-color: #FFBABA;
  display: none;
}

.response.right{
  padding: 8px 10px;
  color: #4F8A10;
  background-color: #DFF2BF;
  display: none;
}

footer {
  font-size: 12px;
  margin-top: 0px;
  margin-bottom: 5px;
  bottom: 0;
  width: 100%;
}

label {
  display: block;
  padding-top: 5px;
  padding-bottom: 5px;
}

button {
  background: #bbb;
  border: 0px;
  color: #ffffff;
  font-size: 14px;
  padding: 6px 12px 6px 12px;
  text-decoration: none;
}

button:hover{
  background: #ccc;
}

button:focus {
    outline: none;
}

#floating_results {
  position: fixed;
  bottom: 0px;
  right: 0px;
  margin: 1em;
}

#floating_results .right_counter,
#floating_results .wrong_counter,
#floating_results .delimiter {
  display: inline-block;
  font-size: 150%;
  font-weight: bold;
  margin: 0px 0px;
  text-align: center;
  vertical-align: middle;
}

#floating_results .right_counter,
#floating_results .wrong_counter {
  border-radius: 50%;
  color: white;
  padding: 0.3em 0.6em;
  transition: padding 0.5s;
}

#floating_results .right_counter {
  background-color: green;
}

#floating_results .delimiter {
  background-color: transparent;
  padding: 0px 0px;
  margin: 0px 0px;
}

#floating_results .wrong_counter {
  background-color: red;
}

#floating_results .right_counter.rise,
#floating_results .wrong_counter.rise {
  padding: 0.5em 0.9em;
  transition: padding 0.5s;
}

#footer_results {
  margin: 1em 1em 3em 1em;
  text-align: center;
  font-size: 150%;
}

#footer_results .heading {
  font-style: italic;
  text-decoration: underline;
}

#footer_results .right_counter,
#footer_results .wrong_counter {
  font-style: italic;
  font-weight: bold;
}
"""

STYLES_SCRIPTS = r"""<meta charset="UTF-8" />
    <link href='https://fonts.googleapis.com/css?family=Josefin+Sans|Alike' rel='stylesheet' type='text/css'>
    <link rel="stylesheet" href="quiz.css" type="text/css" />
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    <script type="text/x-mathjax-config">
      MathJax.Hub.Config({
        tex2jax: {
          inlineMath: [ ['$','$'], ["\\(","\\)"] ],
          processEscapes: true
        }
      });
    </script>
    <script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.2/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/8.2/highlight.min.js"></script>
    <script>hljs.initHighlightingOnLoad();</script>
"""

if __name__ == '__main__':
  main()

