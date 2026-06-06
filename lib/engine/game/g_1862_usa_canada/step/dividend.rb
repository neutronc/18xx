# frozen_string_literal: true

require_relative '../../../step/dividend'

module Engine
  module Game
    module G1862UsaCanada
      module Step
        class Dividend < Engine::Step::Dividend
          def process_dividend(action)
            entity = action.entity
            first_time = entity.operating_history.none? { |_, info| info.dividend.kind.to_sym == :payout }

            # Capture routes and bonuses before parent clears them
            current_routes = routes
            @game.activate_new_bonuses!(entity, current_routes)
            @game.check_golden_spike!(entity, current_routes)

            # Store routes for log_run_payout to access
            @dividend_routes = current_routes

            super
            @game.on_first_payout!(entity) if first_time && action.kind.to_sym == :payout
          end

          def log_run_payout(entity, kind, revenue, subsidy, action, payout)
            unless self.class::DIVIDEND_TYPES.include?(kind)
              routes_to_log = @dividend_routes || []
              base_rev = @game.routes_revenue(routes_to_log)
              corp_bonus = @game.corp_bonus_revenue(entity, routes_to_log)
              slc_bonus = @game.slc_route_bonus(entity, routes_to_log)

              components = [base_rev]
              components << corp_bonus if corp_bonus.positive?
              components << slc_bonus if slc_bonus.positive?
              breakdown = components.map { |v| @game.format_currency(v) }.join(' + ')

              @log << "#{entity.name} runs for #{@game.format_currency(revenue)} (#{breakdown}) and pays #{action.kind}"
            end

            if payout[:corporation].positive?
              @log << "#{entity.name} withholds #{@game.format_currency(payout[:corporation])}"
            elsif payout[:per_share].zero?
              @log << "#{entity.name} does not run"
            end
            @log << "#{entity.name} earns #{@game.subsidy_name} of #{@game.format_currency(subsidy)}" if subsidy.positive?
          end

          # Non-buyable treasury shares (the 50% buyback cert) earn dividends back
          # into the corporation.  For corps that have never done a buyback, the
          # non-buyable set is empty and this reduces to super.
          def corporation_dividends(entity, per_share)
            treasury_units = entity.shares_of(entity)
                                   .reject(&:buyable)
                                   .sum { |s| s.num_shares(ceil: false) }
            super + (treasury_units * per_share).ceil
          end
        end
      end
    end
  end
end
