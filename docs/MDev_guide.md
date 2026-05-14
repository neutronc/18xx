# 18xx Engine Developer Guide  
*Cheat Sheet for Core Architecture and Game Extensions*

---

## **1. Core Architecture Overview**

The 18xx engine uses an **object-oriented pattern** split into four main layers:

### **Game::Base**
- **Role:** Common logic for all games, extended by individual titles.
- **Key Methods:**
  ```ruby
  setup                # Initializes bank, players, corporations
  operating_round(num) # Starts an OR set
  stock_round          # Initiates a stock round
  route_trains(entity) # Resolves train runs and revenue
  buy_train(entity, train, price) # Handles train purchase
  merge(entities)      # Handles corporation mergers (overridden by games)
  ```
- **Usage Example:**
  ```ruby
  game = Engine::Game::G18OE.new(players)
  round = game.operating_round(1)
  action = Engine::Action::BuyTrain.new(entity, train, price: 300)
  round.process_action(action)
  ```

---

### **Round::Base**
- **Responsible for:** Executing ordered game steps per round.
- **Patterns:**
  ```ruby
  steps.each(&:actions)       # Collect allowed actions for entity
  round.process_action(action) # Delegates to the active Step
  ```

---

### **Step::* Modules**
Defines **atomic phases** of gameplay like buying trains or issuing shares.

- **Examples:**
  - `Step::BuyTrain`
  - `Step::SellShares`
  - `Step::Merge`
  - `Step::Route`
- **Common API:**
  ```ruby
  actions(entity)           # Returns allowed actions
  process_buy_train(action) # Executes train purchase
  process_merge(action)     # Executes merger logic
  ```

---

### **Action::* Classes**
Represent player actions flowing through rounds and steps.

- **Common Patterns:**
  ```ruby
  Engine::Action::BuyTrain.new(entity, train, price)
  Engine::Action::SellShares.new(entity, shares)
  
  action.to_h       # Serialize to hash
  Action.from_h(h)  # Deserialize
  ```

---

## **2. Call Sequence**

```text
Game.new(players)
  -> setup()
  -> stock_round()
  -> operating_round()
       -> each step
          actions(entity)
          process_action(action)
```

---

## **3. Advanced Mechanics from Other Titles**

The following **special rules** exist in variants and serve as extension hooks:

✔ **National Companies**  
- Used in 1844/1854 for creating large “state-owned” systems later in play.
- Implemented via:
  - `Step::Merge` logic for token, train, share migration.
  - Extended `Game#merge` for payout.

✔ **Mergers (1828, 1841)**  
- Complex stock conversions and asset transfers.
- Engine Pattern:
  ```ruby
  process_merge(action)
  merge_corporations(old_corp, new_corp)
  ```

✔ **Combining Trains (1862)**  
- Mechanics allow two smaller trains → combined larger train.
- Custom method:
  ```ruby
  combine_trains(entity, train_a, train_b)
  ```

✔ **Ferries & Ports (18MEX, 18Scandinavian)**  
- Add tile or token bonuses connected to sea or port hexes.
- Often realized via:
  - `Step::Assign` for ferry tokens.
  - `hex.assignments` for bonus handling.

✔ **Sea Zones & Province Crossing (18OE / 18C2C)**  
- Adds cost/barriers to routes:
  - Track-laying and route validators check **zone crossing costs**.
  - Example: `hex.province` or `hex.sea_zone` attributes.

---

## **4. Useful Test Patterns**

Specs often demonstrate real usage patterns:

```ruby
expect(game.round.active_step.actions(entity))
```

Typical sequence:

```ruby
round = game.operating_round(1)
buy_action = Engine::Action::BuyTrain.new(corp, train, price: 200)
round.process_action(buy_action)

merge_action = Engine::Action::Merge.new(corp_a, corp_b)
round.process_action(merge_action)
```

---

## **5. Developer Extension Hooks**

When adding new features:
- Add relevant `Step` for new phase/action.
- Extend `Game::merge`, `Game::route_trains` if needed.
- Wire allowed actions in `actions(entity)`.

---

## **6. Suggested Directory for This Guide**
Create the file:
```
docs/MDev_guide.md
```
and include this content. It will help all developers building variants like `18OE`.

---

> **Pro Tip:** Start by scanning `lib/engine/game/g_18_*` for similar mechanics.  
Examples:
- `g_1862` → train combination.
- `g_18_mex` → ports & ferry logic.
- `g_1828` → mergers and special stock handling.
