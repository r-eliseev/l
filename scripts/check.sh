#!/usr/bin/env bash
# Полная проверка харнеса: документация, задачи, навыки и опыт. Запускается в CI и перед завершением работы.
cd "$(dirname "$0")/.."
rc=0
bash scripts/check-docs.sh || rc=1
bash scripts/check-tasks.sh || rc=1
bash scripts/check-knowledge.sh || rc=1
if [ $rc -eq 0 ]; then echo "Харнес: все проверки пройдены"; fi
exit $rc
