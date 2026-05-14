# 18xx.games — Developer Documentation

This documentation is for developers implementing new 18xx game titles on the 18xx.games platform. The primary path is a linear tutorial from "understanding the engine" through to "testing your finished game."

---

## Building a New Game

| Page | What it answers |
|------|-----------------|
| [Understanding the Engine](engine-concepts.html) | What are the core objects, why action replay, how does a move travel? |
| [Development Setup](getting-started.html) | How do I build and run the project locally and run the tests? |
| [Game Structure](game-implementation.html) | How do I add a new game title from scratch — files, constants, round configuration? |
| [Map Configuration](map.html) | How do I define the hex grid, terrain costs, location names, and tile supply? |
| [Corporations & Companies](entities.html) | What are all valid fields for CORPORATIONS and COMPANIES? |
| [Trains, Phases & Market](trains-phases.html) | How do TRAINS, PHASES, and MARKET control the economic arc? |
| [Rounds & Steps](round-step-system.html) | How does the engine process moves, and how do I write a custom Step? |
| [Abilities](abilities.html) | What ability types exist and when is each `when:` value active? |
| [Tile Reference](tiles.html) | What is the tile string DSL, and how do I inspect tiles while developing? |
| [Testing Your Game](testing.html) | How do I create a fixture, run it, and debug a failing replay? |
| [Coding Guidelines](coding-guidelines.html) | What patterns are required or forbidden in PRs? |

---

## Reference

| Page | What it answers |
|------|-----------------|
| [Game Engine Reference](game-engine.html) | Full Game::Base, Round, Step, and Action class reference with layer taxonomy |
| [Architecture Decision Records](adrs.html) | Why Opal instead of JS, why action replay, why game pinning? |

---

## Platform & Testing Setup

| Page | What it answers |
|------|-----------------|
| [Architecture Overview](architecture.html) | What components exist, how do they communicate, what is the tech stack? |
| [Configuration & Operations](konfiguration-betrieb.html) | Environment variables, Docker services, background jobs |
| [System Boundaries](systemgrenzen.html) | External service dependencies and failure behaviours |

---
*Version: 2026-05-08 — restructured around "Building a New Game" tutorial track.*
