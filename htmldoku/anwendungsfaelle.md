# Use Cases

## 1. Create a New Game

Click *New Game* on the home page. Choose a game title from the dropdown. Set the player count and mode (async/live). Click *Create*. The game appears in the "Open Games" section and waits for other players to join.

## 2. Join a Game

Find the desired title in the open games list. Click the game card, then click *Join*. If you are the last missing player, the creator receives an email notification and the game starts automatically with the opening auction.

## 3. Take a Turn — Buying a Share

Open the game. When it is your turn the stock market area is active. Click a share of the Corporation you want to buy. The interface immediately shows whether the purchase is legal and what it costs. Confirm with the *Buy* button. A log entry confirms the purchase and the next player is activated.

## 4. Run Routes and Pay a Dividend

In an Operating Round: click *Run Routes*. The interface highlights available track segments. Select your trains and the cities they connect. Click *Run*. A dividend dialog appears: choose *Pay* (full payout) or *Withhold* (keep revenue). The share price moves accordingly.

## 5. Undo a Move

Click *Undo* as long as the following player has not yet acted. The system sends an `undo` action. The game is rolled back exactly one step; all affected players immediately see the updated board state.

## 6. Start a Hotseat Game

Click *New Game* and enable the *Hotseat* toggle. Choose title and player count. The game runs entirely in the browser with no server round-trip. All players share the same browser and pass the device after each turn. Hotseat games are not stored on the server.

## 7. Import a Production Game for Local Testing

Developers and testers can import a running production game into their local environment. Start `docker compose exec rack irb`, load `scripts/import_game.rb`, and call `import_game(<id>)`. The imported game is immediately available at `/game/<id>`; all passwords are reset to `password`.

## What's next

- Solving common problems: [FAQ](faq.html)
- Overview of all features: [User Guide](userguide.html)
- Developer setup: [Getting Started](getting-started.html)

---
*Version: 2026-05-08 — derived from `routes/game.rb`, `assets/app/game_manager.rb`, `scripts/import_game.rb`.*
