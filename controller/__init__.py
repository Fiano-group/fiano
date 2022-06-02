"""Controller Module: This module is used to implement the 
calls from the views to the model logic.
These calls are using FLASK calls from web apps
Each module is divided into a controller file, you can use folders 
to divide longer controllers.
Controllers: 
    
If you are planning to add a functionality the order will be:
    - Add a .html into the views folder, following the format specified there.
    - Add a module into the modules folder, following the format specified there.
    - Add a controller to join the frontend calls to your module.
"""

from controller import analysis_controller
from controller import files_controller
from controller import login_controller
from controller import processing_controller
from controller import projects_controller
from controller import users_controller
