[app]

title = Трекеры БЖУ

package.name = calorie_calculator

package.domain = org.The-same-Danilych.calorie_calculator

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,ttf,json

source.include_patterns = assets/*,database/*,ui/*,services/*,utils/*,schemas/*

version = 1.0.0

requirements = python3,kivy==2.3.1,https://github.com/kivymd/KivyMD/archive/master.zip,sqlalchemy,pydantic,typing_extensions,pillow

icon.filename = assets/images/icon.png

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33

android.minapi = 21

android.ndk = 25b

android.sdk = 33

android.allow_backup = True

android.debug = True

log_level = 2

android.arch = arm64-v8a

android.multidex = False
