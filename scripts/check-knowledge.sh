#!/usr/bin/env bash
# Проверка навыков (skills/) и записей опыта (docs/experience/). Код возврата 1, если есть ошибки.
# Проверяется формат, а не правдивость: доказательства и пользу оценивает ревью.
cd "$(dirname "$0")/.."
. scripts/tasks-lib.sh
fail=0
filled() { awk -v h="$2" '$0=="## " h {p=1; next} /^## /{p=0} p && NF {f=1} END{exit !f}' "$1"; }
# строка целиком из подсказки в угловых скобках (шаблон не заполнен)
has_placeholder() { grep -qE '^(# )?<[^>]*>[[:space:]]*$' "$1"; }

# 1. Навыки: skills/<имя>/SKILL.md с полями name (= имя каталога) и description
for d in skills/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  case "$name" in _*) continue ;; esac
  f="${d}SKILL.md"
  [ -f "$f" ] || { echo "ОШИБКА: в $d нет SKILL.md"; fail=1; continue; }
  case "$name" in *[!a-z0-9-]*) echo "ОШИБКА: имя навыка '$name': только a-z, 0-9 и дефис"; fail=1 ;; esac
  n=$(task_field "$f" name); desc=$(task_field "$f" description)
  [ "$n" = "$name" ] || { echo "ОШИБКА: $f: поле name ('$n') не совпадает с именем каталога '$name'"; fail=1; }
  if [ -z "$desc" ]; then echo "ОШИБКА: $f: нет поля description"; fail=1
  else case "$desc" in "<"*) echo "ОШИБКА: $f: description не заполнен"; fail=1 ;; esac; fi
  has_placeholder "$f" && { echo "ОШИБКА: $f: остались незаполненные подсказки в угловых скобках"; fail=1; }
done

# 2. Опыт: статус, дата, непустые «Ситуация» и «Доказательства», нет незаполненных подсказок
for f in docs/experience/*.md; do
  [ -e "$f" ] || continue
  case "$(basename "$f")" in _*) continue ;; esac
  grep -qE '^Статус: (действует|перенесено|устарело|опровергнуто)' "$f" \
    || { echo "ОШИБКА: у $f нет строки 'Статус:' с допустимым значением"; fail=1; }
  grep -qE '^Дата: [0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]]*$' "$f" \
    || { echo "ОШИБКА: у $f нет строки 'Дата: ГГГГ-ММ-ДД'"; fail=1; }
  for h in "Ситуация" "Доказательства"; do
    filled "$f" "$h" || { echo "ОШИБКА: $f: раздел '$h' пуст"; fail=1; }
  done
  has_placeholder "$f" && { echo "ОШИБКА: $f: остались незаполненные подсказки в угловых скобках"; fail=1; }
done

exit $fail
