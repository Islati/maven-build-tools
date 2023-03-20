maven-build-tools 
====
👉 Automate tests, builds, copy, and ftp-upload.


Installing
===

*Installing Latest Release (From PyPi)*

    $ pip install craftbuildtools
    
*Installing Latest Release (From Github)*

    $ git clone https://github.com/Islati/maven-build-tools.git
    $ cd CraftBuildTools
    $ python setup.py install 
    
*Installing Legacy Release (Only available on GitHub)*

    $ wget https://github.com/Islati/maven-build-tools/archive/legacy.tar.gz
    $ tar xvf legacy.tar.gz
    $ cd legacy
    $ python setup.py install


Features
-------------

 - Extremely Simple Project Management.
 - Create a new fully-configured projects in *seconds* with templates.
 - Edit your project information directly from the CLI
 - Build your projects all at once!
 - *Testing Locally?* Copy your built projects directly to your server!
 - *Running a server?* Upload your new builds to your server via FTP!
 - Plugin-Based Design; Enabling you to hack away and make your build process the way you want it!
 - Lightweight, enabling maximum productivity!

Commands
---------------
####<i class="icon-file"></i>Create a Project

*Run the command below, and follow its simply prompts!*

    $ craftbuildtools createproject

*What if I want to skip the prompts?*

    $ craftbuildtools createproject -tp TemplateName
 
 *What if my project is hosted on Git?*
 

    $ craftbuildtools createproject -tp Bukkit_Plugin --clone www.githost.com/TemplateRepo.git

Unlike below, *createproject* is its own command as it's an extremely complex operation, simplified through awesome design!

####<i class="icon-hdd"></i>Add a Project to be Managed

*Enter the command below, and follow the prompts! It's super simple!*

    $ craftbuildtools projects add

####<i class="icon-pencil"></i>Edit a Projects Information

    $ craftbuildtools projects edit

####<i class="icon-trash"></i>Remove a Project from CraftBuildTools

*Enter the command below, and follow the prompts! *

    $ craftbuildtools projects remove

*Note: There's also an option to remove the entire project source... Just incase you need it!*

####<i class="icon-list"></i>List all your available projects!

    $ craftbuildtools projects list

####<i class="icon-code"></i>Build your Project(s)

    $ craftbuildtools build -p ProjOne -p ProjTwo

####<i class="icon-trash"></i>Clean all the old Files!

    $ craftbuildtools clean


####<i class="icon-"></i>Copy all your built project files!

    $ craftbuildtools copy -l ~/Location/

####<i class="icon-upload"></i>Upload your Project(s) build files.

*With options defined after you first ran CraftBuildTools*

    $ craftbuildtools upload

*Specify new values to run the upload by, and save them for next time!*

    $ craftbuildtols upload -h ftp.host.com -u Username -p Password -d /Dev/Plugins/ --updateconfig


####<i class="icon-star"></i>ALL TOGETHER NOW!

    $ craftbuildtools clean build -p Project -p API -p Plugin copy -l ~/MinecraftPlugins/ upload -d /Dev/Plugins/

*See! Isn't that easy?*

***CraftBuildTools will make your minecraft development experience so pleasant and hassle free, you won't be able to turn back once you've started using it!***
