# User Guide

18xx.games is a web platform for playing 18xx board games online. All game rules are implemented; you only need a browser and an account.

## Registration and Account

Create an account at `/signup` with a username, email, and password. Passwords are stored as Argon2 hashes — they are never held in plain text anywhere in the system. You can update your profile at any time under `/profile`.

## Finding and Creating Games

The home page shows three lists: open games (looking for players), active games, and finished games. Click *New Game* to choose a title from the dropdown — the list shows all titles at Beta status or above. Titles in Prealpha or Alpha are labelled accordingly; Alpha games may be archived without notice if a rule fix breaks the active game state.

## Game Modes

18xx.games supports three modes. In **async mode** (the default) players take turns whenever they have time; you receive an email notification when it is your turn. In **live mode** all players are online simultaneously and the browser updates in real time via Server-Sent Events. In **hotseat mode** all players share the same browser without any server involvement; the game exists only in local browser storage.

## Taking a Turn

The game window shows who is to act in the top-right area. The interface only allows legal actions — a greyed-out button or an unclickable tile means that action is not permitted at this moment. After every move a log entry appears and the next player is activated.

## Undo and Redo

Undo is available as long as the following player has not yet responded. Clicking *Undo* sends an `undo` action to the server, which rolls the game back one step; the next move then builds on the prior state.

## Pinned Games

When a developer introduces a breaking change, running games are *pinned* to an older JavaScript bundle. The game continues but displays a notice. Pinned games cannot be debugged and may be archived after a grace period.

## What's next

- Concrete step-by-step walkthroughs: [Use Cases](anwendungsfaelle.html)
- Solving common problems: [FAQ](faq.html)
- Look up game terms: [Glossary](glossary.html)

---
*Version: 2026-05-08 — derived from `assets/app/app.rb`, `routes/game.rb`, `routes/user.rb`.*
