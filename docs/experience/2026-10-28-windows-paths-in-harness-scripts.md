Статус: действует
Дата: 2026-10-28

# На Windows путь из mktemp не совпадает с тем, что понимает git

## Ситуация

Харнес (repo-harness) в Windows + Git Bash. Скрипты задач работают через
`task_on_main`: создаётся временный каталог, в нём `git worktree add`,
задача коммитится и пушится прямо в `origin/main`.

Работает в Linux и macOS. Ломается на Windows: `new-task.sh --publish`
заканчивается сообщением «Нет tasks/_template.md», хотя файл есть и в
локальном репозитории, и в `origin/main`.

## Что сработало или не сработало

Не сработало: `mktemp -d` в Git Bash возвращает путь вида `/tmp/tmp.XXXX`,
который bash понимает как `%TEMP%` (`C:\Users\<user>\AppData\Local\Temp`).
Нативный git этот же путь читает как `C:\tmp\tmp.XXXX` — то есть рабочий
каталог указывает на другую папку. `git worktree add` молча создаёт worktree
в `C:\tmp\tmp.XXXX\wt`, а скрипт ищет его в `%TEMP%\tmp.XXXX\wt` и не
находит: отсюда «Нет tasks/_template.md».

Не помогло: предположение, что дело в правах или в состоянии репозитория.
Диагностика через `git worktree list` показала расхождение путей, и только
после этого стало ясно, что причина в преобразовании пути.

Сработало: привести временный путь к виду `C:/...` через `cygpath -m` перед
передачей git. Такой путь понимают и bash, и нативный git. Добавлена функция
`t_path` в `scripts/tasks-lib.sh`; на системах без `cygpath` она ничего не
меняет, поэтому правка безопасна для Linux.

Правка внесена в два места: в установщик `repo-harness.sh` (чтобы
переустановка не вернула баг) и в уже сгенерированный `scripts/tasks-lib.sh`.

## Доказательства

- Симптом: `bash scripts/new-task.sh --publish backlog public-readme` →
  «Нет tasks/_template.md», при этом `git ls-tree origin/main tasks/` показывает
  `tasks/_template.md`.
- Диагностика: `git worktree list` после пробного `worktree add` показывал
  `C:/tmp/tmp.XXXX/wt`, тогда как `ls $TMP/wt/tasks/` не находил каталог.
- Проверка путей: `cygpath -m /tmp/tmp.XXXX` → `C:/Users/<user>/AppData/Local/Temp/tmp.XXXX`;
  `pwd -W` в том же каталоге даёт тот же результат.
- После правки: `new-task.sh --publish` создаёт задачу в `origin/main`,
  `list-tasks.sh --main` её видит, полный цикл claim → release отрабатывает
  без ошибок.

## Что делать в следующий раз

При отладке скриптов, которые смешивают bash и нативные программы (git,
python, node) в Windows, сначала проверить, одинаково ли обе стороны
понимают один и тот же путь: `cygpath -m "$TMP"` и `pwd -W` должны давать
одинаковый результат. Несовпадение — самая частая причина «файла нет» при
файле, который точно есть.
