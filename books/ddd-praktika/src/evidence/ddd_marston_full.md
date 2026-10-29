- [Home](https://tonymarston.net/index.html)
- [About Me](https://tonymarston.net/aboutme/index.html)
- [PHP/MySQL](https://tonymarston.net/php-mysql/index.html)

# Why I don't do Domain Driven Design

Posted on 1st March 2018by Tony Marston

Amended on 27th July 2024

[Introduction](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#introduction)

[Table 1: Features of Domain Driven Design](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#table1)[DDD Definitions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#definitions)

[A standard design process](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#standard.design.process)[Features of my personal approach](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#my.personal.approach)

[A layered architecture](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture)[Object classification](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#object.classification)[A separate class for each table](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#one.class.per.table)[A system of subsystems](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subsystems)[What is a "domain"?](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#what.is.a.domain)

[Domains - the differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.differences)[Domains - the similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.similarities)

[Domain events](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.events)[Class names](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#class.names)[Method names](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#method.names)[Inheritance](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#inheritance)[Subclassing](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subclassing)[Separate Controllers for each use case](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#separate.controllers)[More Reusability = Higher Productivity](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#reusability.productivity)

[DDD "advice" which I ignore](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#advice.which.i.ignore)

[Associations](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.associations)[Aggregates](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates)[Compositions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.compositions)[Class hierarchies](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.class.hierarchies)[CQRS](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.cqrs)[Factories](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.factories)[Getters and Setters](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.getters.setters)[Interfaces](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.interfaces)[Method names](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.method.names)[Repositories](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.repositories)

[My implementation - Dealing with the differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#implementing.the.different)

[Entity/Table differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#entity.differences)[HTML differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#html.differences)[Transaction (use case) differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.differences)[Validation differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.differences)

[My implementation - Dealing with the similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#implementing.the.similar)

[Entity/Table similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#entity.similarities)[SQL query similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#sql.similarities)[HTML similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#html.similarities)[Transaction (use case) similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.similarities)[Validation similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.similarities)

[Conclusion](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#conclusion)[References](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#references)[Amendment History](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#history)[Comments](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#comments)

## Introduction

What is Domain Driven Design (DDD)? If you read [this Wikipedia article](https://en.wikipedia.org/wiki/Domain-driven_design), which is based on the contents of [Domain-Driven Design Reference (PDF)](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) which was written by Eric Evans, you will see that it talks about DDD consisting of a number of high-level concepts and practices such as those which I have itemised in [Table 1](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#table1) below:

|  | Feature | My implementation |
| 1 | DDD is against the idea of having a single unified model; instead it divides a large system into [bounded contexts](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#bounded-context.definition), each of which have their own model. | Refer to [A system of subsystems](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subsystems) |
| 2 | The structure and language of software code (class names, class methods, class variables) should match the business [domain](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.definition). For example: if software processes loan applications, it might have classes like "loan application", "customers", and methods such as "accept offer" and "withdraw". | Refer to [Class names](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#class.names)<br>Refer to [Method names](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#method.names)<br>Refer to [Class variables](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#class.variables) |
| 3 | Domain-driven design is based on the following goals:<br> <br>- placing the project's primary focus on the core domain and domain logic layer<br>- basing complex designs on a model of the domain<br>- initiating a creative collaboration between technical and domain experts to iteratively refine a conceptual model that addresses particular domain problems | Refer to [A separate class for each table](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#one.class.per.table) |
| 4 | Of primary importance is a _domain_ of the software, the subject area to which the user applies a program. Software's developers build a domain model: a system of abstractions that describes selected aspects of a domain and can be used to solve problems related to that domain.<br>These aspects of domain-driven design aim to foster a _common language_ shared by domain experts, users, and developers - the _ubiquitous language_. The _ubiquitous language_ is used in the domain model and for describing system requirements. <br>_Ubiquitous language_ is one of the pillars of DDD together with _strategic design_ and _tactical design_. | Refer to [domain](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.definition)<br>Refer to [ubiquitous language](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ubiquitous-language.definition)<br>Refer to [Abstraction](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#abstraction.definition) |
| 5 | In domain-driven design, the Domain layer is one of the common layers in an object-oriented multi-layered architecture. | Refer to [A layered architecture](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture) |
| 6 | Domain-driven design recognizes multiple kinds of models:<br> <br>- An **entity** is an object defined not by its attributes, but its identity.<br>- A **value object** is an immutable object that contains attributes but has no conceptual identity. | Refer to [Object classification](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#object.classification) |
| 7 | Models can also define _events_ (something that happened in the past). A domain event is an event that domain experts care about. Models can be bound together by a root entity to become an aggregate. Objects outside the aggregate are allowed to hold references to the root but not to any other object of the aggregate. The aggregate root checks the consistency of changes in the aggregate. Drivers do not have to individually control each wheel of a car, for instance: they simply drive the car. In this context, a car is an aggregate of several other objects (the engine, the brakes, the headlights, etc.). | Refer to [Domain events](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.events)<br>Refer to [Aggregates](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates)<br>Refer to [Compositions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.compositions) |
| 8 | In domain-driven design, an object's creation is often separated from the object itself.<br> <br>- A [repository](https://en.wikipedia.org/wiki/Information_repository), for instance, is an object with methods for retrieving domain objects from a data store (e.g. a database).<br>- A [factory](https://en.wikipedia.org/wiki/Factory_(object-oriented_programming)) is an object with methods for directly creating domain objects.<br>- When part of a program's functionality does not conceptually belong to any object, it is typically expressed as a [service](https://en.wikipedia.org/wiki/Service_(systems_architecture)). | Refer to [Repositories](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.repositories)<br>Refer to [Factories](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.factories) |
| 9 | A bounded context is analogous to a [microservice](https://en.wikipedia.org/wiki/Microservices). In software engineering, a microservice architecture is an architectural pattern that arranges an application as a collection of loosely coupled, fine-grained services, communicating through lightweight protocols. One of its goals is to enable teams to develop and deploy their services independently. This is achieved by creating components which exhibit [loose coupling](https://en.wikipedia.org/wiki/Loose_coupling) instead of [tight coupling](https://en.wikipedia.org/wiki/Coupling_(computer_programming)#Disadvantages_of_tight_coupling). | Refer to [Coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#coupling)<br>Refer to [Loose coupling (good)](https://tonymarston.net/php-mysql/oop-for-heretics.html#loose.coupling)<br>Refer to [Tight coupling (bad)](https://tonymarston.net/php-mysql/oop-for-heretics.html#tight.coupling) |
| 10 | Although domain-driven design is not inherently tied to object-oriented approaches, in practice, it exploits the advantages of such techniques. These include entities/aggregate roots as receivers of commands/method invocations, the encapsulation of state within foremost aggregate roots, and on a higher architectural level, bounded contexts.<br>As a result, domain-driven design is often associated with [Plain Old Java Objects](https://en.wikipedia.org/wiki/Plain_old_Java_object) and [Plain Old CLR Objects](https://en.wikipedia.org/wiki/Plain_old_CLR_object), which are technically technical implementation details, specific to Java and the .NET Framework respectively. These terms reflect a growing view that domain objects should be defined purely by the business behavior of the domain, rather than by a more specific technology framework.<br>Similarly, the [naked objects](https://en.wikipedia.org/wiki/Naked_objects) pattern holds that the user interface can simply be a reflection of a good enough domain model. Requiring the user interface to be a direct reflection of the domain model will force the design of a better domain model. | Refer to [A separate class for each table](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#one.class.per.table)<br>Refer to [Inheritance](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#inheritance)<br>Refer to [Subclassing](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subclassing)<br>Refer to [Aggregates](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates)<br>Refer to [Compositions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.compositions)<br>Refer to [Class hierarchies](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.class.hierarchies) |
| 11 | While domain-driven design is compatible with [model-driven engineering](https://en.wikipedia.org/wiki/Model-driven_engineering) and [model-driven architecture](https://en.wikipedia.org/wiki/Model-driven_architecture), the intent behind the two concepts is different. Model-driven architecture is more concerned with translating a model into code for different technology platforms than defining better domain models.<br>However, the techniques provided by model-driven engineering (to model domains, to create domain-specific languages to facilitate the communication between domain experts and developers,...) facilitate domain-driven design in practice and help practitioners get more out of their models. Thanks to model-driven engineering's model transformation and code generation techniques, the domain model can be used to generate the actual software system that will manage it. | Refer to [A standard design process](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#standard.design.process) |
| 12 | [Command Query Responsibility Segregation (CQRS)](https://en.wikipedia.org/wiki/Command_Query_Responsibility_Segregation) is an architectural pattern for separating reading data (a 'query') from writing to data (a 'command').<br>Commands mutate state and are approximately equivalent to method invocation on aggregate roots or entities. Queries read state but do not mutate it.<br>While CQRS does not require domain-driven design, it makes the distinction between commands and queries explicit with the concept of an aggregate root. The idea is that a given aggregate root has a method that corresponds to a command and a command handler invokes the method on the aggregate root.<br>The aggregate root is responsible for performing the logic of the operation and either yielding a failure response or just mutating its own state that can be written to a data store. The command handler pulls in infrastructure concerns related to saving the aggregate root's state and creating needed contexts (e.g., transactions). | Refer to [CQRS](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.cqrs) |
| 13 | Event sourcing is an architectural pattern in which entities track their internal state not by means of direct serialization or object-relational mapping, but by reading and committing events to an [event store](https://en.wikipedia.org/wiki/Event_store).<br>When event sourcing is combined with [CQRS](https://en.wikipedia.org/wiki/Command_Query_Responsibility_Segregation) and domain-driven design, aggregate roots are responsible for validating and applying commands (often by having their instance methods invoked from a Command Handler), and then publishing events. This is also the foundation upon which the aggregate roots base their logic for dealing with method invocations. Hence, the input is a command and the output is one or many events which are saved to an event store, and then often published on a message broker for those interested (such as an application's view).<br>Modeling aggregate roots to output events can isolate internal state even further than when projecting read-data from entities, as in standard n-tier data-passing architectures. One significant benefit is that axiomatic theorem provers are easier to apply, as the aggregate root comprehensively hides its internal state. Events are often persisted based on the version of the aggregate root instance, which yields a domain model that synchronizes in distributed systems through [optimistic concurrency](https://en.wikipedia.org/wiki/Optimistic_concurrency_control). | Refer to [Object Relational Mappers](https://tonymarston.net/php-mysql/object-relational-mappers-are-evil.html)<br>Refer to [Aggregates](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates)<br>Refer to [Compositions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.compositions) |

Table 1: Features of Domain Driven Design

Although domain-driven design does not depend on any particular tool or framework, there are various open source frameworks available which can help design the data model and possibly offer code generation abilities. [RADICORE](https://radicore.org/) is an open source framework specifically designed to help build and then run web-based database applications for the enterprise which are also known as [Enterprise Applications](https://en.wikipedia.org/wiki/Enterprise_software).

* * *

### DDD Definitions

domainA sphere of knowledge, influence, or activity. The subject area to which the user applies a program is the domain of the software.

A more detailed definition can be found on [this wikipedia page](https://en.wikipedia.org/wiki/Domain_(software_engineering)).

In a large system which is comprised of a number of small subsystems, is the system a single domain, or is each subsystem a separate domain?

modelA system of abstractions that describes selected aspects of a domain and can be used to solve problems related to that domain.ubiquitous languageA language structured around the domain model and used by all team members within a bounded context to connect all the activities of the team with the software.

If each [bounded context](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#bounded-context.definition) is a separate subsystem it means that the users of each subsystem may use terminology or jargon which is unknown to users of other subsystems. While this may be important in the design phase to help ensure that it meets the requirements of its users it should have no effect on the implementation as software engineers have their own jargon.

contextThe setting in which a word or statement appears that determines its meaning. _Statements about a model can only be understood in a context_.bounded contextA description of a boundary (typically a [subsystem](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subsystems), or the work of a particular team) within which a particular model is defined and applicable.

According to the [wikipedia page](https://en.wikipedia.org/wiki/Domain-driven_design#Relationship_to_other_ideas) a bounded context is analogous to a [microservice](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#microservice.definition).

microserviceA [microservice](https://en.wikipedia.org/wiki/Microservices) is defined as follows:

> In software engineering, a microservice architecture is an architectural pattern that arranges an application as a collection of loosely coupled, fine-grained services, communicating through lightweight protocols. One of its goals is to enable teams to develop and deploy their services independently. This is achieved by reducing several dependencies in the codebase, allowing developers to evolve their services with limited restrictions, and hiding additional complexity from users. Consequently, organizations can develop software with rapid growth and scalability, as well as use off-the-shelf services more easily.
>
> Services in a microservice architecture are often processes that communicate over a network to fulfill a goal using technology-agnostic protocols such as HTTP.
>
> A microservice is not a layer within a monolithic application (for example, the web controller or the backend-for-frontend). Rather, it is a self-contained piece of business functionality with clear interfaces, and may, through its own internal components, implement a layered architecture.

abstractionAbstraction is the act of separating the abstract from the concrete, the similar from the different.

As explained in [Designing Reusable Classes](http://www.laputan.org/drc/drc.html) this leads to a style of programming known as _programming-by-difference_ in which you define the _similar_ in some sort of reusable module and the _different_ in a unique module which has some sort of communication with the _similar_ module. For example, if you have several [entities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#entity.definition) which share the same protocols (methods) you can define those methods in an abstract class which can then be inherited by every concrete class.

This topic is explained in more detail in [The meaning of "abstraction"](https://tonymarston.net/php-mysql/abstraction.html).

* * *

## A standard design process

While working for various software houses where our job was to design and build bespoke systems for our clients I became very familiar with the steps needed to convert a set of requirements into a working system. Regardless of the business area involved - order processing, invoicing, stock control, shipments, timesheets, etc - these steps were always the same.

- **Gather Requirements** \- This is always the trickiest part as some clients have only a vague idea of what they want and may assume that what they want is quite common and can be satisfied with standard software. It is only when you show them a system written for a different organisation that they can say "We don't do it like _that_, we do it like _this_". They are often quite surprised at the level of detail which is required, but they have to understand that we, as software builders, can only write software that does what we were asked to make it do. If we are asked to build a system that does A, B and C and that is what we deliver, then when somebody complains that it doesn't do X, Y and Z our only response can be "X, Y and Z were not on the list of requirements". This is why the [Software Requirements Specification (SRS)](https://en.wikipedia.org/wiki/Software_requirements_specification) or Specification of Requirements (SOR) as supplied by the client has to be reworked in order to flesh out the outline requirements with those ever-so-important little details. It is quite common for the SOR to highlight only the common/usual scenarios and either gloss over, or omit entirely, the uncommon/unusual scenarios or [edge cases](https://en.wikipedia.org/wiki/Edge_case). If the designers are not told about these then how can they possibly provide a system that deals with them?

- **Analyse Requirements** \- This means going through all the requirements one by one to ensure that the terminology used by the client is understood by the designer(s), that anything assumed by the customer is stated explicitly. This sometimes means asking probing questions to ensure that not only are the normal situations covered, but also the exceptions. The number of different events is also important, as is their complexity and frequency.

- **Logical Design** \- This may only exist on paper as a [wireframe](https://en.wikipedia.org/wiki/Website_wireframe) or a [paper prototype](https://en.wikipedia.org/wiki/Paper_prototyping) which gives some indication of what the eventual system will look like and how it will operate. Better than that would be a [software prototype](https://en.wikipedia.org/wiki/Software_prototyping) which can act as a visual aid which provides a better level of interactivity, but which does not process any business rules. It can be constructed and modified very quickly using a prototyping tool, but it cannot be extended to produce the final system. It also helps to identify the logical database design, which can be expressed in an [Entity Relationship Diagram (ERD)](https://tonymarston.net/php-mysql/database-design.html#erd), and all the inputs and outputs to deal with that data. It is also essential to ensure that the design of the database is properly [normalised](https://tonymarston.net/php-mysql/database-design.html#normalisation) in order to identify where a single conceptual "object" will actually require a group of tables in a hierarchy of relationships. Each of these tables should be regarded as a separate entity with its own structure and its own rules, and each parent-child relationship should be handled separately. The client is given a walk-through of this Logical Design in order to verify that it meets all his requirements.

- The **Gather-Analyse-Design** cycle is usually an iterative process which is repeated several times until the client is sure that they have stated everything they require, that the designer(s) have fully understood each of those requirements, and that the logical design identifies to the client how those requirements will be met. It is very important that the users of the system play a part in this process. If only their managers identify the requirements they may only give a vague idea of the common situations and gloss over the exceptions. This is where the managers ask for a system that does A, B and C whereas the users want a system that does X, Y and Z. If the users who actually perform the day-to-day tasks are not given a system that helps them deal adequately with the exceptions as well as the normal then they may regard the system as being unusable and fight against its adoption.

  One the design has been signed off by the customer, meaning that they are satisfied that it will meet their requirements, the designers can produce an implementation schedule which shows the projected start and end dates for each piece of work. Resources for each piece can also be identified and costed. As each piece of work is completed, the actual dates can be compared with the planned dates to see if the project is on schedule, ahead of schedule or, more often than not, behind schedule.

- **Physical Design** \- This can only be produced after the logical design has been signed off by the client. It identifies what hardware will be needed, what software tools will be needed (such as the DBMS, programming language, framework and libraries), what programming resources will be needed, in what order the software components will be built, and the Test Plan. This is also the stage at which detailed program specifications can be written so the the programmers know precisely what they are supposed to build. The logical database design is then turned into a physical database using the chosen DBMS.
- **Implementation**\- This is where the program specifications are turned into working code so that they can be assembled into the final product. The chosen framework may provide a certain number of reusable components, so the more it provides the less will have to be developed separately. This is where the classes and their methods which will exist in the Business layer are built, the business rules are coded, and the individual events/tasks are built and tested. Testing usually has several phases:

  - Unit Testing - where the analyst who wrote the program specification checks that what the developer wrote matches the specification.
  - Integration Testing - where multiple parts of a system are tested as a group.
  - [User Acceptance Testing (UAT)](https://en.wikipedia.org/wiki/Acceptance_testing#User_acceptance_testing) \- where the users verify that the system meets their needs.

The [gather-analyse-design](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#gather-analyse-design) cycle is undertaken without reference to what structure the software will finally take as that is nothing more than an implementation detail. It is vitally important that the designer(s) know _what_ needs to be done before they start defining _how_ it can or will be done. The design of the database is far more important than the design of the software, or, as Eric S. Raymond wrote in his book [The Cathedral and the Bazaar](https://en.wikipedia.org/wiki/The_Cathedral_and_the_Bazaar):

> Smart data structures and dumb code works a lot better than the other way around.

The objective of the [gather-analyse-design](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#gather-analyse-design) cycle is to avoid the situation depicted in the following cartoon:

The [Tree Swing Cartoon](https://en.wikipedia.org/wiki/Tree_swing_cartoon)

![tree-swing-cartoon (106K)](https://tonymarston.net/php-mysql/tree-swing-cartoon.png)

This is why it is vitally important that the customer provides detailed and exact descriptions of their needs. Anything which is assumed or implied must be converted into an exact, precise and unambiguous statement so that if an issue arises as a later date it can be traced backwards through UAT, the design phase, all the way up to the SRS/SOR.

Those developers who are taught OO theory before they have any experience in working with databases can very easily fall into the trap of assuming these OO theories were carved in stone by some god-like beings and brought down from the mountain top. I have examined lots of these theories, and I can see very little evidence that the authors have ever worked on an enterprise application with large numbers of database tables and input/output screens, so I take everything they say with a pinch of salt (and sometimes a bucket of disinfectant and a scrubbing brush). Refer to [Advice which I ignore](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#advice.which.i.ignore) for details.

* * *

## Features of my personal approach

I have been designing and building enterprise applications for four decades, with the last two being dedicated to web-based enterprise applications using an object oriented language, and I do not follow the "advice" given in [Domain Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design). I say "advice" because I cannot accept them as "rules which must be obeyed".

* * *

### A layered architecture

When I started programming with COBOL it was standard practice to use the monolithic [1-Tier architecture](https://tonymarston.net/php-mysql/3-tier-architecture.html#1-tier), then when I switched to UNIFACE I was exposed to first the [2-Tier](https://tonymarston.net/php-mysql/3-tier-architecture.html#2-tier) and then the [3-Tier Architecture](https://tonymarston.net/php-mysql/3-tier-architecture.html#3-tier) which has the following layers:

- [Presentation layer](https://tonymarston.net/php-mysql/infrastructure.html#presentation.layer) \- User Interface, displaying data to the user, accepting input from the user
- [Business layer](https://tonymarston.net/php-mysql/infrastructure.html#business.layer) \- Business Rules, handles data validation and task-specific behaviour
- [Data Access layer](https://tonymarston.net/php-mysql/infrastructure.html#data.access.layer) \- Database Communication, constructing SQL queries and executing them via the relevant API

When I switched to PHP I decided to keep using the 3-Tier Architecture, but because I separated out the construction of all HTML documents into a separate component in the Presentation layer I discovered that I had also implemented the [Model-View-Controller (MVC)](https://tonymarston.net/php-mysql/model-view-controller.html) design pattern, but this was by accident, not by design (pun intended). This has the following components:

- [Controller](https://tonymarston.net/php-mysql/infrastructure.html#controller) \- receives requests and converts them into calls on one or more Models, after which it calls the View
- [Model](https://tonymarston.net/php-mysql/infrastructure.html#model) \- handles the validation and business rules for each entity within the application
- [View](https://tonymarston.net/php-mysql/infrastructure.html#view) \- converts data from the Model into the format required by the user (HTML, CSV or PDF)

The combined architecture is shown in [Figure 1](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#figure1) below:

Figure 1 \- MVC plus 3 Tier Architecture

![model-view-controller-03a (5K)](https://tonymarston.net/php-mysql/model-view-controller-03a.png)

* * *

### Object classification

Objects in the RADICORE framework fall into one of the following categories:

- **Entities** (also known as **Domain Objects**)

  An Entity's job is also mainly holding state and associated behavior. Examples of Entities could be Account or User. In a database application each table is a separate entity in the database, with its own business rules, so its methods and properties should be encapsulated in its own class. That class will typically have several public methods which allow the state to be loaded, updated and queried.

  Entities will exist as objects in the Business layer shown in [Figure 1](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#figure1) above.

- **Services**
  A Service performs an operation. It encapsulates an activity but has no encapsulated state (that is, it is stateless). It usually performs its operation on data obtained from an entity. Examples of Services could include a parser, an authenticator, a validator and a transformer. The class for a service will typically have a single public method so that it will produce a single output from a single input.

  Services will exist as objects in the Presentation and Data Access layers shown in [Figure 1](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#figure1) above, but there may also be some in the Business layer.


While **Value Objects** may exist in other languages they do not exist in PHP. Instead all [variables/properties](https://en.wikipedia.org/wiki/Variable_(computer_science)) are held as [primitive data types](https://en.wikipedia.org/wiki/Primitive_data_type) (aka [scalars](https://en.wikipedia.org/wiki/Scalar_processor#Scalar_data_type)).

The components in the RADICORE framework can be classified as follows:

- [Models](https://tonymarston.net/php-mysql/infrastructure.html#model) are **Entities**, with a separate class for each table in the application database. All standard code is inherited from an abstract class which is built into the framework.
- [Views](https://tonymarston.net/php-mysql/infrastructure.html#view) are **Services**, with a separate component for HTML, PDF and CSV output.
- [Controllers](https://tonymarston.net/php-mysql/infrastructure.html#controller) are **Services**, with a separate component for each [Transaction Pattern](https://tonymarston.net/php-mysql/dialog-types.html).
- [Data Access Objects (DAO)](https://tonymarston.net/php-mysql/infrastructure.html#dml.class) are **Services**, with a separate class for each supported DBMS engine (MySQL, PostgreSQL, Oracle and SQL Server).

It should also be noted that:

- **Services** are supplied within the framework and do not have to be created or modified by the developer. Services are also application-agnostic in that they do not contain any knowledge of any part of any application, they do not contain any business rules.
- **Entities** are generated by the application developer, one for each database table, using functions within the [Data Dictionary](https://tonymarston.net/php-mysql/data-dictionary.html), and are the only components which contain information regarding the application. Each [concrete table class](https://tonymarston.net/php-mysql/infrastructure.html#table.class) inherits standard code from an [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class), table metadata from a [table structure file](https://tonymarston.net/php-mysql/data-dictionary.html#table.dict.inc), but uses ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html) to define application-specific business rules.

* * *

### A separate class for each table

When I started to use PHP with its OO capabilities it was obvious to me that I would need to use a [layered architecture](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture) and that I would need a separate class/object in the Business layer for every entity that was of interest to the business. By the time the [implementation](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#implementation) stage is reached all these entities have been identified as tables in the database. This is why I create a separate class for each table. This simple practice leads to the following:

- Each table is subject to exactly the same [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations in the database, so these can be converted into a set of methods which can be implemented in every table class.
- These common methods/operations/protocols can then be defined in an [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class) so that they can be shared by every concrete class using [inheritance](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#inheritance).
- The use of an abstract class enables the use of the [Template Method Pattern](https://en.wikipedia.org/wiki/Template_method_pattern) which allows the abstract class to contain the fixed/invariant methods while each [concrete subclass](https://tonymarston.net/php-mysql/infrastructure.html#table.class) can interrupt the processing with custom code in any of the ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html).
- The fact that each table (Model) class shares the [same set of methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) it means that any [Controller](https://tonymarston.net/php-mysql/infrastructure.html#controller.script) which calls those methods can work with any Model.
- As each table class follows a [standard template](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#class.constructor) it is then possible to have them generated by the framework instead of having to be created manually.

The idea of creating a separate class for each database table is actually recommended in the principle of [Information Expert (GRASP)](https://tonymarston.net/php-mysql/fail-to-grasp-these-principles.html#information.expert) which states the following:

> Assign responsibility to the class that has the information needed to fulfill it.

I interpret "responsibility" to mean code and "information" to mean data, so because each database table is responsible for a different set of data it follows that I should have a separate class to control access to that data, and that class should also contain all the methods which can act upon that data.

Note that while some programmers regard [aggregates](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates) or [compositions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.compositions), which deal with several tables in a hierarchy, as being a single entity and therefore requiring its own class, I do not. I regard a single object being responsible for more than one table as being a violation of the [Single Responsibility Principle (SRP)](https://tonymarston.net/php-mysql/not-so-solid-oo-principles.html#srp).

* * *

### A system of subsystems

A large system, such as an [Enterprise Resource Planning (ERP)](https://en.wikipedia.org/wiki/Enterprise_resource_planning) system is often comprised of a number of interconnected subsystems. If they are built using the same framework or toolset then a user will be able to move through one subsystem to another without noticing the difference.

The RADICORE framework itself is comprised of four subsystems:

1. [Role Based Access Control](https://tonymarston.net/php-mysql/role-based-access-control.html) \- users, events/tasks, permissions, menus.
2. [Audit](https://tonymarston.net/php-mysql/auditlog.html) \- logs all database changes.
3. [Workflow](https://tonymarston.net/php-mysql/workflow.html) \- activity based workflows.
4. [Data Dictionary](https://tonymarston.net/php-mysql/data-dictionary.html) \- class generation and task generation.

Each subsystem has its own database, its own directory in the file system for all its files, and its own entries in the [MENU database](https://tonymarston.net/php-mysql/menuguide/section04.html).

A single logon screen gives access to all these subsystems which makes them appear as one unified system.

Additional application subsystems can be developed as add-ins whenever the need arises. For example, the [GM-X Application Suite](https://geoprise.com/content/gm-x-application-suite) contains the following subsystems:

05. [Party](https://geoprise.com/content/gm-x-party-subsystem) \- people and organisations, customers and suppliers.
06. [Product](https://geoprise.com/content/gm-x-product-subsystem) \- products, components, features, prices.
07. [Order](https://geoprise.com/content/gm-x-order-subsystem) \- sales orders, purchase orders, transfer orders.
08. [Invoice](https://geoprise.com/content/gm-x-invoice-subsystem) \- sales invoices, purchase invoices, debit notes and credit notes.
09. [Inventory](https://geoprise.com/content/gm-x-inventory-subsystem) \- products in inventory, issuances, receipts, facilities, containers, lots.
10. [Shipment](https://geoprise.com/content/gm-x-shipment-subsystem) \- outbound shipments, inbound shipments, customer shipments, supplier shipments.
11. [Request](https://geoprise.com/content/gm-x-request-subsystem) \- requirements, requests and quotations.
12. [Survey](https://geoprise.com/content/gm-x-survey-subsystem) \- surveys and questionnaires.
13. [Content](https://geoprise.com/content/gm-x-content-subsystem) \- miscellaneous content.
14. [Work Effort](https://geoprise.com/content/gm-x-work-effort-subsystem) \- timesheets and expenses.
15. [Alert](https://geoprise.com/content/gm-x-alert-subsystem) \- document management and entity-based workflow
16. [Blockchain](https://geoprise.com/content/gm-x-blockchain) \- administers the exchange of data with cooperating organisations.
17. [Personnel](https://geoprise.com/content/gm-x-strategic-hr-subsystem) \- strategic HR, performance reviews.
18. [Project](https://geoprise.com/content/gm-x-project-subsystem) \- project management
19. Finance - [general ledger](https://geoprise.com/content/gm-x-general-ledger-subsystem)
20. Finance - [accounts receivable](https://geoprise.com/content/gm-x-accounts-receivable-subsystem)
21. Finance - [accounts payable](https://geoprise.com/content/gm-x-accounts-payable-subsystem)
22. Finance - [fixed assets](https://geoprise.com/content/gm-x-fixed-assets-subsystem)

Each of theses subsystems is optional so that client organisations need only pay licence fees for those subsystems they actually need. They are also customisable as the RADICORE framework has built-in facilities which allow different screen and report layouts to be supplied at runtime, and even different versions of the business logic for individual table classes.

* * *

### What is a "domain"?

If the definition of a [domain](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.definition) is A sphere of knowledge and activity around which the application logic revolves does it mean that in a large system which is comprised of a collection of [smaller subsystems](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subsystems) that the system is the domain, or is each subsystem a separate domain? If each subsystem is a separate domain then this would imply that each would require its own separate and unique design process. In this I would have to disagree. While each of the [subsystems](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subsystems) mentioned previously has its [differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.differences) there are also a large number of [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.similarities).

#### Domains - the differences

When a novice looks at the requirements for different subsystems/domains he/she should immediately notice that there are significant differences, such as the following:

- Each has its own database with its own set of tables and columns.
- Each has its own set of inputs.
- Each has its own set of outputs.
- Each has its own set of business rules.
- Each has its own set of [user transactions](https://tonymarston.net/php-mysql/user-transaction.html) (tasks).

#### Domains - the similarities

While those differences appear to be significant an experienced developer will be be able to spot areas in the eventual implementation which are similar enough to be satisfied by reusable modules. Among these similarities are the following:

- Each table in the database, being an [entity](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#entity.definition), will require its own class/object in the [Business layer](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture). While each table has its [differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#entity.differences), there are a number of [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#entity.similarities).
- Regardless of the different structure of each table the rules for [generating SQL queries](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#sql.similarities) are exactly the same.
- Regardless of the [different data](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#html.differences) which may be displayed on an HTML form there are a significant number of [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#html.similarities).
- Each table in the database will have its own set of business and validation rules, some of which will be [similar](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.similarities) while others will be [different](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.differences).
- Each table in the database will have its own collection [user transactions](https://tonymarston.net/php-mysql/user-transaction.html) (tasks) to handle the different operations which can be performed on it, but while each will have its own unique [differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.differences) there will be some [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.similarities).

There are also some similarities which are common to each domain which can be supplied from a single central source, commonly known as a [framework](https://tonymarston.net/php-mysql/what-is-a-framework.html), such as:

- A [LOGON](https://tonymarston.net/php-mysql/menuguide/mnu_logon.html) screen through which all users must pass before they can access the system.
- A central system of [MENUS](https://tonymarston.net/php-mysql/menuguide/appendixa.html) which informs the user what actions are available to him/her.
- A central system of identifying which actions are [available](https://tonymarston.net/php-mysql/menuguide/appendixb.html) to which user.
- A central system of [logging](https://tonymarston.net/php-mysql/auditlog.html) and viewing all database changes.
- A central activity-based [Workflow](https://tonymarston.net/php-mysql/workflow.html) system.

* * *

### Domain events

An event is something that happened which caused an entity to change its state. An event is triggered by a user by activating a task ( [user transaction](https://tonymarston.net/php-mysql/user-transaction.html)) which changes the state of one or more entities.

Eric Evan's article [Domain-Driven Design\\
Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) has this to say on the subject:

> An entity is responsible for tracking its state and the rules regulating its lifecycle. But if you need to know the actual causes of the state changes, this is typically not explicit, and it may be difficult to explain how the system got the way it is. Audit trails can allow tracing, but are not usually suited to being used for the logic of the program itself.
>
> ...
>
> Domain events are ordinarily immutable, as they are a record of something in the past. In addition to a description of the event, a domain event typically contains a timestamp for the time the event occurred and the identity of entities involved in the event. Also, a domain event often has a separate timestamp indicating when the event was entered into the system and the identity of the person who entered it.

The RADICORE framework deals with this "requirement" in the following ways:

- Every database update is logged to the standard [AUDIT](https://tonymarston.net/php-mysql/auditlog.html) database which has a standard set of viewing screens.
- Every database table that I design contains the columns **created\_date**, **created\_user**, **revised\_date** and **revised\_user** which are set automatically by the framework.
- In the case of an aggregate, such as an Order or an Invoice, which is actually comprised of several database tables in a hierarchy, significant changes in state result in a change to that object's **status** column, which is maintained on the table which is the aggregate root. Changes to this value are also recorded in a separate <root>\_STATUS\_HISTORY table so that it can easily be determined who changed the status and when.

Note also that there may be business rules which identify which status changes are valid and which are not, or that certain status changes can only be performed by users with the appropriate level of security (which are known as [ROLES](https://tonymarston.net/php-mysql/menuguide/section04.html#role) in the framework).

* * *

### Class names

My standard practice is to create a separate Model class for each entity in the [Business/Domain layer](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture), which equates to a separate class for each table in the database. I do not play around with [object aggregations](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates) or [object compositions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.compositions).

Once the logical design has been completed and the database has been designed, with all its tables and columns, I then proceed to use my [Data Dictionary](https://tonymarston.net/php-mysql/data-dictionary.html) to build the subsystem's class files to mirror the database structure. I [import](https://tonymarston.net/php-mysql/menuguide/dict_table(add4)import.html) each table's structure into the Data Dictionary, adjust the details if necessary, then [export](https://tonymarston.net/php-mysql/menuguide/dict_table(upd4)export.html) them into the file system. This function will produce the following files in the **<document\_root>/<subsystem>/classes** directory:

- [<tablename>.class.inc](https://tonymarston.net/php-mysql/data-dictionary.html#table.class.inc) \- the class file, which inherits all its [standard methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) from the [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class).
- [<tablename>.dict.inc](https://tonymarston.net/php-mysql/data-dictionary.html#table.dict.inc) \- the table's structure file, whose details are loaded into the table's [standard properties](https://tonymarston.net/php-mysql/infrastructure.html#common.table.properties) when the class is instantiated into an object.

This technique makes it very easy, should the need arise, to change the structure of a table, then redo the import/export process to recreate the **<tablename>.dict.inc** file. The **<tablename>.class.inc** file is never overwritten as it may have been amended to include some ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html). Because no table names or columns names are built into any APIs there is no ripple effect by such a change.

* * *

### Method names

This is in contrast to [suggestions which I ignore](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.method.names).

As each entity in the [business/domain layer](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture) exists in the outside world as a database table, and each table, regardless of its contents, is subject to exactly the same set of [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations, it made sense to me to translate each of there operations into equivalent methods which are as follows:

- [$object->insertRecord($\_POST)](https://tonymarston.net/php-mysql/functions-and-variables.html#insertrecord) \- add a record to a database table.
- [$object->getData($where)](https://tonymarston.net/php-mysql/functions-and-variables.html#getdata) \- read records from the database. May return zero or more rows depending on the contents of the **$where** argument and the contents of the database.
- [$object->updateRecord($\_POST)](https://tonymarston.net/php-mysql/functions-and-variables.html#updaterecord) \- update a record in a database table.
- [$object->deleteRecord($\_POST)](https://tonymarston.net/php-mysql/functions-and-variables.html#deleterecord) \- delete a record from a database table.

These are documented in [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods). Note that for each of these operations the identity of the database table in question will be obtained from the [$tablename](https://tonymarston.net/php-mysql/functions-and-variables.html#notes.$tablename) property within that table's object.

Because each table class has exactly the same method signatures this provides a significant amount of [polymorphism](https://tonymarston.net/php-mysql/oop-for-heretics.html#polymorphism) which I can utilise using that mechanism known as [dependency injection](https://tonymarston.net/php-mysql/dependency-injection-is-evil.html#where.i.do.use.di). This is why I ignore DDD's "suggestions" for [method names](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.method.names) as they destroy any hope of polymorphism and the reusability which it provides.

* * *

### Class variables

These are also known as _properties_, and in a database application there is usually one for each column in the database. It is usual practice to give each of these properties the same name as its column as to do otherwise would lead to confusion.

These properties can be accessed either directly or using getters and setters (also known as [accessors and mutators](https://en.wikipedia.org/wiki/Mutator_method)):

| Access | Directly | Indirectly |
| Writing | $object->foo = 'bar'; | $object->setFoo('bar'); |
| Reading | $foo = $object->foo; | $foo = $object->getFoo(); |

Note that is also possible to specify these properties as arguments on a method/function call.

For reasons explained in [Getters and Setters](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.getters.setters) I do not have a separate property for each column as that produces [tight coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#tight.coupling). I prefer to pass all column data around as a single [$fieldarray](https://tonymarston.net/php-mysql/functions-and-variables.html#notes.$fieldarray) argument as that produces [loose coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#loose.coupling) which in turn produces components which are more reusable.

* * *

### Inheritance

[Inheritance](https://tonymarston.net/php-mysql/oop-for-heretics.html#inheritance) is a method of sharing code whereby a subclass can share the methods and properties of a superclass. The subclass may override (modify) any of the inherited methods, it may add new methods of its own, but it cannot remove or "un-inherit" any of those methods. A superclass may be inherited by any number of subclasses.

While building a small [sample application](https://tonymarston.net/php-mysql/sample-application.html) as a prototype before building the RADICORE framework I had decided to create a separate class for each database table. After creating another class for a second table I noticed a great deal of duplicated code, so I decided to move this code to an [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class) so that it could be inherited by every [concrete table class](https://tonymarston.net/php-mysql/infrastructure.html#table.class). I ended up with lots of code in the abstract class, namely a set of [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) and a set of [common table properties](https://tonymarston.net/php-mysql/infrastructure.html#common.table.properties), and nothing in each concrete class except for the [constructor](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#class.constructor). Notice that unlike some developers who employ separate methods such as `load()`, `validate()` and `store()` I learned back in by COBOL days that when a group of functions always had to be called in a specific sequence that it was more efficient to put that group into separate function which could act as a [wrapper](https://en.wikipedia.org/wiki/Wrapper_function), thus replacing several functions calls with a single call.

While the abstract class could provide all the standard code required by each concrete class, even the [primary validation](https://tonymarston.net/php-mysql/infrastructure-faq.html#faq12), it quickly became obvious that I sometimes needed to inject some non-standard code into the processing sequence for certain [user transactions](https://tonymarston.net/php-mysql/user-transaction.html). My knowledge of inheritance told me that I could add some calls to some dummy methods within the existing wrapper methods in the abstract class which I could then override in any concrete subclass. These dummy methods were defined in the abstract class but did nothing, but if they were redefined in a subclass then they could be programmed to do whatever was necessary in that subclass. I discovered later that I had actually implemented the [Template Method Pattern](https://en.wikipedia.org/wiki/Template_method_pattern) and that my dummy methods were called ["hook" methods.](https://tonymarston.net/php-mysql/radicore-hooks.html)

When I was later informed that I should be using [composition instead of inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) I thought it was a joke as nobody could explain why inheritance was bad and why "object composition", whatever it was, was supposed to be better. Nobody could supply me with any examples which demonstrated that what I had achieved with inheritance could be better achieved with "object composition". I later discovered that the so-called "problems" with inheritance were caused by inheriting from one concrete class to create a different concrete class which meant that some of the inherited methods could be completely inappropriate for the subclass. As I never encountered any of these "problems" I saw no reason to stop using inheritance. I later read in the [Gang of Four (GoF)](https://en.wikipedia.org/wiki/Design_Patterns) book on design patterns that the recommended way to avoid problems was to only ever inherit from an abstract class. This meant that what I had been doing all along was correct and that it was everybody else that was wrong.

My principle of creating a separate class for each database table was a step in the right direction as it enabled me to share the common methods and properties by inheriting them from an abstract class. As I now have a single set of methods which are shared by hundreds of subclasses this produces a large amount of [polymorphism](https://tonymarston.net/php-mysql/oop-for-heretics.html#polymorphism) which I can utilise using [dependency injection](https://tonymarston.net/php-mysql/dependency-injection-is-evil.html#where.i.do.use.di) in my library of reusable [Controller scripts](https://tonymarston.net/php-mysql/infrastructure.html#controller.script). The abstract class has also enabled me to use the [Template Method Pattern](https://en.wikipedia.org/wiki/Template_method_pattern) so that I can easily inject custom code into any table subclass.

As far as I am concerned inheritance has provided me with zero problems and bucket loads of benefits.

* * *

### Subclassing

It is quite possible that it some circumstances you may wish to perform some processing in a particular [hook method](https://tonymarston.net/php-mysql/radicore-hooks.html) for a particular task that is totally different from the code used in the same method for a different task. In this situation I use a standard OO technique called [subclassing](https://en.wikipedia.org/wiki/Inheritance_(object-oriented_programming)#Subclasses_and_superclasses). I create a subclass of the table class with a name such as `<table>_sNN` where "s" denotes a subclass and "NN" is an incrementing number. This automatically inherits all the methods in the superclass but allows me to override any of those methods with a different implementation. Note that the subclass deals with the same table as the superclass, it just provides different business rules for that table. I then change that task's [component script](https://tonymarston.net/php-mysql/infrastructure.html#component.script) to point to this subclass. You can see working examples of this in the Data Dictionary subsystem of the framework where you will find the following class files:

- dict\_table.class.inc - for standard processing
- dict\_table\_s01.class.inc - to import table names into the Data Dictionary database.
- dict\_table\_s02.class.inc - to export table data to a PHP script.
- dict\_table\_s03.class.inc - to display list of [Transaction Patterns](https://tonymarston.net/php-mysql/dialog-types.html).
- dict\_table\_s04.class.inc - to generate the scripts and update the MENU database for the selected Pattern.

* * *

### Separate Controllers for each use case

In my early days as a developer when I was working with [COBOL](https://tonymarston.net/cobol) it was common practice to create a program called "Maintain XXX" where "XXX" was a particular entity (table) which was of interest to the business. This could handle all the [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations which could be performed on that entity, so it needed a mechanism to switch from one operation to another. A typical set of operations was List, Create/Add, Read/Enquire, Update and Delete where each had its own screen and its own business logic. The difference between "List" and "Read" is that "List" can display multiple rows on the screen whereas "Read" (and all the others) can only deal with one row at a time. We called each of there operations a "mode" and had function keys (with labels) on the each screen so the user could switch from one mode to another. The program would always start in "List" mode, and the functions for the other modes were always available.

This practice was continued until the mid-1980s when a customer came up with the requirement for access to individual modes to be denied to certain users, and for the function labels to disappear when access was denied. This had be configurable on the database rather than in code so that it could be modified more easily. Creating a new database table, then modifying the code to act upon the contents of this table proved to be rather tricky, so after a while I decided that the best solution would be to break apart each multi-mode/multi-screen program and create a separate sub-program for each mode. This meant that instead of a large complex program I ended up with a collection of smaller but simpler subprograms each of which dealt with a single mode and a single screen. This resulted in the structure shown in [Figure 2](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#figure2) below:

Figure 2 \- A typical Family of Forms

![infrastructure-07 (1K)](https://tonymarston.net/php-mysql/infrastructure-07.png)

In this collection, which I now call a "family" because of the parent-child relationships, The [LIST1](https://tonymarston.net/php-mysql/dialog-types.html#list1) form is usually activated from a [menu button](https://tonymarston.net/php-mysql/dialog-types.html#menu-bar), although the [LIST2](https://tonymarston.net/php-mysql/dialog-types.html#list2) variant is usually activated from a [navigation button](https://tonymarston.net/php-mysql/dialog-types.html#navigation-bar). All the child forms are activated from [navigation buttons](https://tonymarston.net/php-mysql/dialog-types.html#navigation-bar). This means that the user has to go through the parent form in order to get to a child form. The advantage of having all the members of this family being separate tasks ( [user transactions](https://tonymarston.net/php-mysql/user-transaction.html)) with their own entries on the [TASK](https://tonymarston.net/php-mysql/menuguide/section04.html#task) table is that their positions in any [menu bar](https://tonymarston.net/php-mysql/dialog-types.html#menu-bar) or [navigation bar](https://tonymarston.net/php-mysql/dialog-types.html#navigation-bar) is not hard-coded, it is completely dynamic. The features of the [Role Based Access Control (RBAC)](https://tonymarston.net/php-mysql/role-based-access-control.html#current-design) system which is built into the framework means that access to individual members of the form family can be turned ON or OFF at will without the need for any code changes.

An additional advantage of having a separate component for each member of the forms family, coupled with the fact that each [Model (table)](https://tonymarston.net/php-mysql/infrastructure.html#table.class) class shares the same set of [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods), thus providing [polymorphism](https://tonymarston.net/php-mysql/oop-for-heretics.html#polymorphism), is that once a [Controller](https://tonymarston.net/php-mysql/infrastructure.html#controller.script) has been built to perform a series of method calls on its table class(es) it can be made to call exactly the same methods on a different table class through that mechanism known as [dependency injection](https://tonymarston.net/php-mysql/dependency-injection-is-evil.html#where.i.do.use.di). This mechanism means that each [Controller script](https://tonymarston.net/php-mysql/infrastructure.html#controller.script) can be used with any [table class](https://tonymarston.net/php-mysql/infrastructure.html#table.class).

It should also be noted that in [aggregate compositions](https://tonymarston.net/php-mysql/object-associations-are-evil.html#object.composition) I do not have a single class for the aggregate to handle all the use cases ( [user transactions](https://tonymarston.net/php-mysql/user-transaction.html)) for that aggregate. No matter how many tables are in that aggregate all I see are a number of pairs of tables which are joined in a parent-child relationship, and each pair is dealt with using its own family of forms.

Please also refer to [Transaction (use case) similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.similarities) and [Transaction (use case) differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.differences).

* * *

### More Reusability = Higher Productivity

Before I started using the OO capabilities of PHP I asked myself "why I should bother? What's so great about OOP?" I found the answer in the following statement:

> Object Oriented Programming involves programming which is oriented around objects, thus taking advantage of [Encapsulation](https://tonymarston.net/php-mysql/oop-for-heretics.html#encapsulation), [Inheritance](https://tonymarston.net/php-mysql/oop-for-heretics.html#inheritance) and [Polymorphism](https://tonymarston.net/php-mysql/oop-for-heretics.html#polymorphism) to increase code reuse and decrease code maintenance.

This rang a bell with me as the frameworks which I had developed in my two previous languages had helped increase the productivity of the whole development team by replacing the need to write chunks of identical or similar code with pre-written and reusable code. The less code you have to write to get the job done then the less time it takes to get the job done and the more productive you can be. I therefore set out to use these features of PHP to increase as much as possible the amount of reusable code I could have at my disposal.

While using a [layered architecture](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture) is a step in the right direction, it is how you construct each of the different components in that architecture which indicates if you are taking proper advantage of the features which OOP has to offer. By following my own version of "best practices", and ignoring those which have a dubious pedigree, I have been able to provide the following amounts of reusability which help reduce development times and increase my rate of productivity:

|     |     |
| --- | --- |
| [Models](https://tonymarston.net/php-mysql/infrastructure.html#model) | Each [table class](https://tonymarston.net/php-mysql/infrastructure.html#table.class) inherits all its standard code from a single [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class) while any non-standard code can be inserted into the available ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html). |
| [Views](https://tonymarston.net/php-mysql/infrastructure.html#view) | There is a single reusable component for each type of View:<br> <br>- The HTML View component works by transferring all data from the Model(s) into an XML file, then performs an [XSL Transformation](https://tonymarston.net/php-mysql/infrastructure.html#xsl.transformation) using an XSL stylesheet. I have just 12 [reusable XSL Stylesheets](https://tonymarston.net/xml-xsl/reusable-xsl.html) where the differences are supplied in separate [screen structure files](https://tonymarston.net/php-mysql/infrastructure.html#screen.structure).<br>- The PDF view component works by reading the raw data one row at a time and placing it in the document using instructions in a [report structure file](https://tonymarston.net/php-mysql/output-to-pdf.html#report.structure.file).<br>- The CSV view component works by reading the raw data one row at a time and writing it to the output file. The first row in the output file contains the column names as labels while all subsequent rows contain the column values. |
| [Controllers](https://tonymarston.net/php-mysql/infrastructure.html#controller) | Each of the reusable Controllers calls a predetermined series of methods on an unknown Model (or Models) where the identity of those Model(s) is passed down at run time from a [component script](https://tonymarston.net/php-mysql/infrastructure.html#component.script). There is a separate version of this script for each [user transaction](https://tonymarston.net/php-mysql/user-transaction.html) (task). Each Controller is paired with no more than one View, as documented in [Transaction Patterns](https://tonymarston.net/php-mysql/dialog-types.html), but there are some which have no View at all. |
| [DAOs](https://tonymarston.net/php-mysql/infrastructure.html#data.access.layer) | Each of the reusable [Data Access Objects](https://tonymarston.net/php-mysql/infrastructure.html#dml.class) generates the queries for the common [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations for a particular DBMS. Each method will build its query based on the information passed to it by the Model, then call the API which is specific to that DBMS. |

You should notice here that every Model class supports the [same set of methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) as every other Model class, and every Controller communicates with its Model(s) using those methods. This is a prime example of [polymorphism](https://tonymarston.net/php-mysql/oop-for-heretics.html#polymorphism), and it allows any Model to be used with any Controller.

You should also notice that as much standard code (often referred to as [boilerplate code](https://en.wikipedia.org/wiki/Boilerplate_code)) as possible is supplied by the framework, which means that the bulk of the developer's time can be spent on the important code which deals with the business rules.

* * *

## DDD "advice" which I ignore

While DDD contains many principles and practices, I regard these as "suggestions" and not "rules", which means that I am free to either follow them, in whole or in part, or ignore them altogether. Where I find a simpler way to achieve an objective then I will follow the [KISS principle](https://simple.wikipedia.org/wiki/KISS_principle) and ignore the [KICK](https://tonymarston.net/php-mysql/kick-principle.html) alternative.

While some of these topics are not explicitly mentioned as being part of DDD I have included them because they are part of the OO family of practices and therefore may be implied.

### Associations

When I first encountered the term [association](https://en.wikipedia.org/wiki/Association_(object-oriented_programming)) in various newsgroup postings all I saw was a complicated way of dealing with relationships. It does not matter to me how many tables are linked together in a hierarchy, that hierarchy is nothing more than a collections of tables where different pairs of tables are linked together in a parent-child relationship, and each relationship can be dealt with by standard code in the framework and not custom code in any table class.

You can read more of my thoughts on this topic in [Object Associations are EVIL](https://tonymarston.net/php-mysql/object-associations-are-evil.html).

* * *

### Aggregates

OO afficionados like to use the " [HAS-A](https://en.wikipedia.org/wiki/Has-a)" test to help them recognise things called "object compositions". The wikipedia article contains the following description:

> Has-a is a composition relationship where one object (often called the constituted object, or part/constituent/member object) "belongs to" (is part or member of) another object (called the composite type), and behaves according to the rules of ownership. In simple words, has-a relationship in an object is called a member field of an object. Multiple has-a relationships will combine to form a possessive hierarchy.

An **Aggregation** implies that the contained class can exist independently of the container. If the container is destroyed, the child is not destroyed as it can exist independently of the parent.

It does not matter to me how many objects are linked together in some sort of hierarchy, at the end of the day it is just a collection of tables which are arranged in a number of one-to-many/parent-child relations, and in the RADICORE framework there are standard patterns for dealing with parent-child relationships which do not require any custom code in any table class.

I have written more on this topic in [Object Associations - Aggregations](https://tonymarston.net/php-mysql/object-associations-are-evil.html#object.aggregation) and [A single class for an Aggregation is a mistake](https://tonymarston.net/php-mysql/object-associations-are-evil.html#single.class.aggregation).

* * *

### Compositions

A **Composition** is a type of [aggregation](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates) in which the contained class cannot exist independently of the container. If the container is destroyed, the child is also destroyed.

I have written more on this topic in [Object Associations - Compositions](https://tonymarston.net/php-mysql/object-associations-are-evil.html#object.composition).

There is a different type of composition which is supposed to be an alternative to [inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) which I have written about in [Composition is a Procedural Technique for Code Reuse](https://tonymarston.net/php-mysql/composition-is-a-procedural-technique-for-code-reuse.html).

* * *

### Class hierarchies

I have seen where more than a few developers use the " [IS-A](https://en.wikipedia.org/wiki/Is-a)" test to identify the existence of class hierarchies. They make statements such as "a CAR is-a VEHICLE", "a BEAGLE is-a DOG" and "a CUSTOMER is-a PERSON", and this causes some developers to ask the question:

> If object 'B' **is a** type of object 'A', then surely 'B' must be a subclass of 'A'?

This can lead to statements such as: A Car and a Train and a Truck can all inherit behavior from a Vehicle object, adding their subtle differences. A Firetruck can inherit from the Truck object, and so on. which would produce hierarchies of classes which are multiple levels deep.

This is not how it is handled in a database, so it is not how it should be handled in the code.

Expanding on the "a BEAGLE is-a DOG" statement from above someone who has been trained to think in the "object oriented way" would identify **dog\_type** as the differentiator and create a separate subclass for each possible value, as shown in [Using "IS-A" to identify class hierarchies](https://tonymarston.net/php-mysql/oop-for-heretics.html#is-a.relationships).

If **dog\_type** is identified as the differentiator then it should become a column on the DOG table which can be used as the foreign key to an entry on the DOG\_TYPE table. In this way it is possible to introduce as many different types of dog that you can think of without having to create a separate class for each.

In database applications every entity in the [Business/Domain layer](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture) IS-A database table, and because every table shares the same [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations every [table class](https://tonymarston.net/php-mysql/infrastructure.html#table.class) shares the [same table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) which are inherited from the same [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class). This means that I do not have any deep inheritance hierarchies, with the only exception being when I need [subclasses](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subclassing) to deal with different implementations for the standard ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html).

* * *

### CQRS

This is what it says in the [wikipedia page](https://en.wikipedia.org/wiki/Domain-driven_design#Command_Query_Responsibility_Segregation):

> [Command Query Responsibility Segregation (CQRS)](https://en.wikipedia.org/wiki/Command_Query_Responsibility_Segregation) is an architectural pattern for separating reading data (a 'query') from writing to data (a 'command'). CQRS derives from Command and Query Separation (CQS), coined by Bertrand Meyer.
>
> Commands mutate state and are approximately equivalent to method invocation on aggregate roots or entities. Queries read state but do not mutate it.

This is the description for [Command Query Responsibility Segregation (CQRS)](https://en.wikipedia.org/wiki/Command_Query_Responsibility_Segregation):

> In information technology, **Command Query Responsibility Segregation (CQRS)** is a system architecture that extends the idea behind command-query separation to the level of services. Such a system will have separate interfaces to send queries and to send commands. As in CQS, fulfilling a query request will only retrieve data and will not modify the state of the system (with some exceptions like logging access), while fulfilling a command request will modify the state of the system.
>
> Many systems push the segregation to the data models used by the system. The models used to process queries are usually called _read models_ and the models used to process commands _write models_.

The idea that I should have one model for reading and another Model for writing is unacceptable to me. As far as I am concerned this violates the principle of [encapsulation](https://tonymarston.net/php-mysql/oop-for-heretics.html#encapsulation) which states that ALL the methods and ALL the properties for an entity should be maintained in the SAME class. This means that you do not split those methods and properties across multiple classes, nor do you put methods and properties for multiple entities in the same class.

In a database application each entity in the [Business layer](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#layered.architecture) IS-A database table, and the only operations which can be performed on a database table are [Create, Read, Update and Delete (CRUD)](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete). This is why I created a [set of methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) to perform these operations, and because they are common to every table I make them available in every table class by [inheriting](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#inheritance) them from an [abstract class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class).

* * *

### Factories

In this paper [Domain-Driven Design Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) Eric Evans wrote the following:

> When creation of an entire, internally consistent aggregate, or a large value object, becomes complicated or reveals too much of the internal structure, factories provide encapsulation.

I do not use [object aggregations](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates), therefore I do not need any factories.

I do not need a method of creating objects with different configurations as each of my table objects has only one possible configuration, and that is dealt with in the [class constructor](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#class.constructor).

* * *

### Getters and Setters

While learning how PHP worked I saw that it was common practice to create classes with separate properties for each table column, and to access them using separate getters and setters. I did not like this idea as it would mean that each table (Model) class would require its own set of properties with their getters and setters and that each of these classes would then require its own Controller with the necessary code to access these unique properties. This would therefore make each Controller [tightly coupled](https://tonymarston.net/php-mysql/oop-for-heretics.html#tight.coupling) to a particular Model and throw out of the window any opportunity of having reusable code. I had already noticed that data being sent in from an HTML form was presented in an associative array, and that data read from the database was also presented in an associative array (actually an indexed array of associative arrays), so I decided not to unpick this array into its components parts but to pass it around in its array form as a single argument on every method call. This is shown in the [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) as the [$fieldarray](https://tonymarston.net/php-mysql/functions-and-variables.html#notes.$fieldarray) argument. This simple idea provided several benefits:

- As neither the Model nor the Controller required individual table columns to be defined it meant less code to write.
- As the Controller did not have to contain any references to any columns in its Model it then made them [loosely coupled](https://tonymarston.net/php-mysql/oop-for-heretics.html#loose.coupling) which meant that any Controller could use any Model.
- Because none of the method calls between the Controller and the Model reference any column names it meant that I could change the columns on any table without having to change any method signatures, thus avoiding the ripple effect.

Note that each table class "knows" what columns belong in its table as they are list in the [$fieldspec](https://tonymarston.net/php-mysql/functions-and-variables.html#notes.$fieldspec) array.

* * *

### Interfaces

By "interfaces" I mean [object interfaces](https://www.php.net/manual/en/language.oop5.interfaces.php) which require the use of those keywords **interface** and **implements**. These did not exist in PHP4 so I could not use them. They were introduced in PHP5, but after reading their description in the manual I decided that as I was already using an abstract class to great affect I had no need for them.

I later discovered that they were added to other languages to provide a way of allowing [polymorphism without inheritance](http://accelerateddevelopment.blogspot.com/2012/06/polymorphism-and-inheritance-are.html) in certain strictly typed languages. They were added to PHP just because some not-so-bright programmers said Other OO languages support interfaces, so PHP should support them as well. This is a ridiculous argument as PHP is not strictly typed, nor does it require any mechanism to support polymorphism other than several classes containing the same method signatures. This means that they are totally redundant in PHP and a complete waste of time as they serve no useful purpose.

This topic is covered in more detail in the following:

- [Object Interfaces are EVIL](https://tonymarston.net/php-mysql/object-interfaces-are-evil.html)
- [Subclasses vs Subtypes](https://tonymarston.net/php-mysql/subclasses-vs-subtypes.html)

* * *

### Method names

I have seen many examples where method names are constructed to reflect an action which has been identified in the design process, such as "createCustomer", "SignUpForMagazineSubscription", "accept offer" and "withdraw", but I never followed this practice. My aim of switching to an OO language was to use the facilities offered by [encapsulation](https://tonymarston.net/php-mysql/oop-for-heretics.html#encapsulation), [inheritance](https://tonymarston.net/php-mysql/oop-for-heretics.html#inheritance) and [polymorphism](https://tonymarston.net/php-mysql/oop-for-heretics.html#polymorphism) to create as much reusable code as possible. I therefore creating [my own convention for naming methods](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#method.names).

I also knew two things from my previous experience:

- The only operations which can be performed on a table are [Create, Read, Update and Delete (CRUD)](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete), which is why I have [methods which support these operations](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) in every [table class](https://tonymarston.net/php-mysql/infrastructure.html#table.class) which are inherited from an [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class).
- Regardless of the different effect that each [user transaction](https://tonymarston.net/php-mysql/user-transaction.html) (task) will have, it achieves that effect by following the same pattern - it calls one or more of the CRUD operations on one or more tables, and these operations may be interspersed with the processing of business rules.

This means that names such as "createCustomer", "SignUpForMagazineSubscription", "accept offer" and "withdraw" I consider to be nothing more than labels which may be beneficial to the user but which are irrelevant details in the software. By stripping away the irrelevant and concentrating on the essential I make it easy for the developer to quickly understand the effects of each [user transaction](https://tonymarston.net/php-mysql/user-transaction.html) and to identify the components that will produce that effect. The labels made available to users are nothing more than names held on the [TASK table](https://tonymarston.net/php-mysql/menuguide/mnu_task(upd1).html) in the [MENU database](https://tonymarston.net/php-mysql/menuguide/section04.html).

| OO purists | effect on the database | the Tony Marston way |
| createProduct($\_POST) | insert a record into the PRODUCT table | ```<br>$table_id = 'product';<br>....<br>require "classes/$table_id.class.inc";<br>$dbobject = new $table_id;<br>$result = $dbobject->insertRecord($_POST);<br>``` |
| createCustomer($\_POST) | insert a record into the CUSTOMER table | ```<br>$table_id = 'customer';<br>....<br>require "classes/$table_id.class.inc";<br>$dbobject = new $table_id;<br>$result = $dbobject->insertRecord($_POST);<br>``` |
| createInvoice($\_POST) | insert a record into the INVOICE table | ```<br>$table_id = 'invoice';<br>....<br>require "classes/$table_id.class.inc";<br>$dbobject = new $table_id;<br>$result = $dbobject->insertRecord($_POST);<br>``` |
| payInvoice($\_POST) | insert a record into the PAYMENT table | ```<br>$table_id = 'payment';<br>....<br>require "classes/$table_id.class.inc";<br>$dbobject = new $table_id;<br>$result = $dbobject->insertRecord($_POST);<br>``` |

In my method the value for **$table\_id** is provided in a [component script](https://tonymarston.net/php-mysql/infrastructure.html#component.script) and this is instantiated into an object in the [controller script](https://tonymarston.net/php-mysql/infrastructure.html#controller.script).

The use of an abstract class also provides the means to have methods for standard processing interspersed with methods for custom business rules. This is called the [Template Method Pattern](https://en.wikipedia.org/wiki/Template_method_pattern) and involves a mixture of invariant/fixed methods and variable/customisable or ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html) which can have different implementations in different concrete classes. Every public method in the [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class) is an example of a Template Method.

* * *

### Repositories

In this paper [Domain-Driven Design Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) Eric Evans wrote the following:

> Query access to aggregates expressed in the ubiquitous language. Proliferation of traversable associations used only for finding things muddles the model. In mature models, queries often express domain concepts. Yet queries can cause problems. The sheer technical complexity of applying most database access infrastructure quickly swamps the client code, which leads developers to dumb-down the domain layer, which makes the model irrelevant.

I do not deal with [aggregates](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates) in the DDD way.

* * *

## My implementation - Dealing with the differences

Abstraction is a process whereby you separate the abstract from the concrete, the similar from the different, with the aim of putting the similar into a reusable object and the different into unique objects. This section identifies what I recognise as "different" and how I have isolated them from the "similar".

### Entity/Table differences

While each database can contain any number of tables each one will have its differences which can be categorised under the following headings:

- Database name.
- Table name, which must be unique within the database.
- A list of columns, where each has:
  - A name which must be unique within that table.
  - A data type (character, integer, float, date, time, etc.
  - An optional size.
- A primary key, which may contain one or more columns.
- Zero or more candidate keys, where each may contain one or more columns.
- A list of one-to-many/parent-child relationships with other tables:
  - A list of child relationships where this table is the parent.
  - A list of parent relationships where this table is the child.
- Column values which can vary depending on the table and the operation being performed. Instead of having a separately named class property for each column I prefer to use a single array variable as it promotes [loose coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#loose.coupling) which is better than [tight coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#tight.coupling).

These have been implemented as a set of [common table properties](https://tonymarston.net/php-mysql/infrastructure.html#common.table.properties) which are inherited from an [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class). Each of these properties will be loaded in when the class file is instantiated into an object.

* * *

### HTML differences

Having abstracted out all the [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#html.similarities) in every [HTML document](https://tonymarston.net/php-mysql/infrastructure.html#html.output) I am left with the differences. While the [XSL Stylesheet](https://tonymarston.net/php-mysql/infrastructure.html#xsl.stylesheet) contains the necessary instructions to construct all the standard elements on the HTML page I am left with the one variable which is the zone which handles the application data. This is where I have to identify which piece of table data goes where in that zone. Because I have to copy all the necessary framework and application data to an [XML document](https://tonymarston.net/php-mysql/infrastructure.html#xml.file) I discovered, after a bit of experimentation, that I could also include a description of this application zone in this XML. This meant that instead of having a separate version of an XSL stylesheet for each different screen I could use a standard stylesheet and load data from an external [screen structure file](https://tonymarston.net/php-mysql/infrastructure.html#screen.structure) like the one shown below:

```
<?php
// this identifies which XSL stylesheet to use
$structure['xsl_file'] = 'std.detail1.xsl';

// this identifies which XML data is to go into which XSL zone
$structure['tables']['main'] = 'person';

// this specifies the width of each column
$structure['main']['columns'][] = array('width' => 150);
$structure['main']['columns'][] = array('width' => '*');

// the following may also be used
$structure['main']['columns'][] = array('class' => 'classname');

// this identifies the label and field which is to be displayed in each row
$structure['main']['fields'][] = array('person_id' => 'ID');
$structure['main']['fields'][] = array('first_name' => 'First Name');
$structure['main']['fields'][] = array('last_name' => 'Last Name');
$structure['main']['fields'][] = array('initials' => 'Initials');
$structure['main']['fields'][] = array('nat_ins_no' => 'Nat. Ins. No.');
$structure['main']['fields'][] = array('pers_type_id' => 'Person Type');
$structure['main']['fields'][] = array('star_sign' => 'Star Sign');
$structure['main']['fields'][] = array('email_addr' => 'E-mail');
$structure['main']['fields'][] = array('value1' => 'Value 1');
$structure['main']['fields'][] = array('value2' => 'Value 2');
$structure['main']['fields'][] = array('start_date' => 'Start Date');
$structure['main']['fields'][] = array('end_date' => 'End Date');
$structure['main']['fields'][] = array('selected' => 'Selected');
?>
```

Note that for input and update screens I will need to include for each application column the identity of the HTML control (textbox, radiogroup, dropdown, checkbox, etc) which should be used. This information is obtained from the [$fieldspec](https://tonymarston.net/php-mysql/data-dictionary.html#$fieldspec) array which has been loaded into the object's memory from the [table structure file](https://tonymarston.net/php-mysql/data-dictionary.html#table.dict.inc).

* * *

### Transaction (use case) differences

As explained in [Transaction (use case) similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.similarities) each [user transaction](https://tonymarston.net/php-mysql/user-transaction.html) (task) will require a [Model](https://tonymarston.net/php-mysql/infrastructure.html#model), a [View](https://tonymarston.net/php-mysql/infrastructure.html#view) and a [Controller](https://tonymarston.net/php-mysql/infrastructure.html#controller) to act in unison to carry out the task required by the user.

While each subsystem will require its own set of [user transactions](https://tonymarston.net/php-mysql/user-transaction.html) (tasks) these can be generated by the framework by linking a table class with any of the [Transaction Patterns](https://tonymarston.net/php-mysql/transaction-patterns.html) which are supplied by the framework. Each [user transaction](https://tonymarston.net/php-mysql/user-transaction.html) which then have its own [component script](https://tonymarston.net/php-mysql/infrastructure.html#component.script) in the file system which looks like the following:

```
<?php
$table_id = "person";                      // identify the Model
$screen   = 'person.detail.screen.inc';    // identify the View
require 'std.enquire1.inc';                // activate the Controller
?>
```

As you can see this is a simple script whose purpose is to identify the following:

1. `$table_id` identifies the [Model](https://tonymarston.net/php-mysql/infrastructure.html#model) part of [MVC](https://tonymarston.net/php-mysql/infrastructure.html#mvc). This is one of the generated [database table classes](https://tonymarston.net/php-mysql/infrastructure.html#table.class).
2. `$screen` identifies the [View](https://tonymarston.net/php-mysql/infrastructure.html#view) part of [MVC](https://tonymarston.net/php-mysql/infrastructure.html#mvc). This is one of the generated [screen structure scripts](https://tonymarston.net/php-mysql/infrastructure.html#screen.structure) which identifies the [HTML differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#html.differences).
3. `include` identifies the [Controller](https://tonymarston.net/php-mysql/infrastructure.html#controller) part of [MVC](https://tonymarston.net/php-mysql/infrastructure.html#mvc). This is one of the pre-written [controller scripts](https://tonymarston.net/php-mysql/infrastructure.html#controller.script).

Each Controller is designed to work with only a single View, but a small number of Controllers do not have a View at all. For a complete list of the available Controllers and the Views which they support please refer to [Transaction Patterns for web applications](https://tonymarston.net/php-mysql/dialog-types.html).

Note that each [Controller](https://tonymarston.net/php-mysql/infrastructure.html#controller.script) can work with any Model, but it does not know which one until it is given a value for `$table_id` at run-time. It also means that each Model can work with any Controller.

Use these links for the [validation similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.similarities) and [validation differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.differences).

* * *

### Validation differences

While the [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.similarities) can be handled by a standard component within the framework it is often necessary for a particular operation on a particular table to be interrupted at a particular point in order to execute some custom code, either for some non-standard data validation or to apply a particular business rule. This can be done in the RADICORE framework by locating the relevant [customisable method](https://tonymarston.net/php-mysql/functions-and-variables.html#customisable.methods) which has been been into the processing flow for that operation, then copying that empty method into the subclass so that it can be filled with the necessary code. Various methods are available, such as:

- [\_cm\_commonValidation()](https://tonymarston.net/php-mysql/functions-and-variables.html#notes._cm_commonvalidation)
- [\_cm\_validateInsert()](https://tonymarston.net/php-mysql/functions-and-variables.html#notes._cm_validateinsert)
- [\_cm\_validateUpdate()](https://tonymarston.net/php-mysql/functions-and-variables.html#notes._cm_validateupdate)
- [\_cm\_validateDelete()](https://tonymarston.net/php-mysql/functions-and-variables.html#notes.validatedelete)

There are also other customisable methods with names such as the following:

- `_cm_pre_<operation>()` \- for processing "before" the operation, such as [\_cm\_pre\_insertRecord()](https://tonymarston.net/php-mysql/functions-and-variables.html#notes._cm_pre_insertrecord).
- `_cm_post_<operation>()` \- for processing "after" the operation, such as [\_cm\_post\_insertRecord()](https://tonymarston.net/php-mysql/functions-and-variables.html#notes._cm_post_insertrecord).

Note that these customisable methods are available because of my implementation of the [Template Method Pattern](https://tonymarston.net/php-mysql/template-method-pattern-as-a-framework.html) which was made possible because of my decision for all [concrete table classes](https://tonymarston.net/php-mysql/infrastructure.html#table.class) to inherit from an [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class).

* * *

## My implementation - Dealing with the similarities

Abstraction is a process whereby you separate the abstract from the concrete, the similar from the different, with the aim of putting the similar into a reusable object and the different into unique objects. This section identifies what I recognise as "similar" and how I have turned them into reusable components.

### Entity/Table similarities

Although each database table holds different data they are all subject to exactly the same set of operations which are [Create, Read, Update and Delete (CRUD)](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete). These have been implemented as a set of [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) which are inherited from an [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class). Instead of having separate methods for `load()`, `validate()` and `store()` I have grouped them together into wrapper methods as they always have to be called in the same sequence, and it is more efficient to write a single call to a wrapper method instead of a number of calls to the low-level methods. It also makes it easier to modify the contents of a wrapper method without having to modify any code which calls that method.

The advantage of being able to inherit these methods from an abstract class is that they do not have to be defined in each concrete class as they are automatically there when the class is instantiated into an object. This is why each table class file can be [generated](https://tonymarston.net/php-mysql/menuguide/dict_table(upd4)export.html) from the same template, as shown below:

```
<?php
require_once 'std.table.class.inc';
class #tablename# extends Default_Table
{
    // ****************************************************************************
    // class constructor
    // ****************************************************************************
    function __construct ()
    {
        // save directory name of current script
        $this->dirname   = dirname(__file__);

        $this->dbname    = '#dbname#';
        $this->tablename = '#tablename#';

        // call this method to get original field specifications
        // (note that they may be modified at runtime)
        $this->fieldspec = $this->loadFieldSpec();

    } // __construct

// ****************************************************************************
} // end class
// ****************************************************************************
?>
```

The [loadFieldSpec()](https://tonymarston.net/php-mysql/functions-and-variables.html#notes.loadfieldspec) method is responsible for transferring the contents of the [table structure file](https://tonymarston.net/php-mysql/data-dictionary.html#table.dict.inc) into the object's [common table properties](https://tonymarston.net/php-mysql/infrastructure.html#common.table.properties) which configures the object with all the knowledge it requires so that it can deal effectively with that particular table.

Note that the table class file, when it is first created, does not contain any methods other than the constructor as all the standard processing is performed by the [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods) which are inherited from the [abstract table class](https://tonymarston.net/php-mysql/infrastructure.html#generic.table.class). The use of an abstract class enables the [Template Method Pattern](https://en.wikipedia.org/wiki/Template_method_pattern) to be implemented. This involves the use of invariant/fixed methods to be defined in the superclass which can be interspersed with variable/customisable ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html) which can be overridden within each subclass to provide custom behaviour.

* * *

### SQL query similarities

Communicating with a relational database is very straightforward. It is a simple matter of constructing an [SQL](https://en.wikipedia.org/wiki/SQL) query, which is a string of text, and sending to the database using the relevant `<dbms>_query()` function. There are only four basic methods for manipulating data, part of the [Data Manipulation Language (DML)](https://en.wikipedia.org/wiki/Data_manipulation_language), and they are:

- [CREATE/INSERT](https://en.wikipedia.org/wiki/Insert_(SQL))
- [READ/SELECT](https://en.wikipedia.org/wiki/Select_(SQL))
- [UPDATE](https://en.wikipedia.org/wiki/Update_(SQL))
- [DELETE](https://en.wikipedia.org/wiki/Delete_(SQL))

The query string which is constructed for each of these operations/methods follows the same pattern regardless of what data is being processed.

| Operation | Code |
| Create | ```<br>INSERT INTO <tablename> (column1, column2, column3) VALUES ('value1', 'value2', 'value3');<br>``` |
| Read | ```<br>simple:<br>SELECT * FROM <tablename> [WHERE <condition>]<br>advanced:<br>SELECT <select list><br>FROM <tablename><br>[JOIN <tablename2> ON (...)]<br>[WHERE <condition>]<br>[GROUP BY ...]<br>[HAVING ...]<br>[ORDER BY ...]<br>[LIMIT ... OFFSET ...]<br>``` |
| Update | ```<br>UPDATE <tablename> SET column1='value1', column2='value2', column3='value3' WHERE <condition><br>``` |
| Delete | ```<br>DELETE FROM <tablename> WHERE <condition><br>``` |

Common SQL protocols

Note that the `Create`, `Update` and `Delete` operations function on only one table at a time whereas the `Read` operation can obtain data from several tables.

As you should see the table names, column names and column values are nothing more than pieces of text which appear in the query string along with various keywords, so none of these names have to be specified in separate arguments on the function call to the DBMS. As PHP has excellent string handling functions I found it very easy to create a single [Data Access Object (DAO)](https://tonymarston.net/php-mysql/infrastructure.html#dml.class) which can handle the generation and execution of any query for any table in any database. Each of the four methods - one for each of the above operations - is fairly basic as it responds to the instruction "take _this_ data and construct and execute an SQL query for the DBMS". All I have is a separate DAO class for each supported DBMS (MySQL, PostgreSQL, Oracle and SQL Server) as the query strings may be similar but the function calls are not.

I have seen other people's implementations where they have a separate DAO for each table, but my method is far easier as I can add, remove or modify tables at will without having to add, remove or modify any DAOs.

* * *

### HTML similarities

Unlike in my previous languages where each screen had to be built using a special tool and then compiled, I knew that each web page was nothing more than a text file, with a mixture of tags and values, that had to be constructed from scratch before it could be sent to the client device. I also knew that I did not want to follow the examples I encountered in various books and online tutorials and build each HTML document by spitting out little fragments one piece at a time during the execution of each script.

Because in my previous languages I had built hundreds of different screens for dozens of different applications I had already begun to spot a number of similarities between them. While each screen had different values they each had a structure that was common to other screens, so I looked for a way to hold each different structure in some sort of template so that at run time all I needed to do was fill that template with values. I did not bother searching for templating systems as I had already encountered XML and XSL Transformations in UNIFACE. I played with these on my home computer and discovered that I could easily transform XML into HTML, so after confirming that PHP had the ability to [create XML documents from SQL data](https://tonymarston.net/php-mysql/domxml.html) and perform [XSL Transformations](https://tonymarston.net/php-mysql/sablotron.html), I decided to build all my web pages in this way.

For this I built a standard service object which took as its input one or more entities from the Business/Domain layer and the identity of an XSL stylesheet. Its function was to copy each entity's data into the XML document, add various framework data into that document, load the nominated XSL stylesheet into memory, then perform the XSL transformation. The output from this process was then sent to the client device. In my initial version, which is described in [Generating dynamic web pages using XSL and XML](https://tonymarston.net/xml-xsl/xml-and-xsl.html), I had a separate XSL stylesheet for each screen as I had to specify which piece of data went where. After some experimentation and refactoring I found a way to replace these custom-built XSL stylesheets with a smaller collection of [Reusable XSL Stylesheets and Templates](https://tonymarston.net/xml-xsl/reusable-xsl.html) which make use of a separate [screen structure file](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#html.differences) to identify which piece of application data goes where.

The areas of each web page which area common and can be supplied by the framework without any intervention by the developer are as follows:

- [Menu Bar](https://tonymarston.net/php-mysql/dialog-types.html#menu-bar)
- [Title & QuickSearch Bar](https://tonymarston.net/php-mysql/dialog-types.html#title-bar)
- [Navigation Bar](https://tonymarston.net/php-mysql/dialog-types.html#navigation-bar)
- [Column Headings](https://tonymarston.net/php-mysql/dialog-types.html#column-headings) (for data areas containing [multiple rows](https://tonymarston.net/php-mysql/dialog-types.html#data-area.multiple))
- [Message Area](https://tonymarston.net/php-mysql/dialog-types.html#message-area)
- [Pagination Area](https://tonymarston.net/php-mysql/dialog-types.html#pagination) (for data areas containing [multiple rows](https://tonymarston.net/php-mysql/dialog-types.html#data-area.multiple))
- [Scrolling Area](https://tonymarston.net/php-mysql/dialog-types.html#scrolling) for data areas containing [single rows](https://tonymarston.net/php-mysql/dialog-types.html#data-area.single)
- [Action Bar](https://tonymarston.net/php-mysql/dialog-types.html#action-bar)

Each screen has its own [Data area](https://tonymarston.net/php-mysql/dialog-types.html#data-area) which is supplied by each table class.

I had observed earlier that after building a [user transaction](https://tonymarston.net/php-mysql/user-transaction.html) which did _something_ to a particular database table that I often needed to produce another transaction which did the _same thing_ to a different table. On closer examination I was able to split each transaction into three categories - [structure, behaviour and content](https://tonymarston.net/php-mysql/transaction-patterns.html#transaction.pattern) \- where the structure and behaviour were the same with just the content being different. I first documented this idea from my experience with [Component Templates](https://tonymarston.net/uniface/componenttemplates.html) in UNIFACE which, for my PHP implementation, I later updated to [What are Transaction Patterns?](https://tonymarston.net/php-mysql/transaction-patterns.html) This collection of patterns works as follows:

- the **structure** is provided by the [XSL stylesheet](https://tonymarston.net/php-mysql/infrastructure.html#xsl.stylesheet)
- the **behaviour** is provided the [Controller script](https://tonymarston.net/php-mysql/infrastructure.html#controller.script)
- the **content** is provided by the [Model/Table](https://tonymarston.net/php-mysql/infrastructure.html#table.class)

Note that each screen structure is documented in the RADICORE library of [Transaction Patterns for web applications](https://tonymarston.net/php-mysql/dialog-types.html) where it is coupled with a reusable [Controller script](https://tonymarston.net/php-mysql/infrastructure.html#controller.script) to provide a standard pattern for [user transactions](https://tonymarston.net/php-mysql/user-transaction.html) (tasks). Note that any Controller script can be used with any [Model (table) class](https://tonymarston.net/php-mysql/infrastructure.html#table.class) as they all use the same set of [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods). This provides vast amounts of [polymorphism](https://tonymarston.net/php-mysql/oop-for-heretics.html#polymorphism) which is a vital ingredient of [Dependency Injection](https://tonymarston.net/php-mysql/dependency-injection-is-evil.html#where.i.do.use.di).

* * *

### Transaction (use case) similarities

Note that when I use the word "transaction" I mean [user transaction](https://tonymarston.net/php-mysql/user-transaction.html) (to differentiate from a [database transaction](https://en.wikipedia.org/wiki/Database_transaction)). In the RADICORE framework I also use the name "task" (because it's nice and short) as details of each task are stored in the framework's [TASK](https://tonymarston.net/php-mysql/menuguide/section04.html#task) table.

Using the structure shown in [Figure 1](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#figure1) it follows that every task in the system will need one component from each of those component types, and each of these components will be provided from different sources as follows:

- [Model](https://tonymarston.net/php-mysql/infrastructure.html#model) \- a [table class file](https://tonymarston.net/php-mysql/infrastructure.html#table.class) for that subsystem which was [generated](https://tonymarston.net/php-mysql/menuguide/dict_table(upd4)export.html) from the [Data Dictionary](https://tonymarston.net/php-mysql/data-dictionary.html).
- [View](https://tonymarston.net/php-mysql/infrastructure.html#view) \- one of the HTML, CSV or PDF components supplied by the framework. Note that some Controllers do not use a View.
- [Controller](https://tonymarston.net/php-mysql/infrastructure.html#controller) \- one of the [Controller scripts](https://tonymarston.net/php-mysql/infrastructure.html#controller.script) supplied by the framework.
- [DAO](https://tonymarston.net/php-mysql/infrastructure.html#dml.class) \- one of the DBMS drivers supplied by the framework. This is identified in the applications CONFIG file.

Note that it does not matter how much data is submitted on the HTML form or what the column/field names are, it is all made available in the [$\_POST](https://www.php.net/manual/en/reserved.variables.post) variable which is an associative array. In order to remove the need for code to deconstruct this array and feed in the data one piece at a time, which would automatically produce [tight coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#tight.coupling), I leave this array intact as pass it around as a standard `$fieldarray` argument on all method calls, as shown in [common table methods](https://tonymarston.net/php-mysql/infrastructure.html#common.table.methods).

Note that a particular [Controller scripts](https://tonymarston.net/php-mysql/infrastructure.html#controller.script) and a particular [View](https://tonymarston.net/php-mysql/infrastructure.html#view) are paired together to form a [Transaction Pattern](https://tonymarston.net/php-mysql/dialog-types.html).

The identity of each of these components is documented in the [Transaction (use case) differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#transaction.differences).

Each of these [user transactions](https://tonymarston.net/php-mysql/user-transaction.html) (tasks) will require entries in the framework's [MENU database](https://tonymarston.net/php-mysql/menuguide/section04.html) as follows:

- An entry on the [TASK](https://tonymarston.net/php-mysql/menuguide/section04.html#task) table to provide a user-friendly title and other settings.
- An entry on the [MENU](https://tonymarston.net/php-mysql/menuguide/section04.html#menu) table if it is to appear in the [Menu bar](https://tonymarston.net/php-mysql/menuguide/section03.html#menu-bar).
- An entry on the [NAVIGATION\_BUTTON](https://tonymarston.net/php-mysql/menuguide/section04.html#menu) table if it is to appear in the [Navigation bar](https://tonymarston.net/php-mysql/menuguide/section03.html#navigation-bar) for a parent task.
- An entry on the [ROLE\_TASK](https://tonymarston.net/php-mysql/menuguide/section04.html#role-task) table to grant access to this task to user with this [ROLE](https://tonymarston.net/php-mysql/menuguide/section04.html#role).

Each user of the system will require the following entries in the framework's [MENU database](https://tonymarston.net/php-mysql/menuguide/section04.html):

- An entry on the [USER](https://tonymarston.net/php-mysql/menuguide/section04.html#user) table to identity each person who is authorised to access the system.
- One or more entries on the [USER\_ROLE](https://tonymarston.net/php-mysql/menuguide/section04.html#user-role) table to identify the different [ROLES](https://tonymarston.net/php-mysql/menuguide/section04.html#role) that the user may have.

It is only necessary to construct one set of [Menus](https://tonymarston.net/php-mysql/menuguide/appendixa.html) and Navigation buttons as it is a function of the [Role Based Access Control (RBAC)](https://tonymarston.net/php-mysql/role-based-access-control.html#current-design) software which is built into the framework to filter out any task to which the user does not have access. If the user cannot see a button to activate the task then it cannot be activated.

Use these links for the [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.similarities) and [differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#validation.differences) in the validation and business rules.

* * *

### Validation similarities

There is one universal rule that every developer SHOULD follow when writing software which takes input from a user and adds it to the database and that is to check that each piece of data is compatible with its column specifications BEFORE it is sent to the database otherwise the query will not execute and the software will come to a grinding halt. The correct behaviour is to check each column's value against its specifications, and if this check fails in any way it should be sent back to the user with a suitable error message so that the mistake can be corrected so that the operation can be tried again.

Because this is a universal requirement it should be possible to perform this checking in a standard component. This can be done within the RADICORE framework because of two simple design decisions:

- I do not have a separate class property for each column's data. Instead I pass all the data into and out of each table's object as an associative array. This is to take advantage of the fact that data sent in from an HTML form is presented in the [$\_POST](https://www.php.net/manual/en/reserved.variables.post) array, and data retrieved from the database using the [<dbms>\_fetch\_assoc()](https://www.php.net/manual/en/mysqli-result.fetch-assoc.php) method will also be returned as an associative array.
- Each column's specifications are available in the [$fieldspec](https://tonymarston.net/php-mysql/functions-and-variables.html#notes.$fieldspec) array.

Note that the use of separate class properties for each column leads to [tight coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#tight.coupling) (which is bad) whereas a single array property leads to [loose coupling](https://tonymarston.net/php-mysql/oop-for-heretics.html#loose.coupling) (which is good)

The existence of these two arrays then makes it a simple process to write a [standard validation object](https://tonymarston.net/php-mysql/infrastructure.html#validation.class) which can compare the contents of the two arrays to verify that each column's value matches its specifications.

* * *

## Conclusion

I have designed and built numerous enterprise applications from scratch using totally different languages over several decades, so I have more than a passing knowledge of the steps which are required to undertake such a task. The iterative [Gather-Analyse-Design](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#gather-analyse-design) cycle is always the same, it is only the results of those iterations, the database design, the business rules, and the tasks required to maintain the contents of that database which are different. The deciding factors for a successful implementation are always the same - the accuracy of the design closely followed by the ability of the development team to implement this design using the tools at their disposal. These tools will include the programming language, the DBMS, the code editor, the debugger, and the framework. If any of these is not up to par - either the design, the developers or the development tools - then the result will also not be up to par.

An experienced developer should realise that, despite the differences in the databases, every table is subject to exactly the same operations and can therefore be handled in the same way. Despite the differences in the business rules they can all be handled in the same way. Because these differences can be handled in similar ways it should be possible to reduce these patterns of similarities into reusable code.

I have encountered numerous formalised design methodologies over the years, but neither I nor my fellow developers could ever be persuaded to commit ourselves 100% to a single methodology. We have always chosen the [pick-and-mix](https://www.ldoceonline.com/dictionary/pick-and-mix) approach whereby we picked the parts that we liked, ignored the parts that we didn't like, and mixed them together in a way that suited us. I particularly dislike those parts of DDD which are biased towards the way that OO thinkers are taught to build their solutions, such as [associations](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.associations), [aggregations](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.aggregates), [compositions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.compositions), [factories](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.factories) and [repositories](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#ignore.repositories). Those are _implementation details_ and should have no effect on the design process.

A large [Enterprise Application](https://en.wikipedia.org/wiki/Enterprise_software) often has to cover a collection of different business areas, but it would be wrong to think of each of these areas as a separate [domain](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#what.is.a.domain) as they have their [similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.similarities) as well as their [differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.differences). It is precisely because of the volume of similarities that I think of this collection of business areas to be a complete system while each member of this collection is just a [subsystem](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#subsystems). The domain/system is therefore a database application while each subdomain/subsystem is just an implementation of that domain which deals with its particular [differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#domain.differences).

I designed and built the RADICORE framework specifically to deal with the domain of database application, which means that it has standard ways of dealing with database tables and their relationships, and each subsystem/subdomain can deal with its own set of tables and relationships using these standard ways. The framework also has standard ways of generating HTML pages, CSV files and PDF reports. Once the database has been designed and built the framework's [Data Dictionary](https://tonymarston.net/php-mysql/data-dictionary.html) can be used to generate both the table classes and, using its library of [Transaction Patterns](https://tonymarston.net/php-mysql/dialog-types.html), the [user transactions](https://tonymarston.net/php-mysql/user-transaction.html) necessary to maintain the contents of those tables. While each of these transactions can be run immediately from the framework's system of menus they do not contain any business rules, but the developer can add these later by inserting the necessary code into the ["hook" methods](https://tonymarston.net/php-mysql/radicore-hooks.html) which are available in every table's class. Each subsystem is therefore generated by the framework as an add-on and run from the framework as just another part of an integrated system.

The current [RADICORE](https://radicore.org/) framework is actually the third iteration of a framework which I first developed in the mid-1980s in [COBOL](https://tonymarston.net/cobol) and in the 1990s in [UNIFACE](https://tonymarston.net/uniface), and each iteration has improved my levels of productivity. For example, the time taken to implement [this family of forms](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#figure2) for a single database table has been reduced as follows:

- In COBOL it would take 5 (five) days.
- In UNIFACE it would take 1 (one) day.
- In PHP it takes 5 (five) minutes. (yes, I did write MINUTES and not DAYS).

No matter what the OO afficionados say I ALWAYS start writing code AFTER I have designed and constructed a properly [normalised](https://tonymarston.net/php-mysql/database-design.html#normalisation) database, then I use RADICORE's code generation facilities to construct the basic components which I then season to taste. When I came to build the [TRANSIX](http://web.archive.org/web/20140105143230/http://transitionengineering.com/) application in 2007, my first ERP package I started with some comprehensive database designs which I found in Len Silverston's [Data Model Resource Book](https://www.amazon.com/Data-Model-Resource-Book-Vol/dp/0471380237). These database were PARTY, PRODUCT, ORDER, INVOICE, INVENTORY and SHIPMENTS. I built the components, added the business rules, and demonstrated the first working version to a customer after just 6 man-months. That is an average of one man-month per database. If I were to change my methods and follow the "advice" given by these pseudo-experts and their so-called "best practices" then my levels of productivity would plummet like a lead balloon, so excuse me if I don't follow the crowd and become a [Cargo Cult Programmer](https://en.wikipedia.org/wiki/Cargo_cult_programming) like so many others in the programming community.

Here endeth the lesson. Don't applaud, just throw money.

* * *

## References

- [Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design) from wikipedia
- [Domain-Driven Design Reference (PDF)](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf) by Eric Evans
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html) by Martin Fowler
- [Get your feet wet with domain-driven design: 3 guiding principles](http://web.archive.org/web/20191224181536/https://techbeacon.com/app-dev-testing/get-your-feet-wet-domain-driven-design-3-guiding-principles) from techbeacon.com
- [Domain-Driven Design (DDD)](https://www.geeksforgeeks.org/domain-driven-design-ddd/) from GeeksforGeeks
- [The Concept of Domain-Driven Design Explained](https://medium.com/microtica/the-concept-of-domain-driven-design-explained-3184c0fd7c3f) from medium.com
- [DDD: Strategic Design: Core, Supporting, and Generic Subdomains](https://blog.jonathanoliver.com/ddd-strategic-design-core-supporting-and-generic-subdomains/) by Jonathan Oliver
- [The Most Common Domain-Driven Design Mistake](https://medium.com/navalia/the-most-common-domain-driven-design-mistake-6c3f90e0ec2b) from medium.com
- [Domain Driven Disaster](https://dev.to/cheetah100/domain-driven-disaster-147i) by Peter Harrison
- [The failed promise of Domain-Driven Design - part 1](https://no-kill-switch.ghost.io/the-failed-promise-of-domain-driven-design-part-1/) by Sebastian Gebski
- [The failed promise of Domain-Driven Design - part 2](https://no-kill-switch.ghost.io/the-failed-promise-of-domain-driven-design-part-2/) by Sebastian Gebski
- [The failed promise of Domain-Driven Design - part 3](https://no-kill-switch.ghost.io/the-failed-promise-of-domain-driven-design-part-3/) by Sebastian Gebski

The following articles describe aspects of my framework:

- [User Guide to the Menu and Security (RBAC) System](https://tonymarston.net/php-mysql/menuguide/index.html)
- [User Guide to the Audit Logging System](https://tonymarston.net/php-mysql/menuguide/appendixl.html)
- [User Guide to the Workflow System](https://tonymarston.net/php-mysql/menuguide/appendixm.html)
- [User Guide to the Data Dictionary](https://tonymarston.net/php-mysql/menuguide/appendixn.html)

- [RADICORE - A Development Infrastructure for PHP](https://tonymarston.net/php-mysql/infrastructure.html)
- [Transaction Patterns for Web Applications](https://tonymarston.net/php-mysql/dialog-types.html)
- [Reusable XSL Stylesheets and Templates](https://tonymarston.net/xml-xsl/reusable-xsl.html)
- [The Model-View-Controller (MVC) Design Pattern for PHP](https://tonymarston.net/php-mysql/model-view-controller.html)
- [A Role-Based Access Control (RBAC) system for PHP](https://tonymarston.net/php-mysql/role-based-access-control.html)
- [FAQ on the Radicore Development Infrastructure](https://tonymarston.net/php-mysql/infrastructure-faq.html)
- [Creating an Audit Log with an online viewing facility](https://tonymarston.net/php-mysql/auditlog.html)
- [An activity based Workflow Engine for PHP](https://tonymarston.net/php-mysql/workflow.html)
- [UML diagrams for the Radicore Development Infrastructure](https://tonymarston.net/php-mysql/uml-diagrams.html)
- [A Data Dictionary for PHP Applications](https://tonymarston.net/php-mysql/data-dictionary.html)
- [Internationalisation and the Radicore Development Infrastructure (Part 1)](https://tonymarston.net/php-mysql/internationalisation.html)
- [Internationalisation and the Radicore Development Infrastructure (Part 2)](https://tonymarston.net/php-mysql/internationalisation2.html)
- [RADICORE for PHP - Functions, Methods and Variables](https://tonymarston.net/php-mysql/functions-and-variables.html)
- [The RADICORE Security Model](https://tonymarston.net/php-mysql/radicore-security.html)
- [RADICORE for PHP - creating PDF output](https://tonymarston.net/php-mysql/output-to-pdf.html)
- [What is a framework?](https://tonymarston.net/php-mysql/what-is-a-framework.html)
- [What is the 3-Tier Architecture?](https://tonymarston.net/php-mysql/3-tier-architecture.html)
- [Blockchain for Blockheads](https://tonymarston.net/php-mysql/blockchain-for-blockheads.html)
- [Anatomy of an Enterprise Application](https://tonymarston.net/php-mysql/anatomy-of-an-enterprise-application.html)
- [The Template Method Pattern as a Framework](https://tonymarston.net/php-mysql/template-method-pattern-as-a-framework.html)
- [How Radicore's Hook System Works](https://tonymarston.net/php-mysql/radicore-hooks.html)
- [Evolution of the RADICORE framework](https://tonymarston.net/php-mysql/evolution-of-the-radicore-framework.html)
- [The Road to Rapid Application Development (RAD)](https://tonymarston.net/php-mysql/road-to-rad.html)

The following articles express my heretical views on the topic of OOP:

- [Design Patterns - a personal perspective](https://tonymarston.net/php-mysql/design-patterns.html)
- [Object-Oriented Programming for Heretics](https://tonymarston.net/php-mysql/oop-for-heretics.html)
- [Development Standards - Limitation or Inspiration?](https://tonymarston.net/php-mysql/standards.html)
- [Design Patterns are dead! Long live Transaction Patterns!](https://tonymarston.net/php-mysql/design-patterns-are-dead.html)
- [What is Object Oriented Programming (OOP)?](https://tonymarston.net/php-mysql/what-is-oop.html)
- [Not the three greatest paragraphs ever written on encapsulation](https://tonymarston.net/php-mysql/not-the-three-greatest-paragraphs-ever-written-on-encapsulation.html)
- [Table Oriented Programming (TOP)](https://tonymarston.net/php-mysql/table-oriented-programming.html)
- [A minimalist approach to Object Oriented Programming with PHP](https://tonymarston.net/php-mysql/minimalist-approach-to-oop-with-php.html)
- [Using object composition for "has-a" relationships is not such a good idea](https://tonymarston.net/php-mysql/using-object-composition-for-has-a-relationships.html)
- [OO Design is incompatible with Database Design](https://tonymarston.net/php-mysql/oo-design-is-incompatible-with-db-design.html)
- [How NOT to Validate Data](https://tonymarston.net/php-mysql/how-not-to-validate-data.html)
- [Object Oriented Database Programming](https://tonymarston.net/php-mysql/object-oriented-database-programming.html)
- [Let's Make It More Complicated Than It Really Is Just To Prove How Clever We Are](https://tonymarston.net/php-mysql/lets-make-it-more-complicated-than-it-really-is.html)
- [What is the difference between Procedural and OO programming?](https://tonymarston.net/php-mysql/difference-between-procedural-and-oo-programming.html)
- [The difference between an interface and an abstract class](https://tonymarston.net/php-mysql/interface-and-abstract-class.html)
- [Having a separate class for each database table \*IS\* good OO](https://tonymarston.net/php-mysql/separate-class-for-each-table-is-good-oo.html)
- [The concept is OK but your implementation is not](https://tonymarston.net/php-mysql/concept-is-ok-but-implementation-is-not.html)
- [Re: Objects should be constructed in one go](https://tonymarston.net/php-mysql/objects-should-be-constructed-in-one-go.html)
- [Re: What's so great about OOP?](https://tonymarston.net/php-mysql/whats-so-great-about-oop.html)
- [To There and Back - but still in the wrong place](https://tonymarston.net/php-mysql/to-there-and-back-but-still-in-the-wrong-place.html)
- [Re: Exceptions and talking back to the user](https://tonymarston.net/php-mysql/exceptions-and-talking-back-to-the-user.html)
- [Are you achieving the aims of OOP?](https://tonymarston.net/php-mysql/are-you-achieving-the-aims-of-oop.html)
- [RE: Improving PHP's Object Ergonomics](https://tonymarston.net/php-mysql/improving-PHPs-object-ergonomics.html)
- [Pop Quiz on OOP](https://tonymarston.net/php-mysql/pop-quiz-on-oop.html)
- [RE: The purpose of inheritance is code reuse](https://tonymarston.net/php-mysql/the-purpose-of-inheritance-is-code-reuse.html)
- [Fat Model, Skinny Controller](https://tonymarston.net/php-mysql/fat-model-skinny-controller.html)
- [How to decouple business logic from UI logic](https://tonymarston.net/php-mysql/decouple-business-logic.html)
- [From Oop to Poop, from Excellent to Excrement](https://tonymarston.net/php-mysql/from-oop-to-poop.html)
- [The database is NOT just an implementation detail](https://tonymarston.net/php-mysql/db-is-not-just-an-implementation-detail.html)
- [The meaning of "abstraction"](https://tonymarston.net/php-mysql/abstraction.html)
- [Active Record: Getting it Right](https://tonymarston.net/php-mysql/active-record-getting-it-right.html)
- [How to Produce a Rich Domain Model with Active Record](https://tonymarston.net/php-mysql/active-record-rich-domain-model.html)
- [The difference between Tight and Loose Coupling](https://tonymarston.net/php-mysql/tight-vs-loose-coupling.html)
- [PHP's Type System](https://tonymarston.net/php-mysql/php-type-system.html)
- [Polymorphism in PHP](https://tonymarston.net/php-mysql/polymorphism-in-php.html)

These are reasons why I consider some ideas on how to do OOP "properly" to be complete rubbish:

- [Case Sensitive Software is EVIL](https://tonymarston.net/php-mysql/case-sensitive-software-is-evil.html)
- [Software Patents are EVIL](https://tonymarston.net/php-mysql/software-patents-are-evil.html)
- [Stored Procedures are EVIL](https://tonymarston.net/php-mysql/stored-procedures-are-evil.html)
- [Object Relational Mappers are EVIL](https://tonymarston.net/php-mysql/object-relational-mappers-are-evil.html)
- [Dependency Injection is EVIL](https://tonymarston.net/php-mysql/dependency-injection-is-evil.html)
- [Not-so-SOLID OO Principles](https://tonymarston.net/php-mysql/not-so-solid-oo-principles.html)
- [I fail to GRASP these principles](https://tonymarston.net/php-mysql/fail-to-grasp-these-principles.html)
- [Singletons are NOT evil](https://tonymarston.net/php-mysql/singletons-are-not-evil.html)
- [Getters and Setters are EVIL](https://tonymarston.net/php-mysql/getters-and-setters-are-evil.html)
- [Object Interfaces are EVIL](https://tonymarston.net/php-mysql/object-interfaces-are-evil.html)
- [Object Associations are EVIL](https://tonymarston.net/php-mysql/object-associations-are-evil.html)
- [Inheritance is NOT evil](https://tonymarston.net/php-mysql/inheritance-is-not-evil.html)
- [Namespaces are for numpties](https://tonymarston.net/php-mysql/namespaces-are-for-numpties.html)
- [The case against static typing in PHP](https://tonymarston.net/php-mysql/against-static-typing-in-php.html)
- [The case against overloading in PHP](https://tonymarston.net/php-mysql/against-overloading-in-php.html)
- [Attributes are atrocious](https://tonymarston.net/php-mysql/attributes-are-atrocious.html)
- [Autoloaders are abominations](https://tonymarston.net/php-mysql/autoloaders-are-abominations.html)
- [Composition is a procedural technique for code reuse](https://tonymarston.net/php-mysql/composition-is-a-procedural-technique-for-code-reuse.html)
- [Decoupling is delusional](https://tonymarston.net/php-mysql/decoupling-is-delusional.html)
- [Strict typing is for stick-in-the-muds](https://tonymarston.net/php-mysql/strict-typing-is-for-stick-in-the-muds.html)
- [Value objects are worthless](https://tonymarston.net/php-mysql/value-objects-are-worthless.html)
- [Programmer Productivity takes Precedence over Paradigm Purity](https://tonymarston.net/php-mysql/programmer-productivity-takes-precedence-over-paradigm-purity.html)
- [The Fallacy Of ReUse](https://tonymarston.net/php-mysql/the-fallacy-of-reuse.html)
- [RE: Back to Basics - Three or Four OOP Pillars?](https://tonymarston.net/php-mysql/three-or-four-oop-pillars.html)
- [DTOs are Diabolical](https://tonymarston.net/php-mysql/dtos-are-diabolical.html)
- [The true purpose of Dependency Injection](https://tonymarston.net/php-mysql/true-purpose-of-dependency-injection.html)
- [OOP practices which waste time](https://tonymarston.net/php-mysql/oo-practices-which-waste-time.html)

Here are my views on changes to the PHP language and Backwards Compatibility:

- [Breaking Backwards Compatibility is EVIL](https://tonymarston.net/php-mysql/breaking-bc-is-evil.html)
- [Please do not break our language](https://tonymarston.net/php-mysql/please-do-not-break-our-language.html)
- [BC break in 7.2 caused by undocumented and unauthorised change](https://tonymarston.net/php-mysql/bc-break-in-7.2.html)
- [Changing fundamental language behaviors](https://tonymarston.net/php-mysql/changing-fundamental-language-behaviors.html)
- [Is PHP too verbose?](https://tonymarston.net/php-mysql/is-php-too-verbose.html)
- [RE: Improving PHP's Object Ergonomics](https://tonymarston.net/php-mysql/improving-PHPs-object-ergonomics.html)
- [The PHP core developers are lazy, incompetent idiots](https://tonymarston.net/php-mysql/core-developers-are-idiots.html)
- [Is there a case for adding namespaces to PHP core?](https://tonymarston.net/php-mysql/namespaces-in-php-core.html)
- [The case against static typing in PHP](https://tonymarston.net/php-mysql/against-static-typing-in-php.html)
- [The case against function overloading in PHP](https://tonymarston.net/php-mysql/against-overloading-in-php.html)

The following are responses to criticisms of my methods:

- [What is/is not considered to be good OO programming](https://tonymarston.net/php-mysql/good-bad-oop.html)
- [In the world of OOP am I Hero or Heretic?](https://tonymarston.net/php-mysql/hero-or-heretic.html)
- [Your code is crap!](https://tonymarston.net/php-mysql/your-code-is-crap.html)
- [On not using the "right" standards](https://tonymarston.net/php-mysql/not-using-the-right-standards.html)
- [Your rules are RUBBISH!](https://tonymarston.net/php-mysql/your-rules-are-rubbish.html)
- [PHP Best Practices for Database Applications](https://tonymarston.net/php-mysql/best-practices-for-database-applications.html)
- [Response to personal attack on reddit.com](https://tonymarston.net/php-mysql/attack-on-reddit.com.html)

Here are some miscellaneous articles:

- [Component Design - Large and Complex vs. Small and Simple](https://tonymarston.net/uniface/largevssmall.html)
- [How to handle a Many-to-Many relationship with PHP and MySQL](https://tonymarston.net/php-mysql/many-to-many.html)
- [A class for validating and formatting dates](https://tonymarston.net/php-mysql/dateclass.html)
- [Customising the PHP error handler](https://tonymarston.net/php-mysql/errorhandler.html)
- [Technical Keys - Their Uses and Abuses](https://tonymarston.net/php-mysql/technicalkeys.html)
- [Pagination - what it is and how to do it](https://tonymarston.net/php-mysql/pagination.html)
- [The Relational Data Model, Normalisation and effective Database Design](https://tonymarston.net/php-mysql/database-design.html)
- [Development Standards - Limitation or Inspiration?](https://tonymarston.net/php-mysql/standards.html)
- [Saving PHP's Session data to a database](https://tonymarston.net/php-mysql/session-handler.html)
- [Are you a Code Monkey?](https://tonymarston.net/php-mysql/code-monkey.html)
- [The Singleton Design Pattern for PHP](https://tonymarston.net/php-mysql/singleton.html)
- [Working with a stateless protocol](https://tonymarston.net/php-mysql/stateless-protocol.html)
- [A flexible method of storing control data](https://tonymarston.net/php-mysql/control-data.html)
- [Web Site vs Web Application](https://tonymarston.net/php-mysql/web-site-vs-web-application.html)
- [Using Radicore components in a front-end website](https://tonymarston.net/php-mysql/radicore-front-end.html)
- [An end-to-end eCommerce solution requires more than a fancy website](https://tonymarston.net/php-mysql/an-end-to-end-ecommerce-solution-requires-more-than-a-fancy-website.html)
- [Database Design - are you Novice, Ninja or numpty?](https://tonymarston.net/php-mysql/database-design-ru-novice-ninja-or-numpty.html)
- [Why you should build your web application back-to-front](https://tonymarston.net/php-mysql/back-to-front.html)
- [Why PHP is not suitable for enterprise grade web applications](https://tonymarston.net/php-mysql/php-is-not-suitable-for-enterprise-applications.html)

* * *

## Amendment History

|     |     |
| --- | --- |
| 27 Jul 2024 | Restructured the entire document into the following headings:<br> <br>[Features of Domain Driven Design](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#table1) and [DDD Definitions](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#definitions)<br>[A standard design process](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#standard.design.process)<br>[Features of my personal approach](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#my.personal.approach)<br>[DDD "advice" which I ignore](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#advice.which.i.ignore)<br>[My implementation - Dealing with the differences](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#implementing.the.different)<br>[My implementation - Dealing with the similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#implementing.the.similar) |
| 16 May 2021 | Added [The dark side of object aggregation](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#object.aggregation) |
| 01 May 2021 | Added [Separate controller for each Use Cases](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#separate.controller) |
| 02 Mar 2019 | Included references to [The Template Method Pattern as a Framework](https://tonymarston.net/php-mysql/template-method-pattern-as-a-framework.html)<br>Added [What is a "domain"?](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#what.is.a.domain) |
| 24 Jan 2019 | Added [The biggest differences with the most similarities](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#differences.and.similarities) |
| 02 Dec 2018 | Added a [Comparison Matrix](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#comparison.matrix) to summarise the differences between the "approved" approach and my "heretical" approach. |
| 01 Oct 2018 | Added [Build a library of reusable components](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#build.a.library)<br>Added [Turning a library into a framework](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#library.then.framework)<br>Added [Optimise the User Interface](https://tonymarston.net/php-mysql/dont-do-domain-driven-design.html#optimise.the.ui)<br>Reworded the article to emphasize the fact that DDD starts with the domain-specific logic and adds in the domain-agnostic logic afterwards whereas my framework does the exact opposite. It is an implementation of the [Template Method pattern](https://tonymarston.net/php-mysql/radicore-hooks.html#template.method) which starts with domain-agnostic logic and allows domain-specific logic to be added in later via a pre-defined collection of "hook" methods. |

* * *

Disqus Recommendations

We were unable to load Disqus Recommendations. If you are a moderator please see our [troubleshooting guide](https://docs.disqus.com/help/83/).

❮

- 8 years ago
- 4 comments

Object Relational Mappers are EVIL

- 8 years ago
- 4 comments

What is the 3-Tier Architecture?

- 8 years ago
- 10 comments

Dependency Injection is Evil

- 8 years ago
- 2 comments

OO Design is incompatible with Database Design

- 7 years ago
- 8 comments

Response to personal attack on reddit.com

- 8 years ago
- 3 comments

Not-so-SOLID OO Principles

- 8 years ago
- 1 comment

How Radicore's Hook System Works

❯

tempest.services.disqus.com

# tempest.services.disqus.com is blocked

This page has been blocked by an extension

- Try disabling your extensions.

ERR\_BLOCKED\_BY\_CLIENT

Reload


This page has been blocked by an extension

![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)

Disqus Comments

We were unable to load Disqus. If you are a moderator please see our [troubleshooting guide](https://docs.disqus.com/help/83/).

G

Join the discussion…

﻿

Comment

###### Log in with

###### or sign up with Disqus  or pick a name

### Disqus is a discussion network

- Don't be a jerk or do anything illegal. Everything is easier that way.

[Read full terms and conditions](https://docs.disqus.com/kb/terms-and-policies/)

This comment platform is hosted by Disqus, Inc. I authorize Disqus and its affiliates to:

- Use, sell, and share my information to enable me to use its comment services and for marketing purposes, including cross-context behavioral advertising, as described in our [Terms of Service](https://help.disqus.com/customer/portal/articles/466260-terms-of-service) and [Privacy Policy](https://disqus.com/privacy-policy), including supplementing that information with other data about me, such as my browsing and location data.
- Contact me or enable others to contact me by email with offers for goods or services
- Process any sensitive personal information that I submit in a comment. See our [Privacy Policy](https://disqus.com/privacy-policy) for more information

Acknowledge I am 18 or older

- [Favorite this discussion](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Favorite this discussion")

  - ## Discussion Favorited!



    Favoriting means this is a discussion worth sharing. It gets shared to your followers' Disqus feeds, and gives the creator kudos!


     [Find More Discussions](https://disqus.com/home/?utm_source=disqus_embed&utm_content=recommend_btn)

[Share](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

  - Tweet this discussion
  - Share this discussion on Facebook
  - Share this discussion via email
  - Copy link to discussion

  - [Best](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
  - [Newest](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
  - [Oldest](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

- - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
  - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
  - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

    - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
    - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

S

I've been grappling with DDD specifically for some months now. I like a lot of what it does but where I struggle with now is the database aspect. Aggregates are nice and value objects can be useful. However, Sometimes I find it just a bit silly, yes grouping our entities makes more sense but sometimes it just leads to more confusion. What is a table and what isn't? It gets to the point where people make more entities than they should and duplicate their data storage. I think DDD inherently goes against database normalisation which isn't even necessarily bad, I just need a reason to do it as it makes my life with the ORM harder(among other things denormalisation does).

see more

  - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
    - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
    - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

      - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
      - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

T

The problem is that too many of today's young progammers are taught OO theory before learning database theory, and they try to design the software first and leave the database till last. Bending the database so that it fits the software is a big mistake. I was designing and building database applications for 20 years before I switched to an OO language, and when I was taught to start with a properly normalised database and then build the software to follow that structure I could see the benefits immediately. No matter what anyone tells me I will NEVER go back to doing it the old way.

I taught myself to program with objects by reading the bare bones descriptions of encapsulation, inheritance and polymorphism in the PHP manual, and because I know that when writing a database application you are dealing with objects in a database and not objects in the real world it was blindingly obvious to me that I should create a separate class for each table in the database. Regardless of what entity a table represents and what data it contains there are only four basic operations that can be performed on a table, and they are Create, Read, Update and Delete, and I put the code for these four operations in an abstract class which could then be inherited by every table class. Every experienced database programmer knows that as well as code that is common to every database table there needs to be code which is unique to individual tables, and I dealt with this by implementing the Template Method Pattern with the invariant/fixed methods in the abstract class and the variant/customisable methods in each subclass. I now have over 400 tables which inherit a lot of code from a single abstract class. I also have a mechanism built into my framework which will generate the table classes for me, so I never have to waste time in designing and building each table class by hand as each class follows a standard pattern.

My previous experience also taught me that once you have written a user transaction that does a particular thing with one database table it is quite common to want to do the same thing but with a different table, and OOP allowed me to implement this idea very efficiently. By having a Controller which is separate from the Model I could build Controllers which could do the same thing on ANY Model through the power of polymorphism. Over the years I have recognised about 50 different transaction patterns and I have built a Controller for each. So if I have 50 Controllers which can be used with any of my 400 database tables that results in 50 x 400 = 20,000 opportunities for polymorphism. The end result is that I can build user transactions at a much faster rate than anyone else, and each transaction has immediate access to the standard code within the abstract class. All the developer has to do is concentrate on the custom code which goes into the variant methods within the relevant subclass.

I don't waste my time struggling with with associations and aggregations as they are artificial constructs which are not efficient at all. In my opinion aggregations are also wrong because they violate the Single Responsibility Principle. Because each of my table classes contains an accurate representation of the structure of its associated database table I never have this problem called Object-Relational Impedence Mismatch, so I have no need for that abomination called an ORM.

OOP is supposed to be about maximising code reuse by the correct usage of encapsulation, inheritance and polymorphism, and as the amount of reusable code I have in my applications is more that I have seen in the examples put forward by others it would be fair to say that my implementation of OOP is "more correct" than others.

see more

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

- - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
  - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
  - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

    - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
    - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

R

Great post

see more

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

- - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
  - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
  - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

    - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
    - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

![Avatar for Django74](https://c.disquscdn.com/uploads/users/15176/9428/avatar92.jpg?1427849899)

Hi [Tony Marston](https://disqus.com/by/tony_marston/ "https://disqus.com/by/tony_marston/") I think you might be underemphasizing a big pillar of DDD, which is the ubiquitous language. At it's core the whole point of ddd is about not producing code, it's about producing a shared langauge and understanding and connection to the business and the tactical patterns all help to support that.

see more

  - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
    - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
    - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

      - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
      - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

T

The shared language to the business people is English. The people wanting an Order Processing system do not speak a different language from the people wanting an Inventory system or a Invoicing system. They may have different needs and different priorities, but they all speak English. It is the programmer's job to convert the requirements which are defined in a human-readable language into a machine-readable language.

Each database table may be different, but the way I handle each of those tables is exactly the same. This is why I use standard pre-written objects to handle all SQL queries. Each HTML document may be different, but the way I handle each of those documents is exactly the same. This is why I use standard pre-written objects to handle all HTML documents. The only difference between each of those systems is the business rules, which is why each table's concrete table class has its own unique set of hook methods

see more

    - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
      - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
      - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

        - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
        - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

![Avatar for Django74](https://c.disquscdn.com/uploads/users/15176/9428/avatar92.jpg?1427849899)

You're right that it is english, but it can divided into business speak and technical speak. The problem comes when we don't use the same terminology between the two minds of the business and the dev which is the exact purpose you're describing of programmers: to translate requirements to human readable lanaguage. The purpose of ubiquitous language is to align on common terminology, for example sign\_up, versus sign\_up\_for\_sass\_subscription. One communicates more about the mental model of the business in the code. Let me know if that makes sense, maybe not the best example. I think my point is that you can use human readable language, words typically used in a business setting as machine readable language. It's not exclusive. The agreed upon language, which can include business terms becomes computerized and subject to rigor when you include in the code. [Tony Marston](https://disqus.com/by/tony_marston/ "https://disqus.com/by/tony_marston/")

see more

      - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
        - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
        - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

          - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
          - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

T

What you call ubiquitous language I would call unambiguous language. If a business person tells me they want a sign-up screen the first question I ask is "Sign up to what?". The title of a function is not good enough, I always ask for precise details in order to avoid the possibility of wrong assumtions, either on my part or the business person's part. A human-readable instruction manual may be full of assumtions and prior knowledge, but a somuter-readable instruction manual (i.e. a computer progran) has to be specific down to the lowest level of detail. That level of detail has to be identified in the analysis phase as it cannot be left to the development phase.

DDD talks about having a separate model for each domain which would require a separate design process for each of those domains. I have a single design process which can be applied to any domain. This is because every database application has HTML documents at the front end, an SQL database at the back end, and software in the middle to handle the business rules. Most of those components require boilerplate code which can be provided from reusable sources, so it is only the business rules which are different.

see more

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

- - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
  - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
  - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

    - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
    - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

![Avatar for Miroslav Kravec](https://c.disquscdn.com/uploads/users/13040/1102/avatar92.jpg?1750262267)

Looks interesting,.. I've heard purist's opinions mentioning no coupling to any framework. Which goes a lot against yours example:

> A significant point to notice here is that I do NOT have a separate Controller for each Model which calls methods which are specific to that Model as this would require each Controller and Model to be hand-crafted and tightly coupled to each other.

You're coupling entities to a naming convention and class/method interface (insertRecord method, and parameters):

`$result = $dbobject->insertRecord($_POST);`

However, yours way seems much more reasonable, than purist way of not coupling code to any framework. As, controllers seem to have 99% of identical code (if not counting naming differences caused by different entity name). And, if controllers aren't same for basic operations, then it only adds more confusion.

see more

  - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
    - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
    - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

      - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
      - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

T

The idea that I am "coupling entities to a naming convention" is an incorrect usage of the term "coupling" in software. Coupling refers to the connection between two routines, and exists when routine A calls routine B. Routine B contains a method signature and a method body, and routine A calls that signature to execute that method body.

Coupling can either be classed as "loose" (which is good) or "tight" (which is bad). Tight coupling occurs when a change to routine B's signature creates a ripple effect which forces all the other routines which call that signature to be modified accordingly. In the example of a database application where you either add or remove a column to a table and this requires a change to either a method signature or the creation or deletion of a pair of getters and setters, this would be an example of tight coupling. Loose coupling is achieved when such a change does not cause this ripple effect. I achieve this in my framework by virtue of the fact that I never specify any column names of any method signature as all table data is passed around in an array called $fieldarray. Thus I can make any changes I like to the contents $fieldarray without causing this ripple effect.

Note also that loose coupling enables polymorphism while tight coupling prevents it. Polymorphism must exist before you can have dependency injection.

The notion that I should avoid coupling to a particular framework goes against the aims of OOP which is to increase code reuse and decrease maintenance by using encapsulation, inheritance and polymorphism. If you are not tied to a framework then you cannot make use of any reusable code provided by that framework, which must mean that you end up by having to write all that code yourself. In the case of my own RADICORE framework there are a large number of reusable components, which equates to a lot of code that you do not have to write yourself. This framework is based on the 3-Tier Architecture and the MVC design pattern, so it consists of Models, Views, Controllers and Data Access Objects.

1) There is a separate Model for each table in the application database.

2) There are 3 reusable Views, one each for HTML, CSV and PDF output.

3) There are 50 reusable Controllers, one for each of my Transaction Patterns.

4) There are 4 reusable DAOs, one for each supported DBMS - MySQL, PostgreSQL, Oracle and SQL Server.

Only the Model classes have to be built by the developer, but they can be generated automatically as they all inherit a large amount of standard code from an abstract table class. This abstract class contains all the public methods which may be used by the Controllers and Views. It should be noted that each of these public methods is an implementation of the Template Method Pattern as it performs its designated task by calling a series of child methods, some of which have invariant/fixed bodies and others which are variant/customisable. The invariant methods have their method bodies defined in the abstract class while the variant methods are defined with empty bodies which may therefore be overridden in the table subclass in order to provide custom processing for that table class.

Those programmers who follow a philosophy which reduces the amount of reusable code at their disposal are therefore NOT achieving the aims of OOP.

see more

    - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
      - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
      - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

        - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
        - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

![Avatar for Miroslav Kravec](https://c.disquscdn.com/uploads/users/13040/1102/avatar92.jpg?1750262267)

Just stumbled upon [https://www.dddheuristics.c...](https://www.dddheuristics.com/design-heuristics/keep-your-domain-model-decoupled-from-frameworks/: "https://www.dddheuristics.com/design-heuristics/keep-your-domain-model-decoupled-from-frameworks/:")

> When we implement domain models we want to seperate the domain model from other layers to keep the domain clean. We sometimes see the use of frameworks like ORM mapping in the domain model for easier use. This can lead to high coupling between the domain model and the database model, which we don’t want.

I was once made to believe, that it is good to not couple domain logic to any framework,... However, I now think it's quite a bullshit, because:

\- not achieved: the code is still coupled to language (Java, C#, golang, node,...),

\- not beneficial: swapping (replacing currently used) framework usually happens only on complete rewrite of an application,

\- higher development cost: extra boilerplate code to glue framework to framework-independent domain code,

\- higher development cost: write of lots of code from scratch, because of not using common basis provided by framework,

\- ... and, I believe, there is many more reasons,...

Also,.. different frameworks use different patterns and architecture, and therefore it might not even match design of core domain code,.. for example:

\- events and messaging system/design/pattern,

\- not having unit of work support, therefore making each aggregate modification separate transaction (supported by events/messaging).

I now start to believe, that the cost to write the same application in 5 frameworks would be less, than is the cost to write framework independent core, and then integrating it with 5 frameworks.

see more

      - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
        - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
        - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

          - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
          - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

T

In my humble opinion that article is barking up the wrong tree simply because the author does not understand the words he is using. For example:

\- An ORM is not a framework, it is a library. The differences are explained in [https://www.tonymarston.net...](https://www.tonymarston.net/php-mysql/what-is-a-framework.html "https://www.tonymarston.net/php-mysql/what-is-a-framework.html")

\- Separating the domain model from other layers means nothing more than creating separate Controllers, Views and Data Access objects. This is what the MVC and 3-Tier Architecture patterns are all about.

\- High coupling between the domain model and the database model implies that you have two models for each domain object (database table). This is an idea that only a junior programmer could invent. An experienced programmer would have one domain model for each table and one DAO for each DBMS.

\- To say that a domain model should not have any knowledge of the structure of the table which it represents is absolute nonsense as this goes against the whole idea of encapsulation.

This also shows serious misuse of the word “coupling”. As explained in [https://www.tonymarston.net...](https://www.tonymarston.net/php-mysql/oop-for-heretics.html#coupling "https://www.tonymarston.net/php-mysql/oop-for-heretics.html#coupling") this word should only be used to describe the interaction between two modules when one calls the other. To say that code is still coupled to a language implies that it can be decoupled, which is impossible. Code is “written in” a language, not “coupled to” a language.

I agree with you when you say that attempting to write domain code which is completely de-coupled from any framework, and can therefore be run under any framework without amendment, is an impossible dream. Different frameworks offer different facilities, and I have yet to see a framework which can match the facilities offered by RADICORE.

I have written a large enterprise application which contains over a dozen domains, and while the data handled by each domain is totally different there are two glaring similarities:

1) All the data is held in database tables, and every database developer will tell you that every table, regardless of its contents, follows a similar pattern and is subject to the same CRUD queries.

2) Every unit of work (use case) can be boiled down to performing one or more of the CRUD operations on one or more tables and displaying the result in an HTML form. This is another pattern, and I have identified 50 different patterns of structure and behaviour which are provided within my framework.

So while each domain has unique data, the way in which that data is stored, manipulated and displayed can be broken down into a series of patterns which can appear in any domain. A proper framework should therefore support these patterns, thus obviating the need for application developers to keep writing their own boilerplate code. The framework is therefore domain-independent as it can be used to develop any domain which is built around a database.

see more

        - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
          - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
          - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

            - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
            - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

![Avatar for Miroslav Kravec](https://c.disquscdn.com/uploads/users/13040/1102/avatar92.jpg?1750262267)

> This also shows serious misuse of the word “coupling”. As explained in [https://www.tonymarston.net](https://www.tonymarston.net/ "https://www.tonymarston.net")... this word should only be used to describe the interaction between two modules when one calls the other. To say that code is still coupled to a language implies that it can be decoupled, which is impossible. Code is “written in” a language, not “coupled to” a language.

Well, maybe,.. But, the same rules apply to all routines/modules, including standard library of every language, and type names, where there would be too ripple effect in every program, if stdlib/names are changed.

> I agree with you when you say that attempting to write domain code which is completely de-coupled from any framework, and can therefore be run under any framework without amendment, is an impossible dream. Different frameworks offer different facilities, and I have yet to see a framework which can match the facilities offered by RADICORE. ...

I perfectly agree. I have worked on software not based on any framework (except spring), and it was mess. I have worked on JIRA platform, where I have developed plugins, and it was much more cleaner and better structured (though, JIRA architecture has got some serious limitations,... but, for right projects it's great platform). And, as hobby, I have worked with Django. And,.. if there is a choice, **I would always choose to develop software coupled to some framework, which already provides great base implementing lots of domain-agnostic functionalities.** Besides many pros, being coupled to some domain-definition-interface (ie. yours abstract table class) makes whole software much more consistent, and better for cooperation within team....

see more

          - - [−](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Collapse")
            - [+](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Expand")
            - [Post menu](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default# "Post menu")

              - [Block User](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)
              - [Report](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

T

\> I would always choose to develop software coupled to some framework, which already provides great base implementing lots of domain-agnostic functionalities.

You should note that in the RADICORE framework all Controllers, Views and DAOs are domain-agnostic in that they do not refer to any domain objects. It is only the Model classes which contain domain-specific code.

see more

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Show more replies](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

[Load more comments](https://disqus.com/embed/comments/?base=default&f=tonymarston&t_u=https%3A%2F%2Ftonymarston.net%2Fphp-mysql%2Fdont-do-domain-driven-design.html&t_d=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&t_t=Why%20I%20don%27t%20do%20Domain%20Driven%20Design&s_o=default#)

tempest.services.disqus.com

# tempest.services.disqus.com is blocked

This page has been blocked by an extension

- Try disabling your extensions.

ERR\_BLOCKED\_BY\_CLIENT

Reload


This page has been blocked by an extension

![](<Base64-Image-Removed>)![](<Base64-Image-Removed>)

![counter](https://www.tonymarston.net/counter.php?noshow&page=/php-mysql/dont-do-domain-driven-design.html)