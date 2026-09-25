# EE1102 DMOJ (Python session)

Self-hosted DMOJ on this laptop. Everything (site, DB, judges) runs locally in Docker; students reach it via a Cloudflare tunnel later.

- Site: http://localhost:8080 · Admin: `/admin/` · **TA dashboard: `/ta/`**
- Admin login: `admin` / password in `ADMIN_CREDENTIALS.txt`
- Test contest `test` with problem `aplusb` (2 visible samples + 3 hidden cases). Test accounts `teststudent1`, `teststudent2` (password `Qm7-vTr9-xKc2-EE1102`) — delete them in admin before the real session (they count in stats).

## Commands (`./ee1102.sh ...`)
| cmd | what |
|---|---|
| `up` / `down` / `restart` | start / stop / restart services |
| `status` | containers + judge online state |
| `logs [service]` | follow logs (e.g. `logs judge1`) |
| `export <contest>` | write stats xlsx to `dmoj-docker/dmoj/repo/exports/` |
| `backup` | DB dump + problem data to `backups/` |
| `manage <args>` | Django `manage.py` |

## What students can / can't see
- Only Python 3. Only their own submissions, source and score. Contest scoreboard shows only their own row.
- Per-test-case verdicts (AC/WA/TLE/…) and `passed/total`, never hidden test data.
- Blocked for non-staff: `/users/` (global leaderboard), other users' profiles, `/api/`, `/stats/`, contest stats, `/ta/`.
- No self-signup (accounts created by TA). No forced password change on login (DMOJ's breached-password check disabled).

## Adding a problem
1. Admin → Problems → Add. Code (e.g. `p1`), name, statement (Markdown; put visible examples as `## Sample Input 1` / `## Sample Output 1` blocks; math is `~x^2~` inline and `$$...$$` display — **not** `$x$`), group `ee1102`, time limit, memory limit (KB, e.g. 262144), points, **Allows partial points** ✔, allowed languages **Python 3**, **not** publicly visible.
2. Open `/problem/<code>/test_data`: upload a zip of `1.in, 1.out, 2.in, ...`, set each case **points = 1** (so score = tests passed), save. Include the visible samples as the first cases.
3. Add it to the contest (Admin → Contests → problems inline).
4. Optional **Starter code**: on the problem's admin page, fill the *Starter code* box at the bottom. Students' editor starts with it (their own saved draft takes priority) and gets a *Reset to starter code* button.

## Creating the real contest
Admin → Contests → Add: key, name, start/end (wide window, no per-user time limit), **Scoreboard visibility = Hidden permanently**, publicly visible ✔, not rated, format `default`, add problems (points, partial ✔). Students must click **Join** on the contest page. The contest page lists problems (name + points only, no AC rate/solve counts) once the contest starts; links open after joining. Also reachable via **Problems** in the top menu.

## Stats
- Live: `/ta/` (auto-refresh 10 s): joined/active counts, per-problem AC rate + verdicts, student × problem matrix (filter "not solved X", "not yet submitted"), latest submissions, judge status.
- Built-in: contest ranking (full, for admin), `/contest/<key>/stats`, `/submissions/`.
- After: **Export stats (.xlsx)** button on `/ta/` or `./ee1102.sh export <key>`. Sheets: Summary, Students (score/tests/attempts/solve-time per problem), Problems, Test cases (pass rate per case — spots tricky hidden cases), Submissions (all, with source).

## Cloudflare tunnel
Install: `curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cf.deb && sudo dpkg -i /tmp/cf.deb`

**Quick (no account):** `cloudflared tunnel --url http://localhost:8080` → prints `https://<random>.trycloudflare.com`. Must add its URL to `CSRF_TRUSTED_ORIGINS` first. URL changes every time cloudflared restarts.

**Named (stable URL, needs a domain on Cloudflare):**
```
cloudflared tunnel login
cloudflared tunnel create ee1102
cloudflared tunnel route dns ee1102 ee1102.karthikkashyap.com
```
`~/.cloudflared/config.yml`:
```
tunnel: ee1102
credentials-file: /home/kashyap/.cloudflared/<TUNNEL-UUID>.json
ingress:
  - hostname: ee1102.karthikkashyap.com
    service: http://localhost:8080
  - service: http_status:404
```
Run: `cloudflared tunnel run ee1102`. `https://ee1102.karthikkashyap.com` is already in `CSRF_TRUSTED_ORIGINS`.

Websockets + https detection work behind the tunnel. Keep the laptop plugged in with sleep disabled.

## Student accounts (later)
Pending roster CSV — bulk-create script to be added.

## Notes / layout
- `dmoj-docker/dmoj/` — compose setup. Secrets in `environment/*.env`. DB data in `database/`, problem data in `problems/`.
- `dmoj-docker/dmoj/repo/ee1102/` — custom app: dashboard, export, access-restriction middleware, bootstrap command.
- 2 judges (`judge1`, `judge2`), Python 3 only. Per-user queue limit: 2 pending submissions.
- `judge-image/` — builds the `dmoj/judge-tier1` image (no longer on Docker Hub), pinned to a tested judge-server commit.
- Site image uses Python 3.12 (upstream 3.14 breaks Django 4.2 admin).

## Fresh install (from this repo)
Needs Docker + Compose.
```
cd dmoj-docker/dmoj
for f in environment/*.env.example; do cp -n "$f" "${f%.example}"; done
# Fill secrets: random values for MYSQL_PASSWORD, MYSQL_ROOT_PASSWORD, SECRET_KEY, JUDGE_KEY, e.g.
python3 -c "import secrets; print(secrets.token_urlsafe(40))"
mkdir -p problems media
docker build -t dmoj/judge-tier1 ../../judge-image
docker compose build
docker compose up -d db redis site
./scripts/migrate && ./scripts/copy_static
docker compose exec site python3 manage.py ee1102_bootstrap
docker compose exec site python3 manage.py createsuperuser --username admin
cd ../.. && ./ee1102.sh up
```

## Restore from backup
```
cd dmoj-docker/dmoj
gunzip -c ../../backups/dmoj-<stamp>.sql.gz | docker compose exec -T db sh -c 'mariadb -uroot -p"$MYSQL_ROOT_PASSWORD" dmoj'
sudo tar xzf ../../backups/dmoj-<stamp>-problems.tgz    # restores problems/
```
Backups contain student data and hidden tests: keep them out of git (already ignored).
