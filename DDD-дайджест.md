# Domain-Driven Design: рабочий дайджест

Документ собран по открытым первоисточникам (см. раздел «Источники» в конце). Каждое утверждение снабжено номером источника; ниже по тексту — дословные цитаты, чтобы можно было проверить формулировки.

---

## 1. Что это такое и откуда взялось

Domain-Driven Design (DDD) — подход к разработке сложного ПО, в котором структура и язык кода совпадают с предметной областью, а ядро системы моделируется вместе с экспертами этой области.[16] Термин ввёл Эрик Эванс в книге 2003 года; канонический «синий» тред — *Domain-Driven Design: Tackling Complexity in the Heart of Software*.[16][2]

Эванс формулирует DDD в три пункта: сфокусироваться на core domain; исследовать модели в творческом сотрудничестве с практиками домена и разработчиками; говорить на ubiquitous language в явно ограниченном контексте.[1] Это не набор техник, а способ выстраивать разработку вокруг понимания предметной области.[21]

Ключевая мысль Эванса: DDD — это принцип «сосредоточьте лучшую часть своего ума на глубоких проблемах домена, в который вовлечены ваши пользователи, и сотрудничайте с экспертами этого домена, чтобы привести его к концептуальной форме, пригодной для создания мощного и гибкого ПО».[21] Он же отмечал, что подход особенно уместен там, где домен сложен и запутан, и предупреждал, что технологию следует оценивать по тому, помогает ли она команде заниматься доменом, а не отвлекает от него.[21]

Microsoft в Azure Architecture Center формулирует применение DDD к микросервисам как четыре шага: (1) проанализировать бизнес-домен и получить неформальное его описание; (2) определить bounded contexts домена; (3) применить тактические паттерны DDD внутри каждого контекста — сущности, агрегаты, доменные сервисы; (4) по результатам предыдущего шага выделить микросервисы.[7] Microsoft рекомендует DDD только для сложных доменов, где модель даёт явную пользу в формировании общего понимания предметной области.[16]

---

## 2. Стратегический дизайн

### 2.1 Ubiquitous Language (единый язык)

Единый язык — это язык, структурированный вокруг доменной модели и используемый всеми участниками команды внутри одного bounded context, чтобы связать всю работу команды с ПО.[1] Фowler определяет его как практику выработки общего строгого языка между разработчиками и пользователями, основанного на доменной модели, и подчёркивает: Evans настаивает, что язык должен использоваться в разговорах с экспертами домена (это и есть способ проверки модели) и что язык вместе с моделью должен меняться по мере роста понимания домена командой.[5]

Ключевое правило: изменение языка означает изменение модели.[1] То есть переименование класса, метода или модуля — не косметика, а пересмотр модели, и рефакторинг кода под новое имя обязателен.[1] Практический совет оттуда же: описывать сценарии вслух элементами модели, находить более простые способы сказать то, что нужно, и возвращать новые формулировки в диаграммы и код.[1]

### 2.2 Bounded Context (ограниченный контекст)

Bounded context — описание границы (как правило, подсистемы или работы конкретной команды), внутри которой определена и применима некоторая модель.[1] У Fowler это центральный паттерн DDD: DDD делит большие модели на разные bounded contexts и явно обозначает их взаимосвязи, потому что единая модель большой системы «не будет ни выполнимой, ни рентабельной».[4]

Несколько моделей в проекте неизбежны: разные подсистемы обслуживают разные сообщества пользователей, независимые команды решают одну задачу по-разному из-за отсутствия коммуникации, а инструменты могут различаться, из-за чего код нельзя разделить.[1] Поэтому границы фиксируются явно — в терминах организации команды, использования внутри отдельных частей приложения и физических артефактов: кодовых баз и схем БД.[1]

Один и тот же термин может означать разное в разных контекстах: слово *account* в каждом bounded context имеет своё значение, и это нормально, пока единый язык используется последовательно.[7] Отсюда же следует практическое правило границ сервисов: микросервис не должен быть меньше агрегата и не больше bounded context.[8]

### 2.3 Поддомены и приоритизация

DDD делит поддомены на три категории, и классификация помогает решить, куда вкладывать больше всего усилий в проектирование.[7]

| Категория | Что это | Что с этим делать |
|---|---|---|
| **Core subdomain** | Даёт конкурентное преимущество, определяет сам бизнес | Детальное моделирование, существенные вложения в команду |
| **Supporting subdomain** | Поддерживает работу бизнеса, но не отличает от конкурентов | Нужна своя разработка, но это не источник преимущества |
| **Generic subdomain** | Проблема, уже решённая в отрасли | Взять готовое решение / стандартный продукт |

Формулировки в таблице — близкие к тексту Microsoft: core даёт конкурентное преимущество и требует детального моделирования; supporting поддерживает бизнес, но не дифференцирует; generic — это то, что отрасль уже решила, и это можно закрыть готовым решением.[7] В примере Microsoft (доставка грузов дронами) в core попали shipping и управление дронами, в supporting — выставление счетов, в generic — учётные записи пользователей и колл-центр.[7]

Признаки, по которым ищут отдельные поддомены на старте анализа: тесно связанные функции; функции, ключевые для бизнеса, против supporting; граф зависимостей между функциями.[7] Технологии и детали реализации на этом этапе обсуждать не нужно, но места интеграции с внешними системами (CRM, платежи, биллинг) определить стоит.[7]

### 2.4 Context Map и отношения между контекстами

Context Map описывает контакты между bounded contexts и командами с помощью набора паттернов.[13] По подсчёту сообщества ddd-crew, в литературе по DDD обычно описывают девять паттернов context map и три типа отношений между командами.[13]

Три типа отношений команд:[13]

- **Mutually Dependent** — команды или контексты взаимозависимы: их артефакты поставляются вместе, есть взаимная связь по данным и функциональности, нужно много коммуникации (это случай паттерна Partnership).[26]
- **Upstream / Downstream** — действия upstream влияют на downstream, но не наоборот: «upstream-команда может преуспеть независимо от судьбы downstream-команды».[26]
- **Free** — контекст свободен: изменения в других контекстах никак не влияют на его успех, между ними нет ни организационной, ни технической связи.[26]

Девять паттернов context map (по ddd-crew, с определениями из DDD Reference Evans):[13][26]

- **Open-host Service** — протокол, дающий доступ к вашей подсистеме как к набору сервисов; протокол открыт для всех интеграторов и расширяется под новые требования, кроме случаев с уникальными потребностями одного потребителя (для них — одноразовый транслятор).[26]
- **Shared Kernel** — явно очерченное подмножество доменной модели, на которое команды договариваются; ядро должно быть небольшим, и то, что в него входит, не меняется без консультации с другой командой.[26]
- **Customer / Supplier Development** — явные отношения «заказчик — поставщик»: приоритеты downstream учитываются в планировании upstream, задачи под требования downstream согласуются и бюджетируются, чтобы обязательства и сроки были понятны обеим сторонам.[26]
- **Conformist** — «eliminate the complexity of translation between bounded contexts by slavishly adhering to the model of the upstream team»: упрощение интеграции ценой ограничения downstream-дизайнеров и отказа от идеальной модели приложения.[26]
- **Anti-Corruption Layer** — изолирующий слой на стороне downstream, дающий вашей системе функциональность upstream в терминах вашей доменной модели; слой общается с другой системой через её существующий интерфейс, не требуя правок, и переводит между моделями в одну или обе стороны.[26] В Azure это описано как «фасад или адаптерный слой между подсистемами, не имеющими общей семантики», переводящий запросы одной подсистемы в другую, чтобы зависимости от внешних подсистем не ограничивали дизайн приложения; паттерн впервые описал Эванс в *Domain-Driven Design*.[10]
- **Published Language** — хорошо документированный общий язык, способный выразить необходимую доменную информацию и служащий общей средой общения, с переводом в него и из него; типичные примеры — iCalendar и vCard.[26]
- **Separate Ways** — контекст объявляется не связанным с остальными, и разработчики находят простые специализированные решения внутри этого узкого scope.[26]
- **Partnership** — когда провал разработки в одном из двух контекстов означает провал поставки для обоих, команды заключают партнёрство с координированным планированием и совместным управлением интеграцией; взаимозависимые фичи планируются под один релиз.[26]
- **Big Ball of Mud** — часть системы, которая является mess из-за смешанных моделей и непоследовательных границ; это маркер плохой модели, который не должен распространяться на другие bounded contexts.[26]

Практика ddd-crew: не нужно помещать все паттерны и отношения в одну большую карту — она разрастётся и станет непонятной, поэтому рекомендуются небольшие context map под конкретный вопрос, документирование выбранных паттернов и работа с несколькими перспективами.[26]

### 2.5 Инструменты стратегического моделирования

**ContextMapper** — open source-проект, дающий доменный язык и инструменты для стратегического DDD: context mapping, моделирование bounded contexts и декомпозиция на сервисы.[11][12]

- Язык CML (Xtext-based DSL) поддерживает моделирование bounded contexts и связей между ними.[11]
- Есть плагин для Eclipse, расширение для VS Code и standalone-версия на Java.[12]
- Отдельная ценность проекта — Service Cutter, который предлагает декомпозицию на сервисы на основе context map.[12]

**Event Storming** — метод, предложенный Альберто Брандолини: собрать в одной комнате экспертов домена и разработчиков, дать им бумажный рулон, много цветных стикеров и фасилитатора — и за часы получить лучшую модель, которую вообще возможно получить.[24] Это воркшоп-метод, а не инструмент: участники расставляют доменные события как стикеры на временной шкали.[24]

Три распространённых уровня Event Storming:[18]

- **Big Picture** — совместное исследование сложного бизнес-домена; полезно, когда scope велик или неясен.[18]
- **Process Modeling** — детальная проработка конкретного бизнес-процесса от начала до конца; полезно, когда старт и цель процесса известны.[18]
- **Software Design** — развитие Process Modeling: добавляется архитектура системы, включая агрегаты, команды и bounded contexts.[18]

Цель Big Picture — максимизировать обучение через совместное исследование домена, создать общее понимание между отделами и договориться о критичных задачах; противоречия при этом визуализируются автоматически.[18]

**Domain Storytelling** — визуальный совместный метод (книга Stefan Hofer и Henning Schwentner, Addison-Wesley, 2021): истории предметной области как альтернатива формальным моделям, с упором на совместную работу.[25]

---

## 3. Тактический дизайн

### 3.1 Entity (сущность)

Сущность — объект, чья идентичность сохраняется во времени; два экземпляра с одинаковым идентификатором представляют один и тот же доменный концепт, даже если их атрибуты различаются (имя или адрес человека могут измениться — это всё равно тот же человек); наоборот, два объекта с одинаковыми атрибутами, но разными идентификаторами — разные сущности.[8]

Ключевое: идентичность выбирается осознанно.[8] Натуральные ключи (номер заказа, выданный государством ID) несут бизнес-смысл и узнаваемы в разных системах; суррогатные (GUID) не несут смысла, но не связывают модель с внешними системами.[8] В микросервисной архитектуре другие сервисы ссылаются на сущности по идентификаторам, поэтому идентичность должна оставаться стабильной и осмысленной на границах сервисов.[8]

Evans: идентичность, а не атрибуты, должна быть первична в определении модели; класс должен оставаться простым и сфокусированным на непрерывности жизненного цикла и идентичности; модель обязана определить, что значит «это одна и та же вещь».[1] В DDD Reference у паттерна есть синоним — Reference Objects.[1]

### 3.2 Value Object (объект-значение)

Объект-значение не имеет идентичности и определяется только значениями своих атрибутов; два объекта-значения с одинаковыми атрибутами взаимозаменяемы.[8] Типичные примеры: цвета, даты и время, денежные суммы, измерения.[8]

Evans: «if you care only about the attributes and logic of an element of the model, classify it as a value object»; объект-значение следует считать неизменяемым, все операции — свободными от побочных эффектов и не зависящими от изменяемого состояния, идентичность ему давать не нужно.[1] Azure добавляет: value objects предпочтительнее как выбор по умолчанию — концепцию повышают до сущности только тогда, когда за ней действительно стоит идентичность; неизменяемость позволяет безопасно делить объекты между потоками, кэшировать их без defensive copy и проще рассуждать в распределённых системах.[8]

### 3.3 Aggregate (агрегат)

Агрегат — кластер сущностей и объектов-значений с оговорёнными границами: выбирается одна сущность как корень агрегата, а внешние объекты могут ссылаться только на корень (ссылки на внутренние элементы допустимы лишь для использования внутри одной операции).[1] Границы агрегата задают правила согласованности и одновременно управляют транзакциями и распределением: внутри границы правила применяются синхронно, между границами — асинхронно; агрегат держится на одном сервере, разные агрегаты могут быть разнесены по узлам.[1]

Если границы агрегатов проведены плохо, это сигнал пересмотреть модель: сценарий домена может намекать на новый важный инсайт, и такое изменение обычно улучшает выразительность и гибкость модели, попутно решая транзакционные и распределённые проблемы.[1]

### 3.4 Repository (репозиторий)

Репозиторий даёт доступ к агрегатам на языке ubiquitous language: для каждого типа агрегата, требующего глобального доступа, создаётся сервис, дающий иллюзию коллекции всех объектов данного типа в памяти, с известным глобальным интерфейсом, методами добавления/удаления и методами выборки по критериям, понятным экспертам домена; возвращаются полностью сконструированные объекты либо прокси, скрывающие технологию хранения.[1]

Причина существования паттерна — вред от наивных запросов: техническая сложность доступа к данным забивает клиентский код, из-за чего разработчики упрощают доменный слой до нерелевантного, а доменная логика уезжает в запросы и код приложения, и сущности превращаются в контейнеры данных.[1]

### 3.5 Domain Event (доменное событие)

Доменное событие — «something happened that domain experts care about»: нечто, о чём эксперты домена хотят знать.[1] Событие — полноценная часть доменной модели, представление того, что произошло в домене; обычно оно неизменяемо, как запись о прошлом, и содержит отметку времени, а часто — и отдельную отметку времени ввода в систему, и идентификатор внесшего.[1] В распределённой системе состояние сущности можно вывести из известных узлу доменных событий, что позволяет держать связную модель при неполной информации о системе в целом.[1]

### 3.6 Domain Service (доменный сервис)

Когда значимый процесс или преобразование в домене не является естественной обязанностью сущности или объекта-значения, добавляется операция в виде отдельного интерфейса-сервиса: определяется контракт сервиса — набор утверждений о взаимодействии, сформулированных на ubiquitous language конкретного bounded context; имя сервиса само становится частью ubiquitous language.[1] Мотив: натянуть такой процесс на сущность значит исказить её определение или добавить бессмысленные искусственные объекты.[1]

### 3.7 Прочие паттерны и архитектура

В DDD Reference перечислены также Layered Architecture (изоляция доменной модели и бизнес-логики от UI, приложения и инфраструктуры), Modules (модули как часть модели, с именами из ubiquitous language), Factories, Specification, а в стратегической части — Core Domain, Generic Subdomains, Domain Vision Statement, Highlighted Core, Evolving Order, System Metaphor, Responsibility Layers, Knowledge Level, Pluggable Component Framework.[1]

Отдельно отмечается связь с Hexagonal Architecture: Evans пишет, что «related patterns, such as "Hexagonal Architecture" may serve as well or better» для изоляции выражений доменной модели от зависимостей на другие системные concerns.[1] Сам Cockburn определяет гексагональную архитектуру как способ «позволить приложению одинаково управляться пользователями, программами, автоматизированными тестами или пакетными скриптами, и разрабатываться и тестироваться изолированно от его конечных устройств и баз данных исполнения».[23]

Fowler добавляет контринтутивный совет: почти все успешные истории микросервисов начинались с монолита, который вырос слишком большим, а системы, построенные как микросервисы с нуля, по его наблюдениям, заканчивались серьёзными проблемами — отсюда рекомендация не начинать новый проект с микросервисов, даже если вы уверены, что приложение вырастет достаточно большим, чтобы это окупилось.[6]

По той же причине Microsoft советует определять размер микросервиса от доменной модели, а не наоборот: если начать с хорошо спроектированной доменной модели, правильный размер и область каждого микросервиса определить заметно проще.[9]

---

## 4. Ловушки и антипаттерны

**Anemic Domain Model** — антипаттерн, при котором объекты выглядят как настоящая доменная модель (много объектов, названных по существительным домена, с богатыми связями), но поведения на них почти нет: это по сути мешки с геттерами и сеттерами, а вся доменная логика вынесена в сервис-объекты, которые используют модель как данные.[3] По словам Fowler, фундаментальный ужас этого антипаттерна в том, что он противоречит базовой идее объектно-ориентированного проектирования — объединять данные и поведение, — и по сути является процедурным стилем проектирования.[3] Он же отмечает, что ассоциировать DDD с этим антипаттерном — плохо: Evans и сам Fowler оба замечали, что анемичные модели как раз набирают популярность.[3]

Azure формулирует это же как практическое правило: сущности должны инкапсулировать поведение, а не только хранить данные; когда бизнес-логика живёт вне сущности в сервис-классах, получается anemic domain model, который подрывает саму пользу DDD.[8] Пример: логика отмены доставки должна лежать в сущности `Delivery`, а не в отдельном внешнем сервисе.[8]

**«DDD в ничто не превращается»** — типичная ошибка восприятия: помнят несколько тактических паттернов (Aggregate, Repository, Value Object), тогда как стратегический дизайн — Bounded Context, Context Mapping, Ubiquitous Language — занимает больше половины книги и обычно игнорируется.[19] Следствие — ломается простой CRUD на сложные агрегаты и объекты-значения, а затем пишутся тысячи строк бессмысленного DTO-кода ради слоёной архитектуры, и работа идёт «на скорости сопровождения архитектуры», а не бизнеса.[19] Ответ сторонников DDD: это не DDD, а cargo cult — применять DDD везде не значит применять DDD; для простых доменов community рекомендует Transaction Script, а Evans сам больше рекомендовал Hexagonal Architecture, чем слоистую архитектуру.[19]

---

## 5. Критика и границы применимости

**Скептическая позиция.** Тони Марстон в статье «Why I don't do Domain Driven Design» (2018, обновлено 2024) перечисляет «DDD advice», которое он сознательно игнорирует: ассоциации, агрегаты, композиции и другие предписания — в пользу собственного подхода с отдельным классом на таблицу, подсистемами и отдельными контроллерами на каждый use case.[20]

**Структурный аргумент скептика** в «DDD Debate»: если из 10 команд DDD проваливается 9, это свидетельство того, что методология оторвана от реальности, а не о некомпетентности разработчиков; «3 000-строчный монстр» хотя бы позволяет что-то найти, тогда как система, разбитая по DDD, требует навигации по десяткам файлов, чтобы понять одну единицу логики, и это не снятие сложности, а её распределение; а стратегический дизайн — это «политика», а не «технология»: сколько организаций реально выделят время, чтобы эксперты домена согласовали терминологию с разработчиками, и если нет — контексты поделят по воображению, и позже получится ещё большая катастрофа распределённых транзакций.[19]

Ответ сторонника: критика «No True Scotsman» частично обоснована — сообщество DDD уклоняется от разбора провальных кейсов фразой «это был не настоящий DDD», и крутая кривая обучения действительно реальна; но по той же логике Git, Kubernetes и функциональное программирование тоже «недостаточны», и ценность инструмента определяется не простотой, а соотношением пользы и цены освоения; для систем со сложной бизнес-логикой как конкурентным преимуществом (финансы, логистика, бронирование) DDD окупает кривую обучения многократно; «3 000 строк против 300 файлов» — ложная дилемма, поскольку границы агрегатов изолируют сложность, а не распределяют её; и «стратегический дизайн — это политика» — «именно так, и в этом суть»: главный урок DDD в том, что то, что выглядит технической проблемой, на самом деле организационная или коммуникационная.[19]

Ключевая развилка в ответе сторонника — различение существенной (essential) и случайной (accidental) сложности по Бруксу: 3 000-строчный сервис прячет существенную сложность, DDD делает её явной, а границы агрегатов, доменные события и объекты-значения работают как указатели «бизнес-правила живут здесь».[19]

**Практический вывод.** DDD уместен там, где сложность домена — конкурентное преимущество, и неуместен для простого CRUD; Microsoft прямо ограничивает рекомендацию сложными доменами.[16] Формальный критерий из ответа сторонника: DDD применяют выборочно к core domain, где сложность ожидаема, а не ко всей системе.[19]

---

## 6. С чего начинать практически

1. **Определить домен и core subdomain.** Классифицировать функциональность на core / supporting / generic и решить, где модель даёт преимущество.[7]
2. **Разделить домен на bounded contexts.** Фиксировать границы в терминах команд, частей приложения, кодовых баз и схем БД; в каждом контексте — своя модель и свой ubiquitous language.[1][4]
3. **Нарисовать context map.** Определить отношения между контекстами (mutually dependent / upstream-downstream / free) и выбрать паттерны связи: Shared Kernel, Conformist, Anti-Corruption Layer, Partnership и т.д.[13] Инструмент — ContextMapper с его CML-DSL.[11][12]
4. **Собрать Event Storming.** Big Picture для выравнивания понимания домена, затем Process Modeling для конкретных процессов, затем Software Design для архитектуры и агрегатов.[18][24]
5. **Смоделировать тактически.** Value object по умолчанию, сущности — когда нужна идентичность; агрегаты с корнем и границами согласованности; репозитории на доменном языке; доменные события для фиксации значимого.[1][8]
6. **Держать язык в коде.** Переименование = изменение модели, а не косметика.[1] Проверка: не осталось ли в проекте «anemic» слоя, вынесенного в сервисы.[3][8]

Полезные артефакты на каждом шаге: starter-kit моделирования от ddd-crew с кейсами и переводами, шпаргалка context map с набором для Miro, и подборки бесплатных материалов для обучения — всё это лежит в open-source репозиториях ddd-crew.[14][15][13]

---

## 7. Что почитать

- **Eric Evans, *Domain-Driven Design* (2003)** — «большая синяя книга», первоисточник; на официальном сайте есть бесплатный *Domain-Driven Design Reference* (2015) с определениями и краткими формулировками паттернов, распространяемый по CC-BY.[2][1]
- **Eric Evans & Vaughn Vernon, *Domain-Driven Design Distilled*** — краткая версия, акцент на стратегическом дизайне; на странице проекта — заметки о bounded context и ubiquitous language, problem space против solution space, и о том, что ключевая стратегическая инициатива становится core domain.[22]
- **Eric Evans & Vaughn Vernon, *Domain-Driven Design Reference* (2015)** — компактный справочник: определения domain / model / ubiquitous language / context / bounded context и pattern language из 30+ паттернов; книга сама признаёт, что краткие формулировки паттернов рождались из воркшопов ещё до выхода «синей книги» и были выложены в Creative Commons по инициативе Ward Cunningham.[1]
- **Vaughn Vernon, *Implementing Domain-Driven Design*** — «большая красная книга», практическая реализация; Evans в предисловии к Reference называет её самой амбициозной книгой после собственной.[1]
- **Jimmy Nilsson, *Applying Domain-Driven Design and Patterns*** — первая книга после Evans; в предисловии Evans отмечает: с одной книгой у тебя книга, с двумя — у тебя тема.[1]
- **Alberto Brandolini, *Domain-Driven Design Quickly* (InfoQ)** — бесплатная мини-книга + интервью Evans «почему DDD важен сегодня».[21]
- **Stefan Hofer & Henning Schwentner, *Domain Storytelling* (2021)** — визуальный совместный метод моделирования.[25]
- **Vlad Khononov, *Learning Domain-Driven Design*** — упоминается Azure как современный практический справочник по тактическим паттернам.[8]

## 8. Инструменты и ресурсы

- **ContextMapper** — DSL и инструменты для стратегического DDD; Eclipse-плагин, расширение VS Code, standalone-Java.[11][12]
- **ddd-crew/free-ddd-learning-resources** — подборка бесплатных статей, видео и материалов по DDD: вводные, совместное моделирование, стратегический дизайн, тактический DDD, кейсы, блоги.[14]
- **ddd-crew/ddd-starter-modelling-process** — пошаговый процесс моделирования со стартовым набором, кейсами и переводами.[15]
- **ddd-crew/context-mapping** — шпаргалка по девяти паттернам context map и набор для Miro, с цитатами из DDD Reference.[13]

---

## Источники

## Sources

[1] https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf — Eric Evans — Domain-Driven Design Reference (2015, PDF)
    > "ubiquitous language A language structured around the domain model and used by all team members within a bounded context to connect all the activities of the team with the software."
    > "bounded context A description of a boundary (typically a subsystem, or the work of a particular team) within which a particular model is defined and applicable."
    > "Domain-Driven Design is an approach to the development of complex software in which we: 1. Focus on the core domain. 2. Explore models in a creative collaboration of domain practitioners and software practitioners. 3. Speak a ubiquitous language within an explicitly bounded context."
    > "When you care only about the attributes and logic of an element of the model, classify it as a value object."
    > "Treat the value object as immutable."
    > "Cluster the entities and value objects into aggregates and define boundaries around each."
    > "Choose one entity to be the root of each aggregate, and allow external objects to hold references to the root only"
    > "Within an aggregate boundary, apply consistency rules synchronously. Across boundaries, handle updates asynchronously."
    > "Recognize that a change in the language is a change to the model."
    > "Model information about activity in the domain as a series of discrete events."
    > "For each type of aggregate that needs global access, create a service that can provide the illusion of an in-memory collection of all objects of that aggregate's root type."
[2] https://www.domainlanguage.com/ddd — Domain Language — DDD resources
    > "This reference guide provides a quick and authoritative summary of the key concepts of Domain-Driven Design. It is not meant as a learning introduction to the subject."
[3] https://martinfowler.com/bliki/AnemicDomainModel.html — Martin Fowler — Anemic Domain Model
    > "The basic symptom of an Anemic Domain Model is that at first blush it looks like the real thing."
[4] https://martinfowler.com/bliki/BoundedContext.html — Martin Fowler — Bounded Context
    > "total unification of the domain model for a large system will not be feasible or cost-effective"
[5] https://martinfowler.com/bliki/UbiquitousLanguage.html — Martin Fowler — Ubiquitous Language
    > "Ubiquitous Language is the term Eric Evans uses in Domain Driven Design for the practice of building up a common, rigorous language between developers and users."
[6] https://martinfowler.com/bliki/MonolithFirst.html — Martin Fowler — Monolith First
    > "you
shouldn't start a new project with microservices, even if you're
sure your application will be big enough to make it worthwhile."
[7] https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis — Azure Architecture Center — Use domain analysis to model microservices
    > "Core subdomains provide a competitive advantage."
    > "Supporting subdomains keep the business operational but don't differentiate it from competitors."
    > "Generic subdomains represent problems that the industry already solved."
[8] https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-domain-driven-design — Azure Architecture Center — Use tactical DDD to design microservices
    > "As a general principle, design a microservice to be no smaller than an aggregate and no larger than a bounded context."
    > "When business logic lives outside the entity in service classes, you create an anemic domain model."
    > "Prefer value objects as your default modeling choice."
[9] https://learn.microsoft.com/en-us/azure/architecture/microservices/model/microservice-boundaries — Azure Architecture Center — Identify microservice boundaries
    > "But if you start from a carefully designed domain model, you can more easily define the correct size and scope of each microservice."
[10] https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer — Azure Architecture Center — Anti-Corruption Layer pattern
    > "Implement a facade or adapter layer between different subsystems that don't share the same semantics."
    > "Eric Evans first described this pattern in Domain-Driven Design: Tackling Complexity in the Heart of Software ."
[11] https://contextmapper.org — ContextMapper — modeling framework for strategic DDD
    > "ContextMapper is an open source project providing a Domain-specific Language and Tools for Strategic Domain-driven Design (DDD), Context Mapping, Bounded Context Modeling, and Service Decomposition."
[12] https://contextmapper.org/docs/home — ContextMapper — documentation
    > "Context Mapper is a modular and extensible modeling framework for Domain-driven Design (DDD) and its strategic patterns."
[13] https://github.com/ddd-crew/context-mapping/blob/master/README.md — ddd-crew — Context Mapping (patterns cheat sheet)
    > "There are nine context map patterns and three different team relationships."
[14] https://github.com/ddd-crew/free-ddd-learning-resources — ddd-crew — Free DDD Learning Resources
    > "A collection of resources for learning DDD. All are free to access."
[15] https://github.com/ddd-crew/ddd-starter-modelling-process — ddd-crew — DDD starter modelling process
    > "If you're new to DDD or just not sure where to start, this process can reduce your cognitive load."
[16] https://en.wikipedia.org/wiki/Domain-driven_design — Wikipedia — Domain-driven design
    > "The term was coined by Eric Evans in his book of the same name published in 2003."
[18] https://www.qlerify.com/post/event-storming-the-complete-guide — Qlerify — Event Storming: the complete guide
    > "- Big Picture – Used to explore a complex business domain collaboratively. Useful when the scope is large or unclear."
    > "- Process Modeling – Focuses on detailing a specific business process from start to finish. Useful when the starting point and the goal of the process are clear."
    > "- Software Design – Extends Process Modeling to include designing the architecture of a software system, including aggregates, commands, and bounded con"
[19] https://advanced-beginner.github.io/en/docs/ddd/appendix/ddd-debate — Advanced Beginner — DDD Debate: proponents vs skeptics
    > "most DDD I have witnessed was a ‘festival of unnecessary complexity’."
[20] https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html — Tony Marston — Why I don't do Domain Driven Design
    > "Why I don't do Domain Driven Design"
    > "While DDD contains many principles and practices, I regard these as "suggestions" and not "rules", which means that I am free to either follow them, in whole or in part, or ignore them altogether."
    > "Where I find a simpler way to achieve an objective then I will follow the KISS principle and ignore the KICK alternative."
[21] https://www.infoq.com/articles/eric-evans-ddd-matters-today — InfoQ — Eric Evans on why DDD Matters Today
    > "Fundamentally, DDD is the principle that we should be focusing on the deep issues of the domain our users are engaged in"
[22] https://l-lin.github.io/architecture/ddd/ddd-distilled/ddd-distilled---strategic-design-with-bounded-contexts-and-ubiquitous-language — DDD Distilled — strategic design notes
    > "A Bounded Context is a semantic contextual boundary."
[23] https://alistaircockburn.com/Hexagonal-Architecture — Alistair Cockburn — Hexagonal Architecture
    > "Allow an application to equally be driven by users, programs, automated test or batch scripts, and to be developed and tested in isolation from its eventual run-time devices and databases."
[24] https://www.infoq.com/news/2014/06/dddx-brandolini-eventstorming — InfoQ — Domain Modelling Using Event Storming (Alberto Brandolini)
    > "Gather all domain experts and developers in a room, provide them with a paper roll, lots of colored post-its and a facilitator and they may in hours create the best model ever"
[25] https://www.oreilly.com/library/view/domain-storytelling-a/9780137458974/app01.xhtml — O'Reilly — Domain Storytelling: history of the method
    > "Domain Storytelling: A Collaborative, Visual, and Agile Way to Build Domain-Driven Software"
[26] https://raw.githubusercontent.com/ddd-crew/context-mapping/master/README.md — ddd-crew — Context Mapping README (raw, полные определения паттернов)
    > "A protocol that gives access to your subsystem as a set of services."
    > "Eliminate the complexity of translation between bounded contexts by slavishly adhering to the model of the upstream team."
    > "As a downstream client, create an isolating layer to provide your system with functionality of the upstream system in terms of your own domain model."
    > "Designate with an explicit boundary some subset of the domain model that the teams agree to share. Keep this kernel small."
    > "Where development failure in either of two contexts would result in delivery failure for both, forge a partnership between the teams in charge of the two contexts."
    > "Establish a clear customer/supplier relationship between the two teams, meaning downstream priorities factor into upstream planning."
    > "Use a well-documented shared language that can express the necessary domain information as a common medium of communication, translating as necessary into and out of that language."
    > "Declare a bounded context to have no connection to the others at all, allowing developers to find simple, specialized solutions within this small scope"
    > "A (part of a) system which is a mess by having mixed models and inconsistent boundaries."
    > "Prefer small context maps for explicit questions"
    > "Work with smaller context maps, aimed to answer specific questions."
