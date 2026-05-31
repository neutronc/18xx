# frozen_string_literal: true

require_relative '../../../step/route'

module Engine
  module Game
    module G1862UsaCanada
      module Step
        class Route < Engine::Step::Route
          def process_run_routes(action)
            entity = action.entity
            @round.routes = action.routes
            @round.extra_revenue = action.extra_revenue
            trains = {}
            abilities = []

            @round.routes.each do |route|
              train = route.train
              if train.owner && @game.train_owner(train) != entity
                raise GameError,
                      "Cannot run another corporation's train. refresh"
              end
              raise GameError, 'Cannot run train twice' if trains[train]
              raise GameError, 'Cannot run train that operated' if train.operated

              trains[train] = true
              revenue = @game.format_revenue_currency(route.revenue)
              corp_bonus = @game.corp_bonus_revenue(route)
              slc_bonus = @game.slc_route_bonus(route)

              bonus_str = ''
              bonus_str += " (+#{@game.format_currency(corp_bonus)} Bonus)" if corp_bonus.positive?
              bonus_str += " (+#{@game.format_currency(slc_bonus)} SLC)" if slc_bonus.positive?

              @log << "#{entity.name} runs a #{train.name} train for #{revenue}#{bonus_str}: #{route.revenue_str}"
              abilities.concat(route.abilities) if route.abilities
            end
            log_extra_revenue(entity, action.extra_revenue)
            pass!

            abilities.uniq.each { |type| @game.abilities(action.entity, type, time: 'route')&.use! }
          end
        end
      end
    end
  end
end
