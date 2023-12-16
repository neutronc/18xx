# frozen_string_literal: true

require_relative 'meta'
require_relative '../base'
require_relative 'map'
require_relative 'entities'
require_relative '../../round/operating'

module Engine
  module Game
    module G1835
      class Game < Game::Base
        include_meta(G1835::Meta)
        include G1835::Entities
        include G1835::Map

        register_colors(black: '#37383a',
                        seRed: '#f72d2d',
                        bePurple: '#2d0047',
                        peBlack: '#000',
                        beBlue: '#c3deeb',
                        heGreen: '#78c292',
                        oegray: '#6e6966',
                        weYellow: '#ebff45',
                        beBrown: '#54230e',
                        gray: '#6e6966',
                        red: '#d81e3e',
                        turquoise: '#00a993',
                        blue: '#0189d1',
                        brown: '#7b352a')

        CURRENCY_FORMAT_STR = '%sM'
        # game end current or, when the bank is empty
        GAME_END_CHECK = { bank: :current_or }.freeze
        # bankrupt is allowed, player leaves game
        BANKRUPTCY_ALLOWED = true

        BANK_CASH = 12_000
        PAR_PRICES = {
          'PR' => 154,
          'BY' => 92,
          'SX' => 88,
          'BA' => 84,
          'WT' => 84,
          'HE' => 84,
          'MS' => 80,
          'OL' => 80,
        }.freeze
        CERT_LIMIT = { 3 => 19, 4 => 15, 5 => 12, 6 => 11, 7 => 9 }.freeze

        STARTING_CASH = { 3 => 600, 4 => 475, 5 => 390, 6 => 340, 7 => 310 }.freeze
        # money per initial share sold
        CAPITALIZATION = :incremental

        MUST_SELL_IN_BLOCKS = false

        MARKET = [['',
                   '',
                   '',
                   '',
                   '132',
                   '148',
                   '166',
                   '186',
                   '208',
                   '232',
                   '258',
                   '286',
                   '316',
                   '348',
                   '382',
                   '418'],
                  ['',
                   '',
                   '98',
                   '108',
                   '120',
                   '134',
                   '150',
                   '168',
                   '188',
                   '210',
                   '234',
                   '260',
                   '288',
                   '318',
                   '350',
                   '384'],
                  %w[82
                     86
                     92p
                     100
                     110
                     122
                     136
                     152
                     170
                     190
                     212
                     236
                     262
                     290
                     320],
                  %w[78
                     84p
                     88p
                     94
                     102
                     112
                     124
                     138
                     154p
                     172
                     192
                     214],
                  %w[72 80p 86 90 96 104 114 126 140],
                  %w[64 74 82 88 92 98 106],
                  %w[54 66 76 84 90]].freeze

        PHASES = [
          {
            name: '1.1',
            on: '2',
            train_limit: { minor: 2, major: 4 },
            tiles: [:yellow],
            operating_rounds: 1,
          },
          {
            name: '1.2',
            on: '2+2',
            train_limit: { minor: 2, major: 4 },
            tiles: [:yellow],
            operating_rounds: 1,
          },
          {
            name: '2.1',
            on: '3',
            train_limit: { minor: 2, major: 4 },
            tiles: %i[yellow green],
            operating_rounds: 2,
          },
          {
            name: '2.2',
            on: '3+3',
            train_limit: { major: 4, minor: 2 },
            tiles: %i[yellow green],
            operating_rounds: 2,
          },
          {
            name: '2.3',
            on: '4',
            train_limit: { prussian: 4, major: 3, minor: 1 },
            tiles: %i[yellow green],
            operating_rounds: 2,
          },
          {
            name: '2.4',
            on: '4+4',
            train_limit: { prussian: 4, major: 3, minor: 1 },
            tiles: %i[yellow green],
            operating_rounds: 2,
          },
          {
            name: '3.1',
            on: '5',
            train_limit: { prussian: 3, major: 2 },
            tiles: %i[yellow green],
            operating_rounds: 3,
            events: { close_companies: true },
          },
          {
            name: '3.2',
            on: '5+5',
            train_limit: { prussian: 3, major: 2 },
            tiles: %i[yellow green brown],
            operating_rounds: 3,
          },
          {
            name: '3.3',
            on: '6',
            train_limit: { prussian: 3, major: 2 },
            tiles: %i[yellow green brown],
            operating_rounds: 3,
          },
          {
            name: '3.4',
            on: '6+6',
            train_limit: { prussian: 3, major: 2 },
            tiles: %i[yellow green brown],
            operating_rounds: 3,
          },
        ].freeze

        TRAINS = [{ name: '2', distance: 2, price: 80, rusts_on: '4', num: 9 },
                  { name: '2+2', distance: 2, price: 120, rusts_on: '4+4', num: 4 },
                  { name: '3', distance: 3, price: 180, rusts_on: '6', num: 4 },
                  { name: '3+3', distance: 3, price: 270, rusts_on: '6+6', num: 3 },
                  { name: '4', distance: 4, price: 360, num: 3 },
                  { name: '4+4', distance: 4, price: 440, num: 1 },
                  { name: '5', distance: 5, price: 500, num: 2 },
                  { name: '5+5', distance: 5, price: 600, num: 1 },
                  { name: '6', distance: 6, price: 600, num: 2 },
                  { name: '6+6', distance: 6, price: 720, num: 4 }].freeze

        LAYOUT = :pointy

        SELL_MOVEMENT = :down_block

        HOME_TOKEN_TIMING = :float

        def pre_pru_corporations
          # Priority ordered list of pre-PRU corporations
          @pre_pru_corps ||= %w[P1 P2 P3 P4 P5 P6].map { |id| corporation_by_id(id) }
        end

        def setup
          corporations.each do |i|
            @stock_market.set_par(i, @stock_market.par_prices.find do |p|
                                       p.price == PAR_PRICES[i.id]
                                     end)
            i.ipoed = true

            pru.shares.select { |s| s.percent == 10 && !s.president }.each { |s| s.double_cert = true }
          end
        end
        def event_pru_formation!
          @log << "-- Event: #{EVENTS_TEXT['pru_formation'][1]} --"
          @ready_to_form_pru = true
        end

        def init_round
          G1835::Round::Draft.new(self,
                                  [G1835::Step::Draft],
                                  reverse_order: true)
        end

        def form_PRU!
          @log << '-- Event: PRU forms --'

          @stock_market.set_par(PRU, @stock_market.share_prices_with_types(%i[par_1]).first)
          PRU.floatable = true
          PRU.ipoed = true
          PRU.floated = true

          #@bank.spend(400, PRU)
          @PRU_train.owner = PRU
          PRU.trains << @PRU_train
          @log << "#{PRU.name} starts with #{format_currency(400)} and a #{@PRU_train.name} train"

          previous_owners = []
          pre_pru_corporations.each do |corp|
            @log << "#{corp.name} merging into #{PRU.name}"
            previous_owners << corp.owner

            @log << "#{PRU.name} receives #{format_currency(corp.cash)}"
            corp.spend(corp.cash, PRU) if corp.cash.positive?

            place_PRU_tokens!(corp)

            num_trains = corp.trains.size
            if num_trains.positive?
              @log << "#{PRU.name} receives #{num_trains} train#{num_trains == 1 ? '' : 's'}:" \
                " #{corp.trains.map(&:name).join(', ')}"
              transfer(:trains, corp, PRU)
            end

            PRU_share_exchange!(corp)

            close_corporation(corp, quiet: true)
          end

          PRU.tokens.sort_by! { |t| t.used ? 0 : 1 }

          determine_PRU_president!(previous_owners.uniq)
        end

        def determine_pru_president!(president_priority_order)
          player_share_percent = pru.player_share_holders
          max_percent = player_share_percent.values.max || 0
          return if max_percent < 10

          # Determine president
          candidates = player_share_percent.select { |_, percent| percent == max_percent }.keys
          if candidates.size > 1
            candidates.sort_by! { |player| president_priority_order.index(player) || president_priority_order.size }
          end
          president = candidates.first

          # Make sure president has a 10% cert
          if (president_shares = president.shares_of(pru)).none? { |share| share.percent == 10 }
            ten_percent_share = @share_pool.shares_of(pru).find { |share| share.percent == 10 } ||
              president_priority_order[-1].shares_of(pru).find { |share| share.percent == 10 }
            @share_pool.transfer_shares(ShareBundle.new([ten_percent_share]), president, allow_president_change: false)
            @share_pool.transfer_shares(ShareBundle.new(president_shares.take(2)), share.owner, allow_president_change: false)
          end

          # Make sure president has the presidents cert
          if (presidents_share_owner = pru.presidents_share.owner) != president
            @share_pool.transfer_shares(ShareBundle.new([pru.presidents_share]), president)
            @share_pool.transfer_shares(
              ShareBundle.new([president_shares.find { |share| !share.president && share.percent == 10 }]),
              presidents_share_owner
            )
          end

          pru.owner = president
          @log << "#{president.name} becomes the president of #{pru.name}"
        end

        def place_pru_tokens!(corporation)
          locations = corporation.tokens.map { |token| token.used ? token.hex.full_name : 'Unused' }.join(', ')
          @log << "#{pru.name} receives #{corporation.tokens.size} tokens: #{locations}"
          corporation.tokens.each do |token|
            pru.tokens << Token.new(pru, price: 100)
            next unless token.used

            if token.city.tokened_by?(pru)
              @log << "#{pru.name} already has a token on #{token.hex.full_name}, placing token on charter instead"
              token.remove!
            else
              token.swap!(pru.tokens.last, check_tokenable: false)
            end
          end
        end

        def pru_share_exchange!(corporation)
          corporation.share_holders.keys.each do |share_holder|
            pru_shares = pru.shares_of(pru)
            shares = share_holder.shares_of(corporation).map do |corp_share|
              percent = corp_share.president ? 10 : 5
              share = pru_shares.find { |pru_share| pru_share.percent == percent }
              pru_shares.delete(share)
              share
            end
            next if shares.empty?

            share_holder = @share_pool if share_holder.corporation?
            bundle = ShareBundle.new(shares)
            @share_pool.transfer_shares(bundle, share_holder, allow_president_change: false)

            cash_per_share = corporation.par_price ? corporation.share_price.price - pru.share_price.price : 0
            cash = cash_per_share * bundle.percent / 5
            msg = share_holder.name.to_s
            if cash.zero? || share_holder == @share_pool
              msg += ' receives'
            elsif cash.positive?
              msg += " receives #{format_currency(cash)} and"
              @bank.spend(cash, share_holder)
            else
              msg += " pays #{format_currency(cash.abs)} and receives"
              share_holder.spend(cash.abs, @bank, check_cash: false)
            end

            msg += " #{bundle.percent}% of #{pru.name}"
            @log << msg
            next if !share_holder.player? || !share_holder.cash.negative?

            debt = share_holder.cash.abs
            share_holder.debt += debt
            share_holder.cash += debt
            @log << "#{share_holder.name} takes #{format_currency(debt)} of debt to complete payment"
          end
        end
            def init_stock_market
              G1835::StockMarket.new(game_market, self.class::CERT_LIMIT_TYPES,
                                     multiple_buy_types: self.class::MULTIPLE_BUY_TYPES)
            end

            def initial_auction_companies
              privates
            end

            def unowned_purchasable_companies(_entity)
              @companies.select { |c| c.owner == @bank }
            end

            def next_round!
              @round =
                case @round
                when Engine::Round::Auction
                  init_round_finished
                  reorder_players(log_player_order: true)
                  new_stock_round
                when Engine::Round::Stock
                  @operating_rounds = @phase.operating_rounds
                  new_operating_round
                when G1835::Round::Operating
                  next_round =
                    if @round.round_num < @operating_rounds
                      or_round_finished
                      -> { new_operating_round(@round.round_num + 1) }
                    else
                      @turn += 1
                      or_round_finished
                      or_set_finished
                      -> { new_stock_round }
                    end
                  if @ready_to_form_pru
                    @post_pru_formation_round = next_round
                    new_pru_formation_round
                  else
                    next_round.call
                  end
                when G1835::Round::pruFormation
                  next_round = @post_pru_formation_round
                  @ready_to_form_pru = false
                  @post_pru_formation_round = nil
                  next_round.call
                end
            end

            def operating_round(round_num)
          Engine::Round::Operating.new(self, [
            Engine::Step::Bankrupt,
            Engine::Step::SpecialTrack,
            Engine::Step::SpecialToken,
            Engine::Step::Track,
            Engine::Step::Token,
            Engine::Step::Route,
            Engine::Step::Dividend,
            Engine::Step::DiscardTrain,
            Engine::Step::BuyTrain,
          ], round_num: round_num)
        end
      end
    end
  end
end
