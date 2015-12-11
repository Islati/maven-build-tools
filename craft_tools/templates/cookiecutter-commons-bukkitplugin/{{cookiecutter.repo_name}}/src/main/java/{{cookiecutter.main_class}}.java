package {{cookiecutter.main_package}};
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
