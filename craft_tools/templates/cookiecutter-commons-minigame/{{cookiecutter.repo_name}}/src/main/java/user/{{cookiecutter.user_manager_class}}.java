package {{cookiecutter.main_package}}.user;

import import {{cookiecutter.main_package}}.{{cookiecutter.main_class}};

import com.caved_in.commons.game.players.UserManager;
import com.caved_in.commons.player.User;
import org.simpleframework.xml.Serializer;
import org.simpleframework.xml.convert.AnnotationStrategy;
import org.simpleframework.xml.core.Persister;

import java.io.File;
import java.util.UUID;

public class {{cookiecutter.user_manager_class}} extends UserManager<{{cookiecutter.user_class}}> {
    private static {{cookiecutter.main_class}} core = {{cookiecutter.main_class}}.getInstance();
    
    private Serializer serializer = new Persister(new AnnotationStrategy());

    public {{cookiecutter.user_manager_class}}() {
        super({{cookiecutter.user_class}}.class);
    }
    
    public boolean hasOfflineData(UUID id) {
        return getUserFile(id).exists();
    }
    
    public boolean loadData(UUID id) {
        File userFile = getUserFile(id);
        if (!userFile.exists()) {
            return false;
        }
        
        
        boolean loaded = false;

        try {
            {{cookiecutter.user_class}} user = serializer.read({{cookiecutter.user_class}}.class,userFile);
            if (user != null) {
                addUser(user);
                loaded = true;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return loaded;
    }
    
    public boolean save(UUID id) {
        if (!hasData(id)) {
            core.debug("There's no data loaded for the id: " + id.toString());
            return false;
        }
        File userFile = getUserFile(id);
        
        {{cookiecutter.user_class}} player = getUser(id);
        boolean saved = false;
        try {
            serializer.write(player,userFile);
            saved = true;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return saved;
    }
    
    private File getUserFile(UUID id) {
        return new File(core.getUserDataFolder(),String.format("%s.xml",id.toString()));
    }
}
