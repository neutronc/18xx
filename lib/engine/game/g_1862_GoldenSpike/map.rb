# frozen_string_literal: true

# FIXME: All hex coordinates are approximations based on photo analysis.
# Exact positions, mountain/river terrain, and pre-printed track directions
# must be verified against the physical rulebook before release.
module Engine
  module Game
    module G1862GoldenSpike
      module Map
        LAYOUT = :pointy

        LOCATION_NAMES = {
          # Pacific Northwest
          'B2'  => 'Vancouver',
          'C1'  => 'Victoria',
          'C3'  => 'Seattle',
          'C5'  => 'Spokane',
          'D2'  => 'Portland'
          # Western Canada
          'A7'  => 'Calgary',
          'B10' => 'Regina',
          'B14' => 'Winnipeg',
          'B20' => 'Thunder Bay',
          # Mountain West
          'E6'  => 'Boise'
          'D10' => 'Billings',
          'E11' => 'Rapid City',
          'F8'  => 'Ogden'
          'G9'  => 'Salt Lake City/SLC',
          'G11' => 'Denver',
          # Pacific Coast
          'G3'  => 'San Francisco/Sacramento',
          'I5'  => 'Los Angeles',
          'J6'  => 'San Diego',
          # Great Plains
          'D16' => 'Minneapolis',
          'D18' => 'Duluth',
          'G17' => 'Kansas City',
          'F14' => 'Omaha',
          'G19' => 'St. Louis',
          # Midwest / Great Lakes
          'F20' => 'Chicago',
          'G23' => 'Columbus',
          # Canada East
          'E25' => 'Toronto',
          'D26' => 'Ottawa',
          'C29' => 'Quebec',
          'D28' => 'Montreal',
          # Northeast
          'F28' => 'New York',
          'F30' => 'Boston',
          # Southwest
          'I9'  => 'Phoenix',
          'J8'  => 'Tucson',
          'J10' => 'Santa Fe',
          # South Central
          'I15' => 'Oklahoma City',
          'J16' => 'Dallas',
          'I17' => 'Little Rock',
          'K15' => 'Austin',
          'K17' => 'Houston',
          # Southeast
          'J18' => 'Jackson',
          'I23' => 'Atlanta',
          'I21' => 'Chattanooga',
          'H26' => 'Richmond',
          'K19' => 'New Orleans',
          'J20' => 'Mobile',
          # Off-board labels
          'A29' => 'Labrador',
          'K9'  => 'Mexico',
          'K11' => 'Mexico'
          'L24' => 'Florida',
        }.freeze

        # Tile counts from physical game tile sheet.
        # Yellow: 80 standard + 5 Sonderteile = 85 total
        # Green:  42 standard + 9 Sonderteile = 51 total
        # Brown:  19 standard + 7 Sonderteile = 26 total
        # Gray:    3 standard + 5 Sonderteile =  8 total
        TILES = {
          # Yellow
          '3'  => 4,
          '4'  => 10,
          '6'  => 10,
          '7'  => 4,
          '8'  => 12,
          '9'  => 22,
          '57' => 10,
          '58' => 8,
          # Green
          '14' => 4,
          '15' => 4,
          '16' => 2,
          '17' => 2,
          '18' => 2,
          '19' => 2,
          '20' => 2,
          '23' => 3,
          '24' => 3,
          '25' => 2,
          '26' => 2,
          '27' => 2,
          # Brown
          '39' => 2,
          '40' => 2,
          '41' => 2,
          '42' => 2,
          '43' => 2,
          '44' => 1,
          '45' => 2,
          '46' => 2,
          '47' => 2,
          '70' => 2,
          # Gray (city upgrade tiles)
          '127' => 1,
          '128' => 1,
          '129' => 1,
        }.freeze

        MAP_HOMECITY_HEXES = %w[
          C3 B14 D28 D16 F14 F20 F28 G3 J16 J20 K19
        ].freeze

        HEXES = {
          white: {
            # ── Blank upgradeable hexes ──────────────────────────────────────
            %w[
              A11 A13 A17 A19 A21 A23 A25 A27 B12 B14 B16 B18 
              B20 B22 B24 B26 C13 C15 C17 C19 C21 C23 C25 C27 
              C29 D4 D14 D16 D18 D20 D24 D26 D28 E19 E27  F22 
              F24 G15 G21 H14 H16 H18 H22 I25 J14 J22 K13 K23
            ] => '',

            # ── Mountain terrain ($80) ───────────────────────────────────────
            %w[
              A3 A5 B4 B6 B8 C7 C9 D6 D8 E3 E7 E9 F4 F6 F10
              G5 G7 H8 I7  
            ] => 'upgrade=cost:80,terrain:mountain',
            
            # ── Hill terrain ($40) ───────────────────────────────────────
            %w[
              A9 C11 D12 F12 F26 G13 G25 H12 H24 I11 I13 J12
            ] => 'upgrade=cost:40,terrain:mountain',
            # ── River terrain ($40) ──   
            %w[ A15 B28 D30 E1 E13 E15 E17 F2 F16 H4 H20 I19 J24 K21] =>'upgrade=cost:40,terrain:river',
            # ── City with River ($40) ──
            %w [ F18 G17] =>'city=revenue:0;upgrade=cost:40,terrain:river',
            # Town with river ($40)
            %w [ G19 J17] =>'town=revenue:0;upgrade=cost:40,terrain:river',
            # Plain City
            %w [ A7, B10, B14, C29 D16 D26 E11 G9 G11 G27 H10 I15 I23 J6 J10 J16 J20 K15]
            # Town
            %w [ C5 B20 D10 D18 E29 C5 F8 G23 H6 H26 I9 I17 I21 J8 K17] =>'town=revenue:0',

            # ── Single-slot cities ───────────────────────────────────────────
            ['B2']  => 'city=revenue:0;label=V',   # Vancouver
            ['D2']  => 'city=revenue:0;label=P',   # Portland

            ['I5']  => 'city=revenue:0;label=L',   # Los Angeles
            
            ['D28'] => 'city=revenue:10;label=M',   # Montreal
          },

          yellow: {
            # SLC pre-printed yellow tile — transcontinental junction.
            # Revenue 20, east-west path through city.
            ['G9'] => 'city=revenue:20;path=a:1,b:_0;path=a:4,b:_0;label=SLC',
          },

          red: {
            # Labrador — far northeast off-board (20/40 by phase)
            ['A29'] =>
              'offboard=revenue:yellow_20|brown_40;path=a:2,b:_0;path=a:3,b:_0',
            # Mexico — south of El Paso (0 yellow, 80 brown)
            ['G7']  =>
              'offboard=revenue:yellow_0|brown_80;path=a:0,b:_0;path=a:5,b:_0',
            # Florida — southeast off-board (30/60 by phase)
            ['G23'] =>
              'offboard=revenue:yellow_30|brown_60;path=a:0,b:_0;path=a:5,b:_0',
          },
        }.freeze
      end
    end
  end
end
