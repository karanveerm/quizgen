from xml.dom import minidom
import quiz_parser
import sys
import re
import glob


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
  selector_div.appendChild(doc.createTextNode(option['description']))

  response_div = doc.createElement('div')
  # response_div.attributes['class'] = 'response'

  span = doc.createElement('span')
  if option['correct']:
    span.attributes['class'] = 'right'
    response_div.attributes['class'] = 'response right'
    span.appendChild(doc.createTextNode('Correct! '))
  else:
    span.attributes['class'] = 'wrong'
    response_div.attributes['class'] = 'response wrong'
    span.appendChild(doc.createTextNode('Incorrect. '))
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

  response_div = doc.createElement('div')

  explanation = ''
  if option['correct']:
    response_div.attributes['class'] = 'response right'
    explanation = 'This option is correct. '
  else:
    response_div.attributes['class'] = 'response wrong'
    explanation = 'This option is incorrect. '


  response_div.appendChild(doc.createTextNode(explanation + option['explanation']))

  label.appendChild(checkbox)
  label.appendChild(selector_span)
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
  button.appendChild(doc.createTextNode('Submit'))
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

  first_question = True
  for question in problem_group['questions']:
    hr = doc.createElement('hr')
    if not first_question or problem_group['problem_intro']:
      fieldset.appendChild(hr)
    first_question = False
    elem = create_dom_from_question(question)
    fieldset.appendChild(elem)

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

  for problem_group in quiz['problem_groups']:
    elem = create_dom_from_problem_group(problem_group)
    wrapper.appendChild(elem)
    wrapper.appendChild(doc.createElement('br'))

  return wrapper


def add_dom_to_template(dom, html_file_name, quiz):
  """
  Expects a template called 'template.html' with a [BODY] holder where the body
  will be added and a [TITLE] holder for title.
  """
  generated_file = open(html_file_name, 'w+')
  template_file =  open('template.html')

  content = template_file.read()
  content = content.replace('[TITLE]', quiz['title'])
  content = content.replace('[BODY]', dom.toprettyxml())

  # For the images
  content = re.sub('\|\|IMG:\s?(\S+)\|\|', r'<div><img src="\1"></div>', content)

  # For the links
  content = re.sub('\|\|LINK:\s?(\S+)\|\|', r'<a href="\1">\1</a>', content)

  generated_file.write(content)
  generated_file.close()


if __name__ == '__main__':
  if len(sys.argv) < 2:
    raise Exception('Usage: python generate_quiz.py quiz_name.quiz generated_html_name.html')

  for filename in sys.argv[1:]:
    quiz = quiz_parser.parse(filename)

    dom = create_dom_from_quiz(quiz)

    if len(sys.argv) > 2 and '.html' in sys.argv[2]:
      html_file_name = sys.argv[2]
    else:
      html_file_name = filename.replace('.quiz', '.html')
    add_dom_to_template(dom, html_file_name, quiz)
