package {{cookiecutter.main_package}}.state;

import com.caved_in.commons.game.MiniGameState;
import com.caved_in.commons.player.Players;

public class PlayingState extends MiniGameState {
    @Override
    public void update() {

    }

    @Override
    public int id() {
        return 2;
    }

    @Override
    public boolean switchState() {
        return Players.getOnlineCount() == 0;
    }

    @Override
    public int nextState() {
        return 1;
    }

    @Override
    public void setup() {
        debug("Listening to all player interactions on a per-tick basis!");
        setSetup(true);
    }

    @Override
    public void destroy() {

    }
}
