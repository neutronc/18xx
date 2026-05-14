# Glossary

| Term | Meaning | Code source |
|------|---------|-------------|
| **Action** | A persisted move. Contains an entity reference, a type (`buy_shares`, `lay_tile`, `run_routes`, etc.), and type-specific arguments. Stored as JSON in the `actions` table and replayed on load. | [`lib/engine/action/base.rb:1`] |
| **Advisory Lock** | PostgreSQL mechanism that prevents two simultaneous requests from corrupting the same game session. Acquired per game ID. | [`routes/game.rb:56`] |
| **Auto-Action** | An Action the engine generates and processes automatically without player input — e.g. bankruptcy declaration or a forced train purchase. | [`lib/engine/game/base.rb:851-875`] |
| **Bank** | The central cash reserve for the session. When the bank breaks (cash ≤ 0), a `bank` end condition may trigger. | [`lib/engine/bank.rb:1`] |
| **Certificate Limit** | Maximum number of certificates a player may hold. Game-specific and player-count-dependent. | [`lib/engine/game/base.rb:200`] |
| **Company** | A private company auctioned at game start that grants special abilities. Not to be confused with Corporation. | [`lib/engine/company.rb:1`] |
| **Corporation** | The investable railway company. Has shares, trains, tokens, and a position on the stock market. | [`lib/engine/corporation.rb:1`] |
| **DEV_STAGE** | Development status of a game title: `:prealpha`, `:alpha`, `:beta`, `:production`. Affects warning messages and archival behaviour. | [`lib/engine/game/meta.rb:4`] |
| **Depot** | The supply of unsold trains. Corporations buy trains from the Depot. | [`lib/engine/depot.rb:1`] |
| **Dividend** | Revenue distributed per share after an Operating Round. Amount depends on revenue run and payout decision. | [`lib/engine/step/dividend.rb:1`] |
| **Ebuy** | Emergency Buy. A Corporation that has no train after operating must purchase one — potentially using the president's cash. | [`lib/engine/game/base.rb:282-330`] |
| **Entity** | Collective term for all acting objects: Player, Corporation, Minor, Company. | [`lib/engine/entity.rb:1`] |
| **Game::Base** | Base class for all game titles. Holds all engine objects and orchestrates the game flow. | [`lib/engine/game/base.rb:91`] |
| **Graph** | The routing graph the engine computes from the current track layout. Used for revenue calculation and route validation. | [`lib/engine/graph.rb:1`] |
| **Hex** | A hexagon on the game map. Contains a `Tile` with the track layout and cities. | [`lib/engine/hex.rb:1`] |
| **Hotseat** | Local multiplayer mode without a server. All players share the same browser. | [`assets/app/game_manager.rb:23-42`] |
| **MessageBus** | Redis-backed pub/sub channel for real-time updates. Pushes updated game state to all browser clients after every Action. | [`lib/bus.rb:1-30`] |
| **Minor** | A small subsidiary company in certain game titles. Can own shares and run routes. | [`lib/engine/minor.rb:1`] |
| **Opal** | Ruby-to-JavaScript transpiler. Allows the same engine codebase to run in the browser and on the server. | [`Gemfile:6`] |
| **Operating Round (OR)** | Round type in which Corporations act in turn order to lay track, place tokens, buy trains, and run routes. | [`lib/engine/round/operating.rb:1`] |
| **Par** | The issue price of a share at a corporation's IPO. Sets the starting position on the stock market. | [`lib/engine/share_price.rb:1`] |
| **Phase** | A game segment advanced by train purchases. Determines allowed track types, number of ORs, and which trains rust. | [`lib/engine/phase.rb:1`] |
| **Pin** | Mechanism that locks a running game to an older JavaScript bundle when a breaking change is introduced. | [`lib/engine/game/base.rb:688-694`] |
| **Round** | Container for a turn segment (SR, OR, Auction). Holds an ordered list of Steps and Entities. | [`lib/engine/round/base.rb:12`] |
| **Snabberb** | Minimal virtual-DOM framework for the Ruby/Opal frontend layer. | [`Gemfile:14`] |
| **Step** | Atomic decision unit within a Round. Declares ACTIONS and processes incoming Actions. | [`lib/engine/step/base.rb:8`] |
| **Stock Round (SR)** | Round type in which players buy and sell shares. | [`lib/engine/round/stock.rb:1`] |
| **StockMarket** | Two-dimensional price grid. Share buys/sells move a corporation's marker; special cells trigger game end or closure. | [`lib/engine/stock_market.rb:1`] |
| **Tile** | The track tile on a Hex. Contains paths, cities, and towns. | [`lib/engine/tile.rb:1`] |
| **Token** | A Corporation's presence marker on a city. Allows the city to be included in a route. | [`lib/engine/token.rb:1`] |
| **Train** | A Corporation's train. Has a reach (distance) and triggers phase transitions when purchased. | [`lib/engine/train.rb:1`] |

## What's next

- How the objects interact: [Mental Model](mental-model.html)
- A move in motion: [Core Flow](kernablauf.html)
- Technical engine reference: [Game Engine](game-engine.html)

---
*Version: 2026-05-08 — derived from `lib/engine/`, `models/`, `assets/app/`.*
