#!/bin/bash
set -x

die() { echo $@; exit 1; }

# ---- settings (from etcd) ----------------------------------------------------

# true: dryrun mode, false: break stuff for reals
export chaos_leashed=true
export conformity_leashed=true
export janitor_leashed=true
export volume_tagging_leashed=true


# override scheduler and cause chaos now
export is_monkey_time=${is_monkey_time:-false}

# set the timezone for the scheduler
export timezone=$(etcdctl get /services/chaosmonkey/timezone ||
  echo "America/New_York")

# where to send email
export notify_email=$(etcdctl get /services/chaosmonkey/notify_email)
[ -z "$notify_email" ] && die "must set /services/chaosmonkey/notify_email"

# ---- credentials (from meta-data) --------------------------------------------
# (Disabled because the Java AWS client will automatically pull instance
# credentials for us)
# url=http://169.254.169.254/latest/meta-data
# role=$(curl $url/iam/security-credentials/ | grep "ChaosMonkeyRole")
# [ -z "$role" ] && die "cannot find credentials for ChaosMonkeyRole"
# credentials_json=$(curl $url/iam/security-credentials/$role)
# export AWS_ACCESS_KEY_ID=$(echo $credentials_json | jq -r '.AccessKeyId')
# export AWS_SECRET_ACCESS_KEY=$(echo $credentials_json | jq -r '.SecretAccessKey')
# export AWS_SECURITY_TOKEN=$(echo $credentials_json | jq -r '.Token')

# Guess the AWS region we are running in
export AWS_REGION=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/.$//')

# ---- build property files ----------------------------------------------------

for path in $(ls *.properties); do
  envsubst < $path > SimianArmy/src/main/resources/$(basename $path)
done

# ---- run it ------------------------------------------------------------------
cd SimianArmy
exec ./gradlew jettyRun