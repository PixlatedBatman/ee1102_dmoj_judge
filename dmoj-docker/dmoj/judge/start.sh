#!/bin/bash
# Build judge config: problem storage + autodetected runtimes, then start the judge (Python 3 only).
{
  echo "problem_storage_globs:"
  echo "  - /problems/*"
  cat /judge-runtime-paths.yml
} > /tmp/judge.yml
chmod 644 /tmp/judge.yml
exec /usr/bin/tini -- /judge/.docker/entry run -p 9999 -c /tmp/judge.yml --only-executors PY3 bridged "$JUDGE_NAME" "$JUDGE_KEY"
