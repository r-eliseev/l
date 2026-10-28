#!/usr/bin/env bash
# Список навыков: имя и описание. Полный текст навыка лежит в skills/<имя>/SKILL.md.
# Использование: scripts/list-skills.sh
cd "$(dirname "$0")/.."
. scripts/tasks-lib.sh
found=0
for f in skills/*/SKILL.md; do
  [ -e "$f" ] || continue
  d=$(basename "$(dirname "$f")")
  case "$d" in _*) continue ;; esac
  printf '%s — %s\n' "$d" "$(task_field "$f" description)"
  found=1
done
[ $found -eq 1 ] || echo "Навыков пока нет."
