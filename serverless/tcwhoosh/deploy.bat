@echo off

SET currentFolder = %cd%
FOR /D %%p IN ("C:\Users\%USERNAME%\AppData\Local\UnitedIncome\serverless-python-requirements\Cache\*.*") DO (
    echo %%p | findstr /r downloadCacheslspyc > NUL
    if errorlevel 1 (
        rmdir "%%p" /s /q
    )
)
cd %currentFolder%

call serverless deploy --stage %1 --verbose