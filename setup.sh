#!/bin/bash
# Install launchd agents from this repo, load them, verify processes, show crontab.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCH_AGENTS="${HOME}/Library/LaunchAgents"

PLISTS=(
  com.sonicsaga.standup.plist
  com.sonicsaga.hlpnl.plist
)

LABELS=(
  com.sonicsaga.standup
  com.sonicsaga.hlpnl
)

SCRIPTS=(
  standup.py
  hl_pnl.py
)

failures=0

unload_plist() {
  local dest=$1
  launchctl bootout "gui/$(id -u)" "$dest" 2>/dev/null \
    || launchctl unload "$dest" 2>/dev/null \
    || true
}

load_plist() {
  local dest=$1
  if launchctl bootstrap "gui/$(id -u)" "$dest" 2>/dev/null; then
    return 0
  fi
  launchctl load "$dest"
}

launchd_status() {
  local label=$1
  local line pid exit_code

  line=$(launchctl list 2>/dev/null | awk -v lbl="$label" '$3 == lbl {print; exit}')
  if [[ -z "$line" ]]; then
    echo "NOT LOADED"
    return 1
  fi

  pid=$(echo "$line" | awk '{print $1}')
  exit_code=$(echo "$line" | awk '{print $2}')

  if [[ "$pid" == "-" ]]; then
    echo "loaded, not running (last exit: ${exit_code})"
    return 1
  fi

  echo "running (PID ${pid})"
  return 0
}

echo "=== Installing and loading launchd agents ==="
mkdir -p "$LAUNCH_AGENTS"

for plist in "${PLISTS[@]}"; do
  src="${SCRIPT_DIR}/${plist}"
  dest="${LAUNCH_AGENTS}/${plist}"

  if [[ ! -f "$src" ]]; then
    echo "ERROR: missing ${src}"
    failures=$((failures + 1))
    continue
  fi

  cp "$src" "$dest"
  unload_plist "$dest"
  if load_plist "$dest"; then
    echo "Loaded: ${plist}"
  else
    echo "ERROR: failed to load ${plist}"
    failures=$((failures + 1))
  fi
done

echo ""
echo "=== Launchd status ==="
for i in "${!LABELS[@]}"; do
  label="${LABELS[$i]}"
  plist="${PLISTS[$i]}"
  status=$(launchd_status "$label")
  rc=$?
  echo "${label} (${plist}): ${status}"
  if [[ $rc -ne 0 ]]; then
    failures=$((failures + 1))
  fi
done

echo ""
echo "=== Process check ==="
for script in "${SCRIPTS[@]}"; do
  matches=$(pgrep -fl "$script" 2>/dev/null || true)
  if [[ -n "$matches" ]]; then
    while IFS= read -r line; do
      echo "  OK: ${line}"
    done <<< "$matches"
  else
    echo "  MISSING: no process matching ${script}"
    failures=$((failures + 1))
  fi
done

echo ""
echo "=== Crontab ==="
if crontab -l 2>/dev/null; then
  :
else
  echo "(empty or no crontab for $(whoami))"
fi

echo ""
if [[ $failures -eq 0 ]]; then
  echo "Summary: all services OK"
  exit 0
else
  echo "Summary: ${failures} problem(s) — check messages above"
  exit 1
fi
