#!/bin/bash
# Helper for the EE1102 DMOJ setup. Run from anywhere: ./ee1102.sh <command>
set -e
cd "$(dirname "$(readlink -f "$0")")/dmoj-docker/dmoj"
manage() { docker compose exec -T site python3 manage.py "$@"; }

case "$1" in
  up)       docker compose up -d && docker compose restart nginx >/dev/null && echo "Up: http://localhost:${DMOJ_PORT:-8080}  (TA dashboard: /ta/)" ;;
  down)     docker compose down ;;
  restart)  docker compose up -d --force-recreate site celery bridged wsevent && docker compose restart nginx ;;  # recreate so env changes apply
  status)   docker compose ps --format 'table {{.Service}}\t{{.Status}}'
            manage shell -c "from judge.models import Judge; [print(f'{j.name}: {\"online\" if j.online else \"OFFLINE\"}') for j in Judge.objects.all()]" 2>/dev/null ;;
  logs)     docker compose logs -f --tail 100 "${@:2}" ;;
  export)   [ -n "$2" ] || { echo "usage: $0 export <contest_key>"; exit 1; }; manage ee1102_export "$2" ;;
  backup)   mkdir -p ../../backups; f=../../backups/dmoj-$(date +%Y%m%d-%H%M).sql.gz
            docker compose exec -T db sh -c 'mariadb-dump -uroot -p"$MYSQL_ROOT_PASSWORD" dmoj' | gzip > "$f"
            tar czf "${f%.sql.gz}-problems.tgz" problems; echo "Backup: $f (+ problems tgz)" ;;
  manage)   manage "${@:2}" ;;
  bootstrap) manage ee1102_bootstrap ;;
  *) echo "usage: $0 {up|down|restart|status|logs [service]|export <contest>|backup|bootstrap|manage <args>}"; exit 1 ;;
esac
