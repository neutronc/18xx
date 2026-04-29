# frozen_string_literal: true

module Engine
  module Game
    module G1862GoldenSpike
      module Entities
        # ---------------------------------------------------------------------------
        # Private Companies (P1–P8)
        # Auctioned in first stock round only; unsellable to corporations; no end value.
        # ---------------------------------------------------------------------------
        COMPANIES = [
          {
            name: 'Butterfield Overland Mail',
            sym: 'BOM',
            value: 20,
            revenue: 5,
            desc: 'No special abilities. Income only.',
            color: nil,
          },
          {
            name: 'Toronto Steamship Company',
            sym: 'TOR',
            value: 50,
            revenue: 10,
            desc: 'Blocks the Toronto hex while owned by a player. The owning corporation '\
                  'may place the special Toronto gray tile on the Toronto hex as a stock '\
                  'round action (free, no connection required). Closes when placed.',
            abilities: [
              { type: 'blocks_hexes', owner_type: 'player', hexes: ['C21'] },
              {
                type: 'tile_lay',
                owner_type: 'corporation',
                hexes: ['C21'],
                tiles: ['X_TORONTO_GRAY'], # FIXME: assign real tile ID in Sprint 11
                when: 'stock_round',
                count: 1,
                free: true,
                closed_when_used_up: true,
              },
            ],
            color: nil,
          },
          {
            name: 'Bahnhoflizenz',
            sym: 'GHU',
            value: 75,
            revenue: 15,
            desc: 'The owning corporation\'s director may place a station token for $80 '\
                  'less than the normal cost (minimum $0).',
            abilities: [
              {
                type: 'tile_discount',
                discount: 80,
                terrain: 'station',
                owner_type: 'corporation',
              },
            ],
            color: nil,
          },
          {
            name: 'Rocky Mountain Company',
            sym: 'RMC',
            value: 100,
            revenue: 20,
            desc: 'The owning corporation may lay one additional yellow tile during its '\
                  'operating turn. This ability is one-time use and closes the company.',
            abilities: [
              {
                type: 'tile_lay',
                owner_type: 'corporation',
                hexes: [],
                tiles: [],
                when: 'owning_corp_or_turn',
                count: 1,
                closed_when_used_up: true,
                special: false,
                free: false,
              },
            ],
            color: nil,
          },
          {
            name: 'Pacific Steamship Company',
            sym: 'PSC',
            value: 140,
            revenue: 25,
            desc: 'The initial purchaser immediately receives a 10% share of WP. '\
                  'Closes when WP first pays a dividend.',
            abilities: [
              { type: 'shares', shares: 'WP_1' },
              # Custom close trigger: when WP pays first dividend — handled in game.rb
            ],
            color: nil,
          },
          {
            name: 'First New York Steamship Co.',
            sym: 'FNY',
            value: 180,
            revenue: 30,
            desc: 'The initial purchaser immediately receives a 10% share of NYC. '\
                  'Closes when NYC first pays a dividend.',
            abilities: [
              { type: 'shares', shares: 'NYC_1' },
              # Custom close trigger: when NYC pays first dividend — handled in game.rb
            ],
            color: nil,
          },
          {
            name: 'Sacramento-Omaha Company',
            sym: 'SOC',
            value: 220,
            revenue: 35,
            desc: 'The initial purchaser immediately receives a 10% share of CPR and '\
                  'a 10% share of UP. Closes when either CPR or UP floats. '\
                  'While open, reduces the UP/CPR Salt Lake City route bonus payout to $15.',
            abilities: [
              { type: 'shares', shares: 'CPR_1' },
              { type: 'shares', shares: 'UP_1' },
              # Custom close trigger: when CPR or UP floats — handled in game.rb
            ],
            color: nil,
          },
          {
            name: 'New Haven Steamship Company',
            sym: 'NHSC',
            value: 270,
            revenue: 40,
            desc: "The initial purchaser immediately receives the 30% Director's "\
                  'certificate of NYH. NYH must be parred at exactly $100. '\
                  'Closes when NYH floats.',
            abilities: [
              { type: 'shares', shares: 'NYH_0' },
              { type: 'no_buy' },
              # Custom close trigger: when NYH floats — handled in game.rb
              # Custom par restriction: NYH par locked to $100 — handled in game.rb
            ],
            color: nil,
          },
        ].freeze

        # ---------------------------------------------------------------------------
        # Corporations — 3 groups, unlocked progressively:
        #   Group 1 (NYH, NYC, CP)  : available from game start
        #   Group 2 (CPR, UP, ATS, SP) : unlocked when ALL Group 1 companies float
        #   Group 3 (NP, CN, TP, ORN, WP, GMO) : unlocked when ALL Group 2 companies float
        #
        # Share structures:
        #   Group 1: 30% Director cert + 7 × 10% = 100%  (float at 60%)
        #   Group 2/3: 20% Director cert + 8 × 10% = 100% (float at 60%)
        #
        # FIXME: All hex coordinates are placeholders — update when map.rb is complete.
        # ---------------------------------------------------------------------------
        CORPORATIONS = [
          # -------------------------------------------------------------------------
          # Group 1 — 30% Director, float at 60%
          # -------------------------------------------------------------------------
          {
            sym: 'NYH',
            name: 'New York New Haven',
            logo: '1862_GoldenSpike/NYH',
            simple_logo: '1862_GoldenSpike/NYH.alt',
            float_percent: 60,
            shares: [30, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40, 100, 100],
            coordinates: 'D26',
            color: '#d1232a',
            text_color: 'white',
          },
          {
            sym: 'NYC',
            name: 'New York Central',
            logo: '1862_GoldenSpike/NYC',
            simple_logo: '1862_GoldenSpike/NYC.alt',
            float_percent: 60,
            shares: [30, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40, 100, 100],
            coordinates: 'D26',
            city: 1,
            color: '#110a0c',
            text_color: 'white',
          },
          {
            sym: 'CP',
            name: 'Canadian Pacific',
            logo: '1862_GoldenSpike/CP',
            simple_logo: '1862_GoldenSpike/CP.alt',
            float_percent: 60,
            shares: [30, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40, 100, 100],
            coordinates: 'C27',
            color: '#d88e39',
            text_color: 'black',
          },

          # -------------------------------------------------------------------------
          # Group 2 — 20% Director, float at 60%
          # -------------------------------------------------------------------------
          {
            sym: 'CPR',
            name: 'Central Pacific Railroad',
            logo: '1862_GoldenSpike/CPR',
            simple_logo: '1862_GoldenSpike/CPR.alt',
            float_percent: 60,
            shares: [20, 10, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40, 100],
            coordinates: 'D4',
            color: '#f48221',
            text_color: 'black',
          },
          {
            sym: 'UP',
            name: 'Union Pacific',
            logo: '1862_GoldenSpike/UP',
            simple_logo: '1862_GoldenSpike/UP.alt',
            float_percent: 60,
            shares: [20, 10, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40, 100],
            coordinates: 'D16',
            color: '#025aaa',
            text_color: 'white',
          },
          {
            sym: 'ATS',
            name: 'Atchison Topeka & Santa Fe',
            logo: '1862_GoldenSpike/ATS',
            simple_logo: '1862_GoldenSpike/ATS.alt',
            float_percent: 60,
            shares: [20, 10, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40, 100],
            coordinates: 'D20',
            color: '#32763f',
            text_color: 'white',
          },
          {
            sym: 'SP',
            name: 'Southern Pacific',
            logo: '1862_GoldenSpike/SP',
            simple_logo: '1862_GoldenSpike/SP.alt',
            float_percent: 60,
            shares: [20, 10, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40, 100],
            coordinates: 'F18',
            color: '#76a042',
            text_color: 'black',
          },

          # -------------------------------------------------------------------------
          # Group 3 — 20% Director, float at 60%
          # -------------------------------------------------------------------------
          {
            sym: 'NP',
            name: 'Northern Pacific',
            logo: '1862_GoldenSpike/NP',
            simple_logo: '1862_GoldenSpike/NP.alt',
            float_percent: 60,
            shares: [20, 10, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40],
            coordinates: 'C17',
            color: '#95c054',
            text_color: 'black',
          },
          {
            sym: 'CN',
            name: 'Canadian National',
            logo: '1862_GoldenSpike/CN',
            simple_logo: '1862_GoldenSpike/CN.alt',
            float_percent: 60,
            shares: [20, 10, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40],
            coordinates: 'B16',
            color: '#ADD8E6',
            text_color: 'black',
          },
          {
            sym: 'TP',
            name: 'Texas Pacific',
            logo: '1862_GoldenSpike/TP',
            simple_logo: '1862_GoldenSpike/TP.alt',
            float_percent: 60,
            shares: [30, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40],
            coordinates: 'E15',
            color: '#7b352a',
            text_color: 'white',
          },
          {
            sym: 'ORN',
            name: 'Oregon Railroad & Navigation',
            logo: '1862_GoldenSpike/ORN',
            simple_logo: '1862_GoldenSpike/ORN.alt',
            float_percent: 60,
            shares: [30, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40],
            coordinates: 'C1',
            color: '#FFF500',
            text_color: 'black',
          },
          {
            # WP co-homes in Sacramento (slot 1) alongside CPR (slot 0).
            # Both transcontinental roads originate from the Sacramento terminus.
            sym: 'WP',
            name: 'Western Pacific',
            logo: '1862_GoldenSpike/WP',
            simple_logo: '1862_GoldenSpike/WP.alt',
            float_percent: 60,
            shares: [30, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40],
            coordinates: 'D4',
            city: 1,
            color: '#8dd7f6',
            text_color: 'black',
          },
          {
            sym: 'GMO',
            name: 'Gulf Mobile & Ohio',
            logo: '1862_GoldenSpike/GMO',
            simple_logo: '1862_GoldenSpike/GMO.alt',
            float_percent: 60,
            shares: [20, 10, 10, 10, 10, 10, 10, 10, 10],
            max_ownership_percent: 100,
            tokens: [0, 40],
            coordinates: 'F20',
            color: '#6ec037',
            text_color: 'black',
          },
        ].freeze
      end
    end
  end
end
