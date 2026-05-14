# FAQ

## Moves and Actions

**Why are some buttons greyed out?**
The interface only allows actions that the active Step currently permits. A greyed-out button means the action is not legal for your current turn — either it is not your turn, or the game rules forbid it at this moment.

**I see a "Game out of sync" error. What should I do?**
Your browser has a stale game state. Reload the page (`F5`). The browser will fetch the current state from the server.

**Can I undo a move that another player has already seen?**
No. Undo is only available while the following player has not yet responded. Once the next player has submitted an action, the previous move is locked.

**Why does a move sometimes appear with a bullet (•) in the log?**
The bullet marks moves executed on your behalf in *Master Mode* by another player (e.g. the game creator) [`lib/engine/game/base.rb:882-885`].

## Game Management

**How long is a finished game stored?**
Finished games are automatically archived one year after they were created. Archived games lose their action history; only metadata is retained [`queue.rb:35-48`].

**What happens to active games that go idle?**
Active games are automatically archived after 90 days without activity [`queue.rb:38-41`].

**What is a "pinned" game?**
When a breaking change is introduced to the codebase, running games are bound to an older JavaScript bundle. The game continues, but bug reports are not accepted; the game may be archived after 7 days (for Beta titles).

## Game Titles and Development Status

**What do Alpha / Beta / Production mean for a title?**
Production means a fully tested rule implementation. Beta means the implementation may still contain bugs; active games can be pinned when fixes are applied. Alpha titles are experimental; games are archived without notice if a fix breaks the active game state.

**I found a rule bug. Where do I report it?**
Use the GitHub issue tracker at [github.com/tobymao/18xx/issues](https://github.com/tobymao/18xx/issues). The issue label matches the game title (e.g. `1830`). For discussion, join the 18xx Slack `#18xxgamesdev` channel.

## What's next

- Starting and joining a game: [Use Cases](anwendungsfaelle.html)
- Full feature overview: [User Guide](userguide.html)

---
*Version: 2026-05-08 — derived from `lib/engine/game/base.rb`, `queue.rb`, `routes/game.rb`.*
