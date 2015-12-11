package {{cookiecutter.main_package}}.listener;

import {{cookiecutter.main_package}}.{{cookiecutter.main_class}};
import {{cookiecutter.main_package}}.users.{{cookiecutter.user_class}};
import {{cookiecutter.main_package}}.users.{{cookiecutter.user_manager_class}};

import com.caved_in.commons.game.listener.UserManagerListener;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerKickEvent;
import org.bukkit.event.player.PlayerQuitEvent;

public class PlayerConnectionListener extends UserManagerListener {
    private {{cookiecutter.main_class}} core;
    private {{cookiecutter.user_manager_class}} users;

    public PlayerConnectionListener({{cookiecutter.main_class}} game) {
        super(game);
        this.core = game;
        this.users = game.getUserManager();
    }

    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent e) {
        Player p = e.getPlayer();

        if (users.hasOfflineData(p.getUniqueId())) {
            boolean loaded = users.loadData(p.getUniqueId());
            if (!loaded) {
                core.debug("Unable to load data for the player");
                return;
            }

            {{cookiecutter.user_class}} user = users.getUser(p);
        } else {
            users.addUser(p);
        }
    }

    @EventHandler
    public void onPlayerQuit(PlayerQuitEvent e) {
        Player player = e.getPlayer();

        boolean saved = users.save(player.getUniqueId());
        if (saved) {
            core.debug("Saved data for " + player.getName());
        } else {
            core.debug("Failed to save data for " + player.getName());
        }
    }

    @EventHandler
    public void onPlayerKick(PlayerKickEvent e) {
        Player player = e.getPlayer();

        boolean saved = users.save(player.getUniqueId());
        if (saved) {
            core.debug("Saved data for " + player.getName());
        } else {
            core.debug("Failed to save data for " + player.getName());
        }
    }
}
