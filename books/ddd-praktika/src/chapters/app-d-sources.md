# Приложение Г. Источники

*Все утверждения о первоисточниках в книге снабжены номером в квадратных
скобках. Ниже — полный перечень источников с адресами и ключевыми
дословными цитатами, на которые опирается текст.*

*Цитаты приведены в том виде, в каком они звучат в оригинале, — чтобы можно
было проверить формулировку, не доверяя пересказу.*


## Как читать ссылки

Номер в квадратных скобках после утверждения означает: это утверждение
опирается на источник под этим номером в перечне ниже. Источники
сгруппированы по типу — сначала первоисточники DDD, затем
архитектурные материалы и практические ресурсы.

## Первоисточники DDD

### [1] Eric Evans — Domain-Driven Design Reference (2015, PDF)

https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf

Ключевые формулировки:

> «ubiquitous language A language structured around the domain model and used by all team members within a bounded context to connect all the activities of the team with the software.»

> «bounded context A description of a boundary (typically a subsystem, or the work of a particular team) within which a particular model is defined and applicable.»

> «Domain-Driven Design is an approach to the development of complex software in which we: 1. Focus on the core domain. 2. Explore models in a creative collaboration of domain practitioners and software practitioners. 3. Speak a ubiquitous language within an explicitly bounded context.»

> «When you care only about the attributes and logic of an element of the model, classify it as a value object.»

> «Treat the value object as immutable.»

> «Cluster the entities and value objects into aggregates and define boundaries around each.»

> «Choose one entity to be the root of each aggregate, and allow external objects to hold references to the root only»

> «Within an aggregate boundary, apply consistency rules synchronously. Across boundaries, handle updates asynchronously.»

> «Recognize that a change in the language is a change to the model.»

> «Model information about activity in the domain as a series of discrete events.»

> «For each type of aggregate that needs global access, create a service that can provide the illusion of an in-memory collection of all objects of that aggregate's root type.»


### [2] Domain Language — DDD resources

https://www.domainlanguage.com/ddd

Ключевые формулировки:

> «This reference guide provides a quick and authoritative summary of the key concepts of Domain-Driven Design. It is not meant as a learning introduction to the subject.»


### [16] Wikipedia — Domain-driven design

https://en.wikipedia.org/wiki/Domain-driven_design

Ключевые формулировки:

> «The term was coined by Eric Evans in his book of the same name published in 2003.»


### [21] InfoQ — Eric Evans on why DDD Matters Today

https://www.infoq.com/articles/eric-evans-ddd-matters-today

Ключевые формулировки:

> «Fundamentally, DDD is the principle that we should be focusing on the deep issues of the domain our users are engaged in»


### [22] DDD Distilled — strategic design notes

https://l-lin.github.io/architecture/ddd/ddd-distilled/ddd-distilled---strategic-design-with-bounded-contexts-and-ubiquitous-language

Ключевые формулировки:

> «A Bounded Context is a semantic contextual boundary.»


## Классические эссе и паттерны

### [3] Martin Fowler — Anemic Domain Model

https://martinfowler.com/bliki/AnemicDomainModel.html

Ключевые формулировки:

> «The basic symptom of an Anemic Domain Model is that at first blush it looks like the real thing.»


### [4] Martin Fowler — Bounded Context

https://martinfowler.com/bliki/BoundedContext.html

Ключевые формулировки:

> «total unification of the domain model for a large system will not be feasible or cost-effective»


### [5] Martin Fowler — Ubiquitous Language

https://martinfowler.com/bliki/UbiquitousLanguage.html

Ключевые формулировки:

> «Ubiquitous Language is the term Eric Evans uses in Domain Driven Design for the practice of building up a common, rigorous language between developers and users.»


### [27] Martin Fowler — Value Object

https://martinfowler.com/bliki/ValueObject.html

Ключевые формулировки:

> «Objects that are equal due to the value of their properties, in this case their x and y coordinates, are called value objects.»


### [28] Martin Fowler — Event Sourcing

https://martinfowler.com/eaaDev/EventSourcing.html

Ключевые формулировки:

> «Capture all changes to an application state as a sequence of events.»


### [29] Martin Fowler — Transaction Script

https://martinfowler.com/eaaCatalog/transactionScript.html

Ключевые формулировки:

> «Organizes business logic by procedures where each procedure handles a single request from the presentation.»


### [30] Martin Fowler — CQRS

https://martinfowler.com/bliki/CQRS.html

Ключевые формулировки:

> «CQRS stands for Command Query Responsibility Segregation. It's a pattern that I first heard described by Greg Young.»

> «At its heart is the notion that you can use a different model to update information than the model you use to read information.»

> «For some situations, this separation can be valuable, but beware that for most systems CQRS adds risky complexity.»


## Архитектурные руководства

### [7] Azure Architecture Center — Use domain analysis to model microservices

https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis

Ключевые формулировки:

> «Core subdomains provide a competitive advantage.»

> «Supporting subdomains keep the business operational but don't differentiate it from competitors.»

> «Generic subdomains represent problems that the industry already solved.»


### [8] Azure Architecture Center — Use tactical DDD to design microservices

https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-domain-driven-design

Ключевые формулировки:

> «As a general principle, design a microservice to be no smaller than an aggregate and no larger than a bounded context.»

> «When business logic lives outside the entity in service classes, you create an anemic domain model.»

> «Prefer value objects as your default modeling choice.»


### [9] Azure Architecture Center — Identify microservice boundaries

https://learn.microsoft.com/en-us/azure/architecture/microservices/model/microservice-boundaries

Ключевые формулировки:

> «But if you start from a carefully designed domain model, you can more easily define the correct size and scope of each microservice.»


### [10] Azure Architecture Center — Anti-Corruption Layer pattern

https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer

Ключевые формулировки:

> «Implement a facade or adapter layer between different subsystems that don't share the same semantics.»

> «Eric Evans first described this pattern in Domain-Driven Design: Tackling Complexity in the Heart of Software .»


### [23] Alistair Cockburn — Hexagonal Architecture

https://alistaircockburn.com/Hexagonal-Architecture

Ключевые формулировки:

> «Allow an application to equally be driven by users, programs, automated test or batch scripts, and to be developed and tested in isolation from its eventual run-time devices and databases.»


### [31] Azure Architecture Center — CQRS pattern

https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs

Ключевые формулировки:

> «A common pattern is to have the write model publish events when it updates the database, which the read model uses to refresh its data.»

> «The read and write representations of data often differ.»


### [32] Microsoft Learn — Implementing value objects (.NET DDD+CQRS)

https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/implement-value-objects

Ключевые формулировки:

> «Their immutable nature allows them to be reused; they can be interchangeable objects, since their values are the same and they have no identity.»


## Практика и сообщество

### [6] Martin Fowler — Monolith First

https://martinfowler.com/bliki/MonolithFirst.html

Ключевые формулировки:

> «you shouldn't start a new project with microservices, even if you're sure your application will be big enough to make it worthwhile.»


### [11] ContextMapper — modeling framework for strategic DDD

https://contextmapper.org

Ключевые формулировки:

> «ContextMapper is an open source project providing a Domain-specific Language and Tools for Strategic Domain-driven Design (DDD), Context Mapping, Bounded Context Modeling, and Service Decomposition.»


### [12] ContextMapper — documentation

https://contextmapper.org/docs/home

Ключевые формулировки:

> «Context Mapper is a modular and extensible modeling framework for Domain-driven Design (DDD) and its strategic patterns.»


### [13] ddd-crew — Context Mapping (patterns cheat sheet)

https://github.com/ddd-crew/context-mapping/blob/master/README.md

Ключевые формулировки:

> «There are nine context map patterns and three different team relationships.»


### [14] ddd-crew — Free DDD Learning Resources

https://github.com/ddd-crew/free-ddd-learning-resources

Ключевые формулировки:

> «A collection of resources for learning DDD. All are free to access.»


### [15] ddd-crew — DDD starter modelling process

https://github.com/ddd-crew/ddd-starter-modelling-process

Ключевые формулировки:

> «If you're new to DDD or just not sure where to start, this process can reduce your cognitive load.»


### [18] Qlerify — Event Storming: the complete guide

https://www.qlerify.com/post/event-storming-the-complete-guide

Ключевые формулировки:

> «- Big Picture – Used to explore a complex business domain collaboratively. Useful when the scope is large or unclear.»

> «- Process Modeling – Focuses on detailing a specific business process from start to finish. Useful when the starting point and the goal of the process are clear.»

> «- Software Design – Extends Process Modeling to include designing the architecture of a software system, including aggregates, commands, and bounded con»


### [19] Advanced Beginner — DDD Debate: proponents vs skeptics

https://advanced-beginner.github.io/en/docs/ddd/appendix/ddd-debate

Ключевые формулировки:

> «most DDD I have witnessed was a ‘festival of unnecessary complexity’.»


### [20] Tony Marston — Why I don't do Domain Driven Design

https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html

Ключевые формулировки:

> «Why I don't do Domain Driven Design»

> «While DDD contains many principles and practices, I regard these as "suggestions" and not "rules", which means that I am free to either follow them, in whole or in part, or ignore them altogether.»

> «Where I find a simpler way to achieve an objective then I will follow the KISS principle and ignore the KICK alternative.»


### [24] InfoQ — Domain Modelling Using Event Storming (Alberto Brandolini)

https://www.infoq.com/news/2014/06/dddx-brandolini-eventstorming

Ключевые формулировки:

> «Gather all domain experts and developers in a room, provide them with a paper roll, lots of colored post-its and a facilitator and they may in hours create the best model ever»


### [25] O'Reilly — Domain Storytelling: history of the method

https://www.oreilly.com/library/view/domain-storytelling-a/9780137458974/app01.xhtml

Ключевые формулировки:

> «Domain Storytelling: A Collaborative, Visual, and Agile Way to Build Domain-Driven Software»


### [26] ddd-crew — Context Mapping README (raw, полные определения паттернов)

https://raw.githubusercontent.com/ddd-crew/context-mapping/master/README.md

Ключевые формулировки:

> «A protocol that gives access to your subsystem as a set of services.»

> «Eliminate the complexity of translation between bounded contexts by slavishly adhering to the model of the upstream team.»

> «As a downstream client, create an isolating layer to provide your system with functionality of the upstream system in terms of your own domain model.»

> «Designate with an explicit boundary some subset of the domain model that the teams agree to share. Keep this kernel small.»

> «Where development failure in either of two contexts would result in delivery failure for both, forge a partnership between the teams in charge of the two contexts.»

> «Establish a clear customer/supplier relationship between the two teams, meaning downstream priorities factor into upstream planning.»

> «Use a well-documented shared language that can express the necessary domain information as a common medium of communication, translating as necessary into and out of that language.»

> «Declare a bounded context to have no connection to the others at all, allowing developers to find simple, specialized solutions within this small scope»

> «A (part of a) system which is a mess by having mixed models and inconsistent boundaries.»

> «Prefer small context maps for explicit questions»

> «Work with smaller context maps, aimed to answer specific questions.»

