#!/usr/bin/env bash
#
# Run the complete testsuite in one wstest mode, with a given PyPy GC nursery
# size, under a memory limit; record the memory use and check the outcome
# (crossbario/autobahn-testsuite#171).
#
# The container under test is the "subject": the fuzzingclient, or the
# fuzzingserver. Its peer (an echo server, or wstest as testeeclient) is not
# under test and always runs with a small nursery.
#
# Environment:
#   IMAGE           the image to test (required)
#   MODE            fuzzingclient | fuzzingserver (required)
#   NURSERY         PYPY_GC_NURSERY for the subject, e.g. 4MB, or "unset" for
#                   PyPy's default, which depends on the CPU (required)
#   EXPECT          pass   - all cases run, peak memory at most PEAK_LIMIT_MIB
#                   oom    - the subject is killed for exceeding MEMORY_LIMIT;
#                            anything else is a failure
#                   report - record only
#                   (required)
#   MEMORY_LIMIT    memory limit of the subject (default 8g)
#   PEAK_LIMIT_MIB  for EXPECT=pass (default 3072)
#   OUT             output directory (default ./memory-report)
#   PORT            TCP port on localhost (default 9001)
#   TIMEOUT_S       give up after this many seconds (default 2400)
#   DOCKER          the docker command (default "docker")
#
set -euo pipefail

: "${IMAGE:?}" "${MODE:?}" "${NURSERY:?}" "${EXPECT:?}"
MEMORY_LIMIT="${MEMORY_LIMIT:-8g}"
PEAK_LIMIT_MIB="${PEAK_LIMIT_MIB:-3072}"
OUT="${OUT:-memory-report}"
PORT="${PORT:-9001}"
TIMEOUT_S="${TIMEOUT_S:-2400}"
DOCKER="${DOCKER:-docker}"

HERE="$(cd "$(dirname "$0")" && pwd)"
SUBJECT="wstest-memory-subject-${PORT}"
PEER="wstest-memory-peer-${PORT}"

case "${MODE}" in fuzzingclient|fuzzingserver) ;; *) echo "unknown MODE '${MODE}'" >&2; exit 2 ;; esac
case "${EXPECT}" in pass|oom|report) ;; *) echo "unknown EXPECT '${EXPECT}'" >&2; exit 2 ;; esac

mkdir -p "${OUT}/config"
OUT="$(cd "${OUT}" && pwd)"
for f in echo_server.py fuzzingclient.json fuzzingserver.json; do
    sed "s/:9001/:${PORT}/g" "${HERE}/${f}" > "${OUT}/config/${f}"
done

cleanup() {
    ${DOCKER} rm -f -v "${SUBJECT}" "${PEER}" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

# -- what runs where -----------------------------------------------------------

{
    echo "image:    ${IMAGE}"
    echo "image id: $(${DOCKER} image inspect -f '{{.Id}}' "${IMAGE}")"
    echo "pypy:     $(${DOCKER} run --rm "${IMAGE}" pypy --version 2>&1 | tr '\n' ' ')"
    # the nursery PyPy chooses by itself on this CPU (half the cache size)
    echo "default nursery: $(${DOCKER} run --rm "${IMAGE}" pypy -c \
        'import gc; print [l.split(":")[1].strip() for l in str(gc.get_stats()).splitlines() if "nursery" in l][0]' 2>&1)"
    echo "cpu:      $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //')"
    echo "cache:    $(grep -m1 'cache size' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //') (/proc/cpuinfo)"
    lscpu | grep -E '^L[0-9][a-z]? cache' | sed 's/^/lscpu:    /'
} | tee "${OUT}/environment.txt"

nursery_env=()
if [ "${NURSERY}" != "unset" ]; then
    nursery_env=(-e "PYPY_GC_NURSERY=${NURSERY}")
fi

# Wait until container $1 listens on the port; fail when it exits instead.
wait_for_port() {
    for _ in $(seq 60); do
        if (echo > "/dev/tcp/127.0.0.1/${PORT}") 2>/dev/null; then
            return 0
        fi
        if [ "$(${DOCKER} inspect -f '{{.State.Running}}' "$1")" != "true" ]; then
            break
        fi
        sleep 1
    done
    echo "$1 does not listen on port ${PORT}:" >&2
    ${DOCKER} logs --tail 20 "$1" >&2 || true
    return 1
}

# The cgroup (v2) directory of a running container, for memory.current/.peak.
cgroup_dir() {
    local pid
    pid="$(${DOCKER} inspect -f '{{.State.Pid}}' "$1")"
    echo "/sys/fs/cgroup$(sed -n 's/^0:://p' "/proc/${pid}/cgroup")"
}

run_subject() {
    ${DOCKER} run -d --pull never --name "${SUBJECT}" --network host \
        --memory="${MEMORY_LIMIT}" --memory-swap="${MEMORY_LIMIT}" \
        "${nursery_env[@]}" -e PYTHONUNBUFFERED=1 \
        -v "${OUT}/config:/config:ro" \
        "${IMAGE}" "$@" >/dev/null
}

run_peer() {
    ${DOCKER} run -d --pull never --name "${PEER}" --network host \
        --memory=4g --memory-swap=4g \
        -e PYPY_GC_NURSERY=4MB -e PYTHONUNBUFFERED=1 \
        -v "${OUT}/config:/config:ro" \
        "${IMAGE}" "$@" >/dev/null
}

if [ "${MODE}" = "fuzzingclient" ]; then
    run_peer python /config/echo_server.py "ws://127.0.0.1:${PORT}"
    wait_for_port "${PEER}"
    run_subject wstest --mode fuzzingclient --spec /config/fuzzingclient.json
    WATCHED="${SUBJECT}"
else
    # --webport 0: no web server for the reports, only the fuzzing server itself
    run_subject wstest --mode fuzzingserver --spec /config/fuzzingserver.json --webport 0
    wait_for_port "${SUBJECT}"
    run_peer wstest --mode testeeclient --wsuri "ws://127.0.0.1:${PORT}"
    WATCHED="${PEER}"
fi

# -- sample the memory until the run ends --------------------------------------

subject_cg="$(cgroup_dir "${SUBJECT}")"
peer_cg="$(cgroup_dir "${PEER}")"
if [ ! -r "${subject_cg}/memory.peak" ]; then
    echo "cannot read ${subject_cg}/memory.peak (cgroup v2 with memory.peak is required)" >&2
    exit 2
fi

running() {
    [ "$(${DOCKER} inspect -f '{{.State.Running}}' "$1" 2>/dev/null)" = "true" ]
}

echo "seconds,subject_bytes,subject_peak_bytes,peer_bytes" > "${OUT}/samples.csv"
start="$(date +%s)"
peak=0
peer_peak=0
timed_out=no
while running "${SUBJECT}" && running "${WATCHED}"; do
    now=$(( $(date +%s) - start ))
    cur="$(cat "${subject_cg}/memory.current" 2>/dev/null || echo '')"
    p="$(cat "${subject_cg}/memory.peak" 2>/dev/null || echo '')"
    peer_cur="$(cat "${peer_cg}/memory.current" 2>/dev/null || echo '')"
    pp="$(cat "${peer_cg}/memory.peak" 2>/dev/null || echo '')"
    if [ -n "${pp}" ] && [ "${pp}" -gt "${peer_peak}" ]; then
        peer_peak="${pp}"
    fi
    if [ -n "${p}" ] && [ "${p}" -gt "${peak}" ]; then
        peak="${p}"
    fi
    echo "${now},${cur},${p},${peer_cur}" >> "${OUT}/samples.csv"
    if [ "${now}" -ge "${TIMEOUT_S}" ]; then
        timed_out=yes
        break
    fi
    sleep 5
done
duration=$(( $(date +%s) - start ))

# -- the outcome ----------------------------------------------------------------

subject_running="$(${DOCKER} inspect -f '{{.State.Running}}' "${SUBJECT}")"
subject_oom="$(${DOCKER} inspect -f '{{.State.OOMKilled}}' "${SUBJECT}")"
subject_exit="$(${DOCKER} inspect -f '{{.State.ExitCode}}' "${SUBJECT}")"
peer_running="$(${DOCKER} inspect -f '{{.State.Running}}' "${PEER}")"
peer_exit="$(${DOCKER} inspect -f '{{.State.ExitCode}}' "${PEER}")"

${DOCKER} logs "${SUBJECT}" > "${OUT}/subject.log" 2>&1 || true
${DOCKER} logs "${PEER}" > "${OUT}/peer.log" 2>&1 || true
cases="$(grep -h -c 'Running test case' "${OUT}/subject.log" "${OUT}/peer.log" | sort -n | tail -1)"

# all cases ran: the fuzzingclient ended by itself, or the testeeclient did
# while the fuzzingserver kept running
completed=no
if [ "${timed_out}" = "no" ] && [ "${subject_oom}" = "false" ]; then
    if [ "${MODE}" = "fuzzingclient" ] && [ "${subject_running}" = "false" ] && [ "${subject_exit}" = "0" ]; then
        completed=yes
    fi
    if [ "${MODE}" = "fuzzingserver" ] && [ "${subject_running}" = "true" ] \
        && [ "${peer_running}" = "false" ] && [ "${peer_exit}" = "0" ]; then
        completed=yes
    fi
fi

peak_mib=$(( peak / 1048576 ))

verdict=FAILED
case "${EXPECT}" in
    pass)
        if [ "${completed}" = "yes" ] && [ "${peak_mib}" -le "${PEAK_LIMIT_MIB}" ]; then
            verdict=OK
        fi
        expected="all cases run, peak memory at most ${PEAK_LIMIT_MIB} MiB"
        ;;
    oom)
        if [ "${subject_oom}" = "true" ]; then
            verdict=OK
        fi
        expected="the ${MODE} is killed for exceeding its memory limit of ${MEMORY_LIMIT}"
        ;;
    report)
        verdict=OK
        expected="nothing (recorded for reference)"
        ;;
esac

{
    echo "### wstest ${MODE}, PYPY_GC_NURSERY=${NURSERY}: ${verdict}"
    echo ""
    echo "| | |"
    echo "|---|---|"
    echo "| expected | ${expected} |"
    echo "| peak memory of the ${MODE} | ${peak_mib} MiB (limit ${MEMORY_LIMIT}) |"
    echo "| killed for exceeding the limit (OOMKilled) | ${subject_oom} |"
    echo "| all cases ran | ${completed} |"
    echo "| test cases started | ${cases:-0} |"
    echo "| duration | ${duration} s$( [ "${timed_out}" = "yes" ] && echo ' (TIMED OUT)' ) |"
    echo "| ${MODE} container | running=${subject_running} exit=${subject_exit} |"
    echo "| peer container (not under test, PYPY_GC_NURSERY=4MB) | running=${peer_running} exit=${peer_exit}, peak memory $(( peer_peak / 1048576 )) MiB (limit 4g) |"
    echo ""
    echo '```'
    cat "${OUT}/environment.txt"
    echo '```'
} | tee "${OUT}/summary.md"

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    cat "${OUT}/summary.md" >> "${GITHUB_STEP_SUMMARY}"
fi

[ "${verdict}" = "OK" ]
