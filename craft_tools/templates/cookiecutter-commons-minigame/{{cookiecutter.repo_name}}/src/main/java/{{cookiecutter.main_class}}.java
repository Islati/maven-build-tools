package {{cookiecutter.main_package}};

import {{cookiecutter.main_package}}.user.{{cookiecutter.user_manager_class}};
import {{cookiecutter.main_package}}.state.EmptyServerState;
import {{cookiecutter.main_package}}.state.PlayingState;
import {{cookiecutter.main_package}}.listener.PlayerConnectionListener;

import com.caved_in.commons.game.MiniGame;
import com.caved_in.commons.game.MiniGameState;
import com.caved_in.commons.game.players.UserManager;
import com.caved_in.commons.player.User;
import org.bukkit.entity.Player;

public class {{cookiecutter.main_class}} extends MiniGame<{{cookiecutter.user_manager_class}}> {
    private static {{cookiecutter.main_class}} instance = null;

    public static {{cookiecutter.main_class}} getInstance() {
        return instance;
    }

    private static final String USER_DATA_FOLDER = "plugins/{{cookiecutter.project_name}}/users/";

    @Override
    public void startup() {
        instance = this;

        /**
        * Register your user manager class so you
        * can actually create instances of the user data!
        */
        registerUserManager({{cookiecutter.user_manager_class}}.class);

        /*
        * Used to handle all incoming data and connections of players!
        * If we don't set a custom listener, then we'll have a hell-of-a hard time
        * saving and loading data for players!
        */
        setUserManagerListener(new PlayerConnectionListener(this));

        /**
        * Dummy game states used for empty server, and when there's
        * more than one person online!
        *
        * Modify this to your likings when you wish to implement some logic into the States
        */
        registerGameStates(
            new EmptyServerState(),
            new PlayingState()
        );
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
        File userDataFolder = new File(getUserDataFolder());
        if (!userDataFolder.exists()) {
            userDataFolder.mkdirs();
        }
    }

    @Override
    public long tickDelay() {
        return 20; //TODO Modify this tho how often you wish the core to tick!
    }

    public String getUserDataFolder() {
        return USER_DATA_FOLDER;
    }
}
