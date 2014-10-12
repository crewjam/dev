import argparse
import sys

from dev.units.gerrit import Build as BuildGerrit
from dev.units.nginx import Build as BuildNginx
from dev.units.chaosmonkey import Build as BuildChaosMonkey

def BuildUnits(options, output):
  BuildChaosMonkey(options, output)
  BuildGerrit(options, output)
  BuildNginx(options, output)

def Main(args=sys.argv[1:]):
  parser = argparse.ArgumentParser()
  #parser.add_argument("--discovery-url")
  parser.add_argument("--output", default=".")
  options = parser.parse_args(args)

  BuildUnits(options, options.output)

if __name__ == "__main__":
  Main()