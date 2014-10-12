
import re

def AWSSafeString(name):
  """
  Returns a version of name that is likely to meet AWS requirements for the
  names of AWS resources.
  """
  return re.sub("[^A-Za-z0-9]", "", name.title())
