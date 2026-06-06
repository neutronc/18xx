# frozen_string_literal: true

require_relative '../../../step/track'

module Engine
  module Game
    module G1862UsaCanada
      module Step
        class Track < Engine::Step::Track
          def process_lay_tile(action)
            super
            @game.slc_yellow_placed!(action.entity) if action.hex.id == @game.class::SLC_HEX && action.tile.color == :yellow
            @game.check_transcontinental_connection! if @game.class::SLC_CORPS.include?(action.entity.id)
          end
        end
      end
    end
  end
end
