package {{cookiecutter.main_package}};
{% if cookiecutter.plugin_type == "BukkitPlugin" %}
import com.caved_in.commons.plugin.BukkitPlugin;

public class {{cookiecutter.main_class}} extends BukkitPlugin {
    private static {{cookiecutter.main_class}} instance = null;

    public static {{cookiecutter.main_class}} getInstance() {
        return instance;
    }

    @Override
    public void startup() {
        instance = this;

    }

    @Override
    public void shutdown() {

    }

    @Override
    public String getAuthor() {
        return "{{cookiecutter.project_author}}";
    }

    @Override
    public void initConfig() {

    }
}
{% elif cookiecutter.plugin_type == "MiniGame" %}
import com.caved_in.commons.game.MiniGame;
import com.caved_in.commons.game.players.UserManager;
import com.caved_in.commons.player.User;
import org.bukkit.entity.Player;

public class {{cookiecutter.main_class}} extends MiniGame<{{cookiecutter.main_class}}.{{cookiecutter.main_class}}UserManager> {
    private static {{cookiecutter.main_class}} instance = null;

    public static {{cookiecutter.main_class}} getInstance() {
        return instance;
    }

    @Override
    public void startup() {
        instance = this;

        registerGameStates(new PreGameState());
    }

    @Override
    public void shutdown() {

    }

    @Override
    public String getAuthor() {
        return "{{cookiecutter.plugin_author}}";
    }

    @Override
    public void initConfig() {

    }

    @Override
    public long tickDelay() {
        return 0; //TODO Modify this tho how often you wish the core to tick!
    }

    public static class {{cookiecutter.main_class}}UserManager extends UserManager<{{cookiecutter.main_class}}User> {
        public {{cookiecutter.main_class}}UserManager() {
            super({{cookiecutter.main_class}}User.class);
        }
    }

    public static class {{cookiecutter.main_class}}User extends User {
        public {{cookiecutter.main_class}}User(Player p) {
            super(p);
        }
    }


    public static class PreGameState extends MiniGameState {

        @Override
        public void update() {

        }

        @Override
        public int id() {
            return 1;
        }

        @Override
        public boolean switchState() {
            return false;
        }

        @Override
        public int nextState() {
            return 1;//todo change; Make new state for playing?
        }

        @Override
        public void setup() {
            //setup here

            //then finish setup
            setSetup(true);
        }

        @Override
        public void destroy() {

        }
    }
}
{% endif %}


