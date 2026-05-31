# frozen_string_literal: true

require_relative '../../../step/track'

module Engine
  module Game
    module G1862UsaCanada
      module Step
        class Track < Engine::Step::Track
          def process_lay_tile(action)
            super
            return unless action.hex.id == @game.class::SLC_HEX
            return unless action.tile.color == :yellow

            @game.slc_yellow_placed!(action.entity)
          end
        end
      end
    end
  end
end
