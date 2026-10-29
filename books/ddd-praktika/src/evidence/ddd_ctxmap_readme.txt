# README.md at master · ddd-crew/context-mapping
URL: https://github.com/ddd-crew/context-mapping/blob/master/README.md

# File: ddd-crew/context-mapping/README.md

- Repository: ddd-crew/context-mapping | 2K stars
- Branch: master

```md
# Context Mapping

Context Maps describe the contact between bounded contexts and teams with a collection of patterns. There are nine context map patterns and three different team relationships. The context map patterns describe a variety of perspectives like service provisioning, model propagation or governance aspects. This diversity of perspectives enables you to get a holistic overview of team and bounded context relationships.

Context Maps can be used to analyze existing systems or application landscapes, but they are also suitable for upfront design considerations. However, we have realized that many folks struggle to get started with the context mapping patterns based on the definitions in the existing DDD books. This GitHub repository aims to give you some help with context maps with a cheat sheet and a starter kit for Miro.

## Overview of the context map team relationships and patterns

### Team Relationships

#### Mutually Dependent

<img src="resources/mutual-dependent.jpg" alt="Mutually Dependent" width=300/>

Two teams or bounded contexts are mutually dependent when their software artifacts or systems need to be delivered together to be successful and work. You will often see a close, reciprocal link between data, functionality and capabilities of these teams. Those teams also need a lot of communication between each other in order to coordinate their efforts (see Partnership pattern).

#### Upstream Downstream

<img src="resources/upstream-downstream.jpg" alt="Upstream / Downstream" width=300/>

Actions of an upstream team will have an effect on the downstream team, but actions of the downstream do not have a significant impact on the upstream team. "The upstream team may succeed independently of the fate of the downstream team" (Quote from the [DDD Reference by Eric Evans](https://www.domainlanguage.com/ddd/reference/)).

#### Free

<img src="resources/free.jpg" alt="Free" width=300/>

A Bounded Context or a team that works in it is free if changes in other Bounded Contexts do not influence its success or failure. There is, therefore, no organizational or technical link of any kind between these teams.

### Context Map Patterns

Most publications in the Domain-Driven Design community currently describe nine context mapping patterns. 

#### Open-host Service

<img src="resources/ohs.jpg" alt="Open-host Service" height=150/>

"A protocol that gives access to your subsystem as a set of services. Open the protocol so that all who need to integrate with you can use it. Enhance and expand the protocol to handle new integration requirements, except when a single team has idiosyncratic needs. Then, use a one-off translator to augment the protocol for that special case so that the shared protocol can stay simple and coherent." ([Source: DDD Reference by Eric Evans](https://www.domainlanguage.com/ddd/reference/))

The team