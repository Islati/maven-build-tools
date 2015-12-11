package {{cookiecutter.main_package}}.user;

import {{cookiecutter.main_package}}.{{cookiecutter.main_class}};

import com.caved_in.commons.player.User;
import org.bukkit.entity.Player;
import org.simpleframework.xml.Element;

public class {{cookiecutter.user_class}} extends User {
    private static {{cookiecutter.main_class}} core = {{cookiecutter.main_class}}.getInstance();

    public AdventurePlayer(Player p) {
        super(p);
    }

    public AdventurePlayer(@Element(name = "name") String name, @Element(name = "uuid") String uid, @Element(name = "world") String world) {
        super(name, uid, world);
    }
}
