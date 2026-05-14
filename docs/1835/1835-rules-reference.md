# 1835 Rules Reference

Source: `docs/1835/1835-Spielregeln.pdf`, extracted with `pypdf`.

This is a structured reference based on the German rulebook. It is intended as a lookup document, not a replacement for the original layout or examples.

## 1. Objective

- The winner is the player with the greatest total wealth at game end.
- Total wealth is:
  - personal cash
  - plus the market value of held shares
- Company treasury and trains do not count toward final scoring.

## 2. Core Game Structure

- The game alternates between:
  - `AR` = Aktienrunde (stock round)
  - `OR` = Operationsrunde (operating round)
- In stock rounds, players buy and sell papers.
- In operating rounds, privates pay income and companies operate.

### 2.1 Papers

`Papiere` include:

- private railways
- pre-Prussian company charters
- corporation shares

Only corporation shares are shares in the strict sense.

### 2.2 Number of Operating Rounds

- At the start of the game, there is 1 OR between ARs.
- After the first `3` train is bought, then after the next AR there are 2 ORs between ARs.
- After the first `5` train is bought, then after the next AR there are 3 ORs between ARs.

## 3. Setup

### 3.1 Seating and Priority

- Determine seating order randomly.
- Seat players clockwise in number order.
- Player `1` gets the wooden locomotive marker.
- The wooden locomotive identifies the start player for the current or next stock round.

### 3.2 Starting Cash and Certificate Limit

| Players | Starting Cash | Certificate Limit |
| --- | ---: | ---: |
| 3 | 600 M | 19 |
| 4 | 475 M | 15 |
| 5 | 390 M | 12 |
| 6 | 340 M | 11 |
| 7 | 310 M | 9 |

### 3.3 Start Package Layout

Lay out the start package in four rows:

- Row 1:
  - `Nürnberg-Fürth`
- Row 2:
  - `Bergisch-Märkische (1)`
  - `Leipzig-Dresdner`
  - `Berlin-Potsdamer (2)`
- Row 3:
  - `Magdeburger (3)`
  - `Köln-Mindener (4)`
  - `Bayern` director paper
  - `Braunschweigische`
- Row 4:
  - `Hannoversche`
  - `Berlin-Stettiner (5)`
  - `Altona-Kiel (6)`
  - `Ostbayern`
  - `Pfalzbahnen`

### 3.4 Free Shares in the Start Package

- Each blue private has a free Bavaria share tucked under it.
- `Leipzig-Dresdner` has the Saxony director share tucked under it.
- Remaining shares go to `Nichtverkaufte Aktien`.

### 3.5 Trains at Setup

- All `2` trains begin in `Verfügbare Züge`.
- The rest are stacked in this order:
  - `2+2`
  - `3`
  - `3+3`
  - `4`
  - `4+4`
  - `5`
  - `5+5`
  - `6`
  - `6+6`

## 4. Company Types

There are three distinct company types:

- `Privatbahnen` (private railways)
- `Vorpreußische Gesellschaften` (pre-Prussian companies)
- `Aktiengesellschaften` (corporations)

## 5. Time Structure and Company Availability

### 5.1 Before Share Trading

- No treasury shares may be bought from `Nichtverkaufte Aktien` until the entire start package is sold.

### 5.2 Corporation Availability by Group

Corporations become available in groups:

1. `Bayern`, `Sachsen`
2. `Baden`, `Württemberg`, `Hessen`, plus special `Preußen`
3. `Mecklenburg-Schwerin`, `Oldenburg`

Rules:

- A later group cannot be bought until all shares of the current group have been sold from treasury.
- Within a group, the next corporation becomes available only after at least `50%` of the previous corporation has been sold.
- The first share made available is normally a `20%` director share, except for Bavaria and Prussia special cases.

### 5.3 Special Availability of Prussia

- The four freely purchasable `10%` Prussian shares become available once the Baden director share has been bought.
- These shares do not by themselves open Prussia.
- Until Prussia opens, these shares are only options without operating effect.

## 6. Stock Rounds

### 6.1 Start and Turn Order

- The player with the wooden locomotive starts the stock round.
- Play proceeds clockwise.

### 6.2 End of a Stock Round

- A stock round ends when every player, in sequence, declines to buy.
- Sales do not prevent the round from ending.
- The player to the left of the last player who bought gets the wooden locomotive for the next stock round.
- If nobody buys anything in the entire round, the wooden locomotive stays where it is.

### 6.3 Action Structure in a Stock Round

On a player turn:

- at most one buy is allowed
- any number of sales are allowed
- sales and the buy may be performed in either order

If a player passes:

- they do nothing on that turn
- they may still act later in the same stock round if it has not ended

## 7. Start Package Purchase Rules

- While the start package is not fully sold, players may only:
  - buy one available paper from the start package
  - or pass
- Normally, a player may buy only from the top row.
- If only one paper remains in the top row, the player may instead buy the leftmost paper in the row directly below.
- After the start package is fully sold, Bavaria and Saxony treasury shares become available.

If the stock round ends before the start package is fully sold:

- only companies already in operation will act in the following ORs

## Clemens Variant (Optional)

Dirk Clemens proposed an alternate opening that was documented by Bill Stoll (“Game Drei/Fünf/Sechs”) and later summarized
by Gregor Zeitlinger and Steve Thomas on the 18xx mailing list. When the Clemens Variant is enabled:

- The entire start packet is open; there are no row restrictions.
- Turn order for buying certificates is counter-clockwise for the first lap (e.g., `4-3-2-1`), then switches to the
  normal clockwise order for the remainder of the auction (`1-2-3-4-…`). The last player in seating order acts first and
  the first player effectively gets two consecutive buys at the lap transition.
- Minors that are purchased from the start packet float as usual but may not operate until Bayern (ByE) floats.

Some Stoll tables floated Bayern immediately when its director share was bought; this implementation keeps the standard
float condition but still delays minor operations as described above.

## 8. Buying Shares

### 8.1 New Shares

- A new share may be bought from the top of a treasury stack in `Nichtverkaufte Aktien`.
- The buyer pays the printed issue price.
- Before the corporation has opened, payment goes to the bank.
- After the corporation has already opened and operated, payment goes directly into company treasury.

### 8.2 Pool Shares

- A share in the bank pool may be bought at the current market value.
- Payment goes to the bank.

### 8.3 Nationalization (`Verstaatlichung`)

- If a player owns at least `55%` of a corporation, instead of a normal buy they may forcibly buy one share of that corporation directly from another player.
- The target player cannot refuse.
- Price is `1.5x` current market value.
- The buyer chooses which share certificate is taken.

Example from the rules:

- A `20%` share at market value `80` costs `240` to nationalize.

### 8.4 Rebuy Restriction

- If you sold shares of a corporation earlier in the current stock round, you may not buy or nationalize that corporation again until the next stock round.

## 9. Certificate Limit

The certificate limit counts:

- private railways
- pre-Prussian company charters
- shares

Rules:

- A player may own any percentage of a corporation, subject only to the certificate limit.
- If a player exceeds the limit, for example due to losing a presidency, they must sell down when next able to act.
- For each corporation in which a player owns at least `80%`, their certificate limit increases by `1`.
- A player at the limit with `60%` or `70%` cannot buy the share that would take them to `80%` unless they first free a certificate slot.

## 10. Selling Shares

### 10.1 General Rules

- Only shares may be sold.
- Private railways and pre-Prussian charters can never be sold.
- Sold shares go to the bank pool.
- The seller receives the current market value before any sale-induced price drop.

### 10.2 Sale Action

- One sale action may include any number of shares of one corporation.
- A player may make multiple separate sale actions on their turn.

### 10.3 Sale Restrictions

- No more than `50%` of a corporation may be in the bank pool, except in bankruptcy cases.
- Shares cannot be sold before or in the stock round in which a normal corporation opens. The corporation must have operated at least once before its shares become sellable.
- Exception: Prussian shares are tradeable immediately once Prussia opens.
- The director share may be sold only if another player can legally assume the presidency.
  - `20%` is needed for normal corporations
  - `10%` is enough for Prussia

### 10.4 Price Movement from Sales

- Each separate sale action drops that corporation’s stock marker by one row.
- It does not matter whether the action sold one share or several.
- Price movement happens immediately after the action.
- If the marker is already at the bottom of its column, it does not move further.

### 10.5 End-of-Stock-Round Upward Movement

At the end of a stock round:

- if an operating corporation has no shares in the bank pool and no unsold treasury shares remaining in `Nichtverkaufte Aktien`
- then its stock marker rises one row

If already at the top edge, it does not move further.

## 11. Opening Normal Corporations

A normal corporation opens when at least `50%` of its shares have been sold for the first time.

When it opens:

- the director receives the company charter and all company markers
- one marker goes to the company’s starting stock price
- one marker goes to the home station
- the company receives treasury equal to the percentage already sold
- this includes shares distributed earlier with privates

After opening:

- later treasury share sales pay into company treasury, not to the bank
- this continues until full capitalization has been paid in

## 12. Corporations

### 12.1 Corporation Data

| Corporation | Home | Total Capitalization | Station Markers |
| --- | --- | ---: | ---: |
| Bayern | München | 920 M | 5 |
| Sachsen | Leipzig | 880 M | 3 |
| Baden | Mannheim-Ludwigshafen | 840 M | 2 |
| Württemberg | Stuttgart | 840 M | 2 |
| Hessen | Frankfurt | 840 M | 2 |
| Mecklenburg-Schwerin | Schwerin | 800 M | 2 |
| Oldenburg | Oldenburg | 800 M | 2 |
| Preußen | Berlin | 616 M | 1 |

### 12.2 Presidency

- The holder of the director share is president unless another player owns a higher percentage.
- If another player owns more percentage than the current president, the presidency changes immediately.
- Ties do not change the presidency.
- If several players tie for the highest percentage above the old president, the next such player to the left of the old president becomes president.

### 12.3 Presidency Transfer

When the presidency changes:

- the old president gives the director share to the new president
- the old president receives an equal percentage back in shares of their choice
- the new president immediately takes the charter, trains, and treasury

### 12.4 Voluntary Presidency Dump

- A president may give up office only by legally selling enough shares to do so.
- Another player must already hold a president-eligible stake.
- The bank pool limit and other normal sale rules still apply.

## 13. Private Railways

### 13.1 List of Private Railways

- `Nürnberg-Fürth` (blue)
- `Leipzig-Dresdner Bahn` (red)
- `Braunschweigische Bahn` (black)
- `Hannoversche Bahn` (black)
- `Ostbayerische Bahn` (blue)
- `Pfalzbahnen` (blue)

### 13.2 General Rules for Privates

- Privates are acquired only from the start package.
- They are never sellable.
- They do not lay track.
- They do not place stations as independent companies.
- They do not own or run trains.
- They pay fixed income from the bank to their owner at the start of every OR.
- A player may not voluntarily close a private.
- If not closed by its special power, a private closes when brown phase begins, that is when the first `5` train is bought.

### 13.3 Special Powers of Privates

#### 13.3.1 Nürnberg-Fürth

- If the owner is acting as president of a corporation in an OR, they may place a free station marker in the `Nürnberg-Fürth` hex.
- No connection to that corporation’s network is required.
- This station is additional to any normal station placement.
- The private closes when this power is used.

#### 13.3.2 Ostbayern

- If the owner is acting as president of a corporation in an OR, they may lay a free tile in either of two specified hexes southeast of `Nürnberg-Fürth`.
- No existing network connection is required.
- This lay is additional to the corporation’s normal build action.
- In a later OR they may build the other hex as well, if they still own the private.
- `Ostbayern` closes as soon as both hexes have been built, by anyone.

#### 13.3.3 Pfalzbahnen

The owner has two special rights:

- They may build `Mannheim-Ludwigshafen` for free and in addition to the corporation’s normal build action, without needing connection.
- If `Baden` is already open, they may place a free station there for their corporation, in addition to a normal station placement.

Notes:

- This station power may not interfere with Baden’s home placement.
- Both special actions may occur in the same OR, possibly by different corporations.
- `Pfalzbahnen` closes when the free station power is used.

#### 13.3.4 Leipzig-Dresdner

- The buyer gets the `20%` Saxony director share for free.
- `Leipzig-Dresdner` closes when Saxony buys its first train.

#### 13.3.5 Braunschweigische and Hannoversche

- Once Prussia has opened, each may be converted into a `10%` Prussian share.
- The private closes when converted.
- When brown phase begins, they must convert.

## 14. Pre-Prussian Companies

### 14.1 List

| No. | Company | Home Station | Starting Treasury |
| --- | --- | --- | ---: |
| 1 | Bergisch-Märkische | Düsseldorf | 80 M |
| 2 | Berlin-Potsdamer | Berlin | 170 M |
| 3 | Magdeburger | Magdeburg | 80 M |
| 4 | Köln-Mindener | Dortmund | 160 M |
| 5 | Berlin-Stettiner | Berlin | 80 M |
| 6 | Altona-Kiel | Hamburg | 80 M |

### 14.2 General Rules

- A pre-Prussian company is owned by a single player.
- It is not a private and not a corporation.
- It operates like a corporation during ORs.
- It acts before corporations, always in number order from `(1)` to `(6)`.
- It may own trains, but is not required to own one.
- It may never place stations beyond its home station.
- It has no stock price.
- Its purchase price becomes its treasury.
- Its owner receives `50%` of its route revenue each OR.
- The other `50%` is kept as company treasury.
- It is never sellable.
- Later it converts into Prussian shares.

## 15. Opening and Converting into Prussia

Prussia opens by special rules.

### 15.1 Trigger Window

- Prussia may open once at least one `4` train has been bought.
- It may open during an OR or at the beginning of a later OR or AR.
- The owner of `Berlin-Potsdamer (2)` largely controls the timing.
- Prussia must be opened by the time the first `4+4` train is bought.

### 15.2 Opening Procedure

To open Prussia:

- the owner of `Berlin-Potsdamer` returns that charter to the bank
- they receive the Prussian director share
- Prussia’s stock marker is placed at `154`
- Prussia receives:
  - treasury for previously purchased Prussian treasury shares at `154` each
  - Berlin-Potsdamer’s treasury
  - Berlin-Potsdamer’s trains

### 15.3 Immediate Conversions into Prussia

Then, beginning with the new Prussian president and proceeding around the table:

- players are asked whether they want to convert other pre-Prussian companies
- and whether they want to convert the black privates `Braunschweigische` and `Hannoversche`

If they choose to convert:

- they return the paper
- they receive the corresponding Prussian exchange share from the exchange stack

### 15.4 Effects of Converting a Pre-Prussian Company

When a pre-Prussian company converts:

- its remaining treasury goes to Prussia
- its trains go to Prussia
- its home station is replaced by a Prussian station
- if Prussia already has a station there, the old station is simply removed

### 15.5 No Double Benefit Rule

- A player may not receive double benefit or double income from the same paper in a single OR due to conversion timing.

### 15.6 Later Conversions

- If a company or black private is not converted immediately, its owner may choose to convert it later.
- At the start of later ORs or ARs, players are asked once around the table, beginning with the start player.
- Presidency changes caused by conversion happen immediately, before resolving excess-train effects.

## 16. Operating Round Order

Each OR proceeds in this order:

1. If Prussia is already open, ask players whether they want to convert eligible pre-Prussian papers or black privates into Prussia.
2. Pay private railway income.
3. Operate pre-Prussian companies `(1)` through `(6)`.
4. Operate all open corporations by descending stock price.

Tie breakers for corporations:

- Higher market value acts first.
- If two stock markers share the same space, the marker on top acts first.
- If equal values appear in different positions, the marker farther right acts first.

## 17. Structure of a Company Operating Turn

Every operating company acts in this exact order:

1. `Bauen` = lay or upgrade track
2. `Pöppeln` = place a station
3. `Fahren` = run trains, calculate revenue, pay or withhold
4. `Kaufen` = buy trains

Important:

- A company may skip building or station placement.
- Train buying is always last.
- A train bought this turn cannot run this turn.
- A normal corporation cannot earn revenue in the same turn it opens, unless it is Prussia and already inherited trains.

## 18. Track Rules

### 18.1 General

- Tiles are laid on the hex grid.
- Brown map hexes with printed track are never tiled over.
- Red offboard hexes cannot receive tiles or stations.
- Yellow printed map hexes may be upgraded in green phase.
- Green printed map hexes may be upgraded in brown phase.

### 18.2 Number of Tile Lays

- In yellow phase:
  - each open corporation may lay `2` yellow tiles
  - each pre-Prussian company may lay `1`
- From green phase onward:
  - each corporation may lay or upgrade `1` tile
  - each pre-Prussian company may lay or upgrade `1`

Private special builds are additional.

### 18.3 Connection Requirement

A tile lay or upgrade must:

- extend a theoretically traversable route of the operating company
- or occur in a hex already containing one of that company’s station markers

### 18.4 Terrain Costs

- First-time building in mountain or river hexes costs the printed amount.
- The cost is paid from company treasury before laying the tile.
- If the company cannot pay, it cannot build there.

### 18.5 City and Town Placement Basics

- Empty terrain gets non-city track tiles.
- Single small town gets a yellow tile with one town stop valued at `10`.
- Double small-town hexes get yellow tiles with two town stops.
- Normal city hexes get single-city tiles valued at `20`.
- `Y` cities use `Y` tiles valued at `30`.
- `XX` tiles are only for double-city hexes such as `Mannheim-Ludwigshafen`, `Wiesbaden-Mainz`, and `Duisburg-Essen`.
- `B` tiles can only be used in `Berlin`.
- `H` tiles can only be used in `Hamburg`.

### 18.6 Upgrades

- Yellow may upgrade to green.
- Green may upgrade to brown.
- Existing track connections may not be broken.
- City type may not change during an upgrade.
- Some tiles are not upgradable further; use the promotion tables.
- Exchanged tiles return to the supply.

### 18.7 Placement Restrictions

- A tile may not be oriented so that track runs into water or off the map, except toward legal offboard arrows.
- Track may only enter brown printed hexes where a printed track connection exists.
- Track may not run into the thick blue barrier west of Hamburg.
- A new tile does not have to connect all of its exits to neighboring track.
- At least one track segment of a newly laid tile must lie on a route containing one of the operating company’s stations.

## 19. Station Rules

### 19.1 General

- Each company gets a free home station when it opens.
- A company may have at most one station marker in a hex, even if the hex has multiple cities.
- Full cities block passage by companies that do not already occupy them.

### 19.2 Why Stations Matter

- A company must have one of its own stations somewhere on any route it builds.
- A company must have one of its own stations somewhere on any route it runs.

### 19.3 Cost of New Stations

- New stations cost `20 M` times the minimum number of hexes from the company’s home hex to the target hex.
- Do not count the home hex itself.
- Cost is paid from company treasury before placement.

Example from the rules:

- Bavaria placing a station in Dresden costs `160 M`.
- Bavaria placing a station in Leipzig costs `140 M`.

### 19.4 Placement Limits

- A corporation may place at most one normal station per OR.
- Home station placement does not count against this limit.
- Stations placed through private abilities do not count against this limit.
- Pre-Prussian companies never place additional stations.

### 19.5 Route Requirement for Station Placement

- A station may be placed only if there is a traversable route of any length to another station of the same company.
- The route must not be blocked by foreign stations.
- Exception: special private powers may ignore this.

### 19.6 Reservation for Future Home Stations

- In a city that will later be the home of an unopened company, a foreign company may place a station only if at least one station slot remains available for the future home station.

### 19.7 Baden Special Case

- Baden’s home is in `Mannheim-Ludwigshafen`.
- If that hex is still unbuilt when Baden opens, Baden chooses the exact city only when the hex is built.
- Before Baden has placed its home station there, no other station may be placed in that hex, not even via `Pfalzbahnen`.
- If the hex is built after Baden is already open, the Baden president must immediately choose which city is Baden’s home.

### 19.8 Pre-Prussian Home Stations on Conversion

- A pre-Prussian home station becomes a Prussian station on conversion.
- If Prussia already has a station in that hex, the old station is removed and the space becomes free.

## 20. Running Trains

### 20.1 General

- Each train may run once per OR.
- A route must contain at least two different stations.
- Cities and towns may be start or end points.
- Each route must include one of the operating company’s stations somewhere.

### 20.2 Train Reach

- Large numbers count any stations.
- Small numbers on `+` trains count towns.

Examples:

- A `3` train may visit up to three stations.
- A `2+2` train may visit up to two towns plus two additional stations.

### 20.3 Route Legality

- A route must be continuous.
- You may not skip stations on the path.
- A route may not include the same city twice.
- A route may not run from Berlin back to Berlin.
- The two cities of a double city may both appear on one route while they remain separate.
- Two towns in one hex may both count if they remain separate.

### 20.4 Blocked Cities

- A route may start or end in a city with no remaining station slots.
- A route may not pass through such a blocked city.
- A city that is not completely filled by foreign stations may still be passed through.

### 20.5 Track Reuse

- A route may not use the same piece of track more than once.
- Separate tracks on the same tile may both be used.
- A route entering a station may leave through any other connected track.

### 20.6 Multiple Trains of One Company

- If a company runs more than one train, each train must use a completely separate route in terms of track.
- Routes may meet or cross at stations if separate track is used.
- A branching point where two lines merge into one cannot be shared by two trains in the same turn.

## 21. Revenue and Dividend Rules

### 21.1 Revenue Calculation

- Company revenue is the sum of the revenue of all its trains.
- The president must run for the maximum legally achievable revenue.
- Intentionally choosing a lower revenue is not allowed.

### 21.2 Station Values

- Towns are worth `10`.
- Normal cities are worth `20`.
- `Y` cities are worth `30`.
- Offboard values vary by phase as printed on the map.

Special notes from the rules:

- `Elsaß-Lothringen` is reachable only during phase 2 and is worth `50`.
- The brown Hamburg tile is worth:
  - `60` without crossing the Elbe
  - `50` when crossing the Elbe

### 21.3 Revenue Distribution

For pre-Prussian companies:

- `50%` of revenue goes to the owner
- `50%` goes to company treasury
- no other split is allowed

For corporations:

- the president chooses either:
  - pay the full revenue as dividend
  - or withhold the full revenue into treasury
- splitting between treasury and dividend is not allowed

### 21.4 Dividend Payments to Shareholders

If a corporation pays:

- each player receives the proportional amount matching their percentage ownership
- for `5%` increments, round the total amount owed to the player up

If shares are in the bank pool:

- the corresponding dividend amount goes to company treasury instead
- for `5%` Prussian shares, the total may round down

If the corporation withholds:

- shareholders receive nothing
- all revenue goes to company treasury

## 22. Stock Market Movement During ORs

- If a corporation pays dividend, its stock marker rises:
  - normally one space to the right
  - or one space up where arrow rules indicate
- If a corporation withholds, its stock marker falls:
  - normally one space to the left
  - or one space down where arrow rules indicate
- If a stock marker moves into an occupied space, the moved marker goes underneath existing markers.

The booklet also recommends flipping markers to track which companies have already operated in the round.

## 23. Buying Trains

### 23.1 General Timing

- Train buying happens at the end of the company’s operating turn.
- Bought trains are available starting next turn.

### 23.2 Available Sources

- from the bank at printed cost
- from the bank pool at printed cost
- from another company starting in green phase, at any openly declared negotiated price

Train purchases between companies may occur only when the buying company is the one currently operating.

### 23.3 Mandatory Train Rule

- Every open corporation must own at least one train at the end of its turn, unless no train exists in `Verfügbare Züge` or the bank pool.
- Pre-Prussian companies may own trains but are not required to.

### 23.4 Train Order

- New train types must be bought in strict order.
- All trains of one type must be bought before the next type becomes available.
- Within a size, the normal train must be sold out before the `+` train can be bought.

### 23.5 No Selling Trains to the Bank

- Trains can never be sold back to the bank.

## 24. Train Limits and Forced Losses

### 24.1 Train Limit

- Each phase sets a train limit per company.
- A company already at its train limit may not buy a new train, even if the purchase would rust enough trains to make the post-purchase total legal.

### 24.2 Excess Trains

- If train limits drop and a company ends up over the limit, excess trains are returned to the bank pool without compensation.
- Those trains may then be bought by other companies at printed price.

### 24.3 Prussia Exception

When Prussia opens or absorbs another company:

- Prussia may freely choose which trains to keep
- this is allowed even if it was already at its train limit

## 25. Forced Train Buys and Bankruptcy

### 25.1 Paying for a Required Train

- A company pays for a train from its treasury.
- If a pre-Prussian company lacks the money, it simply cannot buy.
- If a corporation must buy a train and lacks funds, its president must personally contribute the shortfall.

### 25.2 Limits on President Support

- The president may choose among trains available in bank or bank pool.
- Offers from other companies are always optional.
- The president may not contribute extra private money beyond what is required for the forced purchase.
- After such a president-assisted forced buy, the corporation must have no money left over.

### 25.3 Bankruptcy

If the president cannot fund the shortfall:

- they must immediately sell legal shares, even out of turn
- all normal sale restrictions apply
- they may not sell shares of the affected corporation if doing so would cost them the presidency

If that is still insufficient:

- the player is bankrupt and eliminated from the game
- the bank takes all remaining unsellable shares
- the bank pays the remaining train cost
- control of the company passes to the largest shareholder
- ties are broken starting from the player with the wooden locomotive and moving clockwise
- if nobody owns shares, the start player temporarily runs the company
- the director share may appear in the bank pool next stock round

### 25.4 Debt to the Bank

If the bank had to subsidize the required train:

- the company pays neither dividend nor retains spendable treasury until that amount has been repaid
- it is forced to withhold during that period

## 26. Phase Changes and Rusting

All major phase changes are caused by buying new trains from `Verfügbare Züge`.

### 26.1 First `3` Train

- Green phase begins.
- Green tiles become available.
- Yellow tiles may now be upgraded.
- Inter-company train purchases become legal.
- After the next stock round, there are 2 ORs between ARs.

### 26.2 First `4` Train

- All `2` trains rust and are removed from the game.
- Train limits change.
- The owner of `Berlin-Potsdamer` may now open Prussia.

### 26.3 First `4+4` Train

- All `2+2` trains rust and are removed.
- The owner of `Berlin-Potsdamer` must now open Prussia if that has not happened already.

### 26.4 First `5` Train

- Brown phase begins.
- All remaining pre-Prussian companies must convert into Prussia.
- `Braunschweigische` and `Hannoversche` must also convert.
- After all required conversions, resolve any presidency change for Prussia.
- Then apply the new train limits.
- Brown tiles become available.
- After the next stock round, there are 3 ORs between ARs.

### 26.5 First `6` Train

- All `3` trains rust and are removed.

### 26.6 First `6+6` Train

- All `3+3` trains rust and are removed.

## 27. End of Game

### 27.1 Bank Break

If the bank runs out of money during an OR:

- finish the current OR
- any unpaid amounts are recorded
- those recorded amounts count for final scoring

If the bank runs out during an AR:

- finish the current AR
- play one additional OR
- then end the game

### 27.2 Final Scoring

Each player totals:

- personal cash
- any recorded unpaid income
- current market value of all their shares

Do not count:

- company treasury
- trains

Highest total wins.

## 28. Optional Rules from the Booklet

These optional rules are suggested only if your group encounters recurring balance or opening issues.

### 28.1 Stronger Leipzig-Dresdner Income

- If `Leipzig-Dresdner` often stalls the start package, increase its income to `30 M` per round.

### 28.2 Discounting Unsold Privates

- If privates often remain unsold, reduce the price of an unsold private by its income each stock round.
- Example from the rules:
  - `Pfalzbahnen` would cost `135 M` in the second stock round
  - `120 M` in the third

### 28.3 Delay Pre-Prussian Operation

- If pre-Prussian companies dominate too strongly, require the start package to be fully sold before pre-Prussian companies may begin operating.

## 29. Quick Reference for Common Edge Cases

### 29.1 Stock Round Edge Cases

- A stock round ends on consecutive no-buy turns, not consecutive full passes.
- You can split sales into separate sale actions to move a stock more than once.
- You cannot rebuy a corporation in the same stock round after selling it.

### 29.2 Route Edge Cases

- Your trains must use separate track.
- They may share cities, but not the same pieces of track.
- A blocked city may be a route endpoint, but not a pass-through point.

### 29.3 Prussia Edge Cases

- Freely purchasable Prussian shares can exist before Prussia opens.
- They do not give operations or presidency until Prussia is actually opened.
- The owner of `Berlin-Potsdamer` controls Prussia’s opening window, but loses that discretion once the first `4+4` is bought.

### 29.4 Treasury and Revenue Edge Cases

- A normal corporation cannot earn revenue in the same turn it opens, because train buying is last.
- A corporation that pays dividend sends bank-pool share payouts to company treasury.
- A corporation forced to buy a train with president assistance must be left with no treasury cash.
