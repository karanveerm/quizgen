import itertools
import pprint


def make_backwards_compatible(lines):
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


def jump_to_non_blank_line(lines):
  """
  Returns the list of lines starting from the first line that is not empty.
  Returns [] if no lines remain
  """
  while lines and not lines[0]:
    lines = lines[1:]
  return lines


def parse_title(lines):
  """
  The quiz must begin with a "== " followed by an optional title.
  If the title exists, it returns th title, empty string otherwise
  """
  first_line = lines[0]
  if first_line.startswith('== '):
    return first_line[3:]
  raise Exception('Invalid format. Quiz must start with "== " followed by an optional title.')


def parse_new_problem_group(line_group):
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


def parse_explanation_and_description(line):
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


def parse_new_question(line_group):
  """
  Parses a new question for a given problem group. A question consists of a
  description and a number of options. A correct option begins with *= and an
  incorrect option begins with *. An explanation begins with ::
  """
  question = {
    'description': '',
    'options': []
  }

  while not line_group[0].startswith('*'):
    question['description'] += '\n' + line_group[0]
    line_group = line_group[1:]

  for line in line_group:
    if line[0] == '*':
      # New option
      has_explanation, explanation, description = parse_explanation_and_description(line)
      option = {
        'explanation': explanation,
        'description': description,
        'correct': True if line.startswith('*= ') else False
      }
      question['options'].append(option)
    else:
      # Continuation of the description or explanation of the previous option
      if has_explanation:
        question['options'][-1]['explanation'] += '\n' + line
      else:
        has_explanation, explanation, description = parse_explanation_and_description(line)
        question['options'][-1]['description'] += '\n' + description
        question['options'][-1]['explanation'] += '\n' + explanation

  return question


def parse(filename):
  # Open the file and read in the lines
  try:
    quizfile = open(filename, 'r')
  except IOError:
    print 'No file named %s found' % filename

  lines = quizfile.readlines()
  lines = [line.strip() for line in lines]
  lines = make_backwards_compatible(lines)

  quiz = {
    'title': parse_title(lines),
    'problem_groups': []
  }
  lines = jump_to_non_blank_line(lines[1:])

  for is_empty_line, line_group in itertools.groupby(lines, lambda line: not line):
    if is_empty_line: continue

    line_group = list(line_group)

    if line_group[0].startswith('[') and any(line.startswith('*') for line in line_group):
      # Grotesque code needed for backwards compatibility
      # Problem groups need not have intros so a [TITLE] can be immediately followed by
      # a question. This takes care of that case
      problem_group = parse_new_problem_group(line_group)
      problem_group['problem_intro'] = ''
      quiz['problem_groups'].append(problem_group)
      line_group = line_group[1:]

    if line_group[0].startswith('['):
      # Marks the beginning of a new problem group
      problem_group = parse_new_problem_group(line_group)
      quiz['problem_groups'].append(problem_group)
    else:
      # This is a single question that corresponds to the last problem_group in the line_group
      question = parse_new_question(line_group)
      try:
        quiz['problem_groups'][-1]['questions'].append(question)
      except Exception:
        print 'ERROR. Are you sure you started every problem group with "[]"?'

  return quiz
