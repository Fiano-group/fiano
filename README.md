# FIANO
Fiano es un softwate para la clasificación de fibras de alpaca para el control de calidad, esta plataforma se
va  autilizar en la web con cloud computing.

## Instalación
Usamos [python3](https://www.python.org/downloads/) 

## Uso
```import os
import cv2
import shutil
import numpy as np
import thinning
import bcrypt
from flask import Flask, request, render_template, Response, url_for, redirect
from werkzeug.utils import secure_filename
# from matplotlib import pyplot as plt
from matplotlib.figure import Figure

import sqlite3 as sql
from flask import g
```
