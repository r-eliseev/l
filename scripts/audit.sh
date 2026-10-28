#!/usr/bin/env bash
# Сигналы устаревания (борьба с энтропией): то, что находится механически.
# Использование: scripts/audit.sh [дней-занятости] [дней-устаревания-доков] [дней-для-опыта]
#   дней-занятости: после скольких дней занятость задачи считается подозрительной (по умолчанию 7);
#   дней-устаревания-доков: насколько документ должен отстать от кода в books/*/src/, чтобы попасть в список (по умолчанию 30);
#   дней-для-опыта: записи опыта со статусом «действует» старше этого срока попадают в список (по умолчанию 90).
# Смысловую сверку документации с кодом выполняет агент по docs/audit.md.
# Код возврата 1 только если не пройдены проверки scripts/check.sh.
cd "$(dirname "$0")/.."
. scripts/tasks-lib.sh
claim_days="${1:-7}"; doc_days="${2:-30}"; exp_days="${3:-90}"
rc=0

echo "== 1. Проверки харнеса (scripts/check.sh)"
bash scripts/check.sh || rc=1

echo; echo "== 2. Задачи, занятые дольше $claim_days дн. (возможно, зависли)"
cutoff=$(date -u -d "$claim_days days ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
  || date -u -v-"${claim_days}"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)
if [ -n "$cutoff" ]; then
  found=0
  while IFS= read -r f; do
    as=$(task_field "$f" assignee); cl=$(task_field "$f" claimed)
    [ -n "$as" ] && [ -n "$cl" ] || continue
    if [[ "$cl" < "$cutoff" ]]; then echo "  $f: $as, занята с $cl"; found=1; fi
  done < <(find tasks -type f -name '[0-9][0-9]*-*.md' | sort)
  [ $found -eq 1 ] || echo "  нет"
else
  echo "  пропущено: не удалось вычислить дату (нужен GNU или BSD date)"
fi

echo; echo "== 3. Задачи, которые ждут человека (planned, blocked)"
waiting=$(bash scripts/list-tasks.sh planned; bash scripts/list-tasks.sh blocked)
if [ -n "$waiting" ]; then echo "$waiting" | sed 's/^/  /'; else echo "  нет"; fi

echo; echo "== 4. Документы, которые, возможно, устарели (отстали от кода в books/*/src/ на $doc_days дн. и больше)"
if git rev-parse --git-dir >/dev/null 2>&1; then
  code_t=$(git log -1 --format=%ct -- "books" 2>/dev/null)
  if [ -n "$code_t" ]; then
    found=0
    for f in docs/architecture.md docs/conventions.md docs/product.md docs/specs/*.md; do
      [ -e "$f" ] || continue
      case "$(basename "$f")" in _*) continue ;; esac
      doc_t=$(git log -1 --format=%ct -- "$f" 2>/dev/null)
      [ -n "$doc_t" ] || continue
      age=$(( (code_t - doc_t) / 86400 ))
      if [ "$age" -ge "$doc_days" ]; then echo "  $f: отстал от кода на $age дн."; found=1; fi
    done
    [ $found -eq 1 ] || echo "  нет"
  else
    echo "  нет истории коммитов для books/: пропущено"
  fi
else
  echo "  это не git-репозиторий: пропущено"
fi

echo; echo "== 5. ADR, которые ждут решения (статус «предложено»)"
found=0
for f in docs/decisions/*.md; do
  [ -e "$f" ] || continue
  case "$(basename "$f")" in _*) continue ;; esac
  if grep -q '^Статус: предложено' "$f"; then echo "  $f"; found=1; fi
done
[ $found -eq 1 ] || echo "  нет"

echo; echo "== 6. Записи опыта со статусом «действует» старше $exp_days дн. (проверьте, что условия не изменились)"
cutoff_d=$(date -u -d "$exp_days days ago" +%F 2>/dev/null || date -u -v-"${exp_days}"d +%F 2>/dev/null)
if [ -n "$cutoff_d" ]; then
  found=0
  for f in docs/experience/*.md; do
    [ -e "$f" ] || continue
    case "$(basename "$f")" in _*) continue ;; esac
    grep -q '^Статус: действует' "$f" || continue
    d=$(sed -n 's/^Дата: //p' "$f" | head -1)
    [ -n "$d" ] || continue
    if [[ "$d" < "$cutoff_d" ]]; then echo "  $f: от $d"; found=1; fi
  done
  [ $found -eq 1 ] || echo "  нет"
else
  echo "  пропущено: не удалось вычислить дату (нужен GNU или BSD date)"
fi

echo; echo "Смысловая сверка документации, навыков и опыта с кодом: docs/audit.md"
exit $rc
