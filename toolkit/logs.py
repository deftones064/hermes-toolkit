import re
from .config import LOG

def parse_recent_api_calls(limit=80):
    if not LOG.exists():
        return []

    lines = LOG.read_text(errors="ignore").splitlines()[-2000:]
    calls = []

    pat = re.compile(
        r"API call #(?P<num>\d+): model=(?P<model>\S+) provider=(?P<provider>\S+) "
        r"in=(?P<in>\d+) out=(?P<out>\d+) total=(?P<total>\d+).*?cache=(?P<cache>\d+)/(?P<cache_total>\d+) \((?P<pct>\d+)%\)"
    )

    for line in lines:
        m = pat.search(line)
        if m:
            d = m.groupdict()
            for k in ["num", "in", "out", "total", "cache", "cache_total", "pct"]:
                d[k] = int(d[k])
            calls.append(d)

    return calls[-limit:]

def print_logs():
    calls = parse_recent_api_calls(20)
    if not calls:
        print("No recent API calls found.")
        return

    for c in calls:
        print(
            f"#{c['num']:>2} {c['provider']}/{c['model']} "
            f"in={c['in']:,} out={c['out']:,} total={c['total']:,} cache={c['pct']}%"
        )
