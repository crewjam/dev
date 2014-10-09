#!/usr/bin/python
import collections
import subprocess

from flask import Flask, Response, render_template, redirect, url_for

app = Flask(__name__)
app.config["FLEETCTL_COMMAND"] = "./fleet/bin/fleetctl"

Unit = collections.namedtuple("Unit", ("name", "stuff"))

@app.route("/")
def list_units():
  units = []
  proc = subprocess.Popen([app.config["FLEETCTL_COMMAND"], 'list-units'],
    stdout=subprocess.PIPE)

  _ = proc.stdout.readline()
  for line in proc.stdout:
    name, stuff = line.rstrip("\n").split("\t", 1)
    units.append(Unit(name, stuff))

  return render_template("list-units.html", units=units)

@app.route("/machines")
def get_machines():
  machines = []
  proc = subprocess.Popen([app.config["FLEETCTL_COMMAND"], 'list-machines'],
    stdout=subprocess.PIPE)
  _ = proc.stdout.readline()
  for line in proc.stdout:
    name, stuff = line.rstrip("\n").split("\t", 1)
    machines.append((name, stuff))
  return render_template("list-machines.html", machines=machines)

@app.route("/units/<unit>")
def get_unit(unit):
  status_output = subprocess.check_output([app.config["FLEETCTL_COMMAND"],
    "--strict-host-key-checking=false", "status", unit])\
    .decode("utf8")
  journal_output = subprocess.check_output([app.config["FLEETCTL_COMMAND"],
    "--strict-host-key-checking=false", "journal", "-lines=1000", unit])\
    .decode("utf8")
  cat_output = subprocess.check_output([app.config["FLEETCTL_COMMAND"],
    "--strict-host-key-checking=false", "cat", unit])\
    .decode("utf8")

  return render_template("unit.html", status_output=status_output,
    journal_output=journal_output, cat_output=cat_output, name=unit)

@app.route("/units/<unit>", methods=["DELETE"])
def destroy_unit(unit):
  subprocess.check_output([app.config["FLEETCTL_COMMAND"], "destroy", unit])
  return Response(code=204)

@app.route("/units/<unit>", methods=["POST"])
def start_unit(unit):
  subprocess.check_output([app.config["FLEETCTL_COMMAND"], "start", unit])
  return Response(code=204)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=4002, debug=True)