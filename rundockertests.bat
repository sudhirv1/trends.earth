@echo off
REM Run docker tests on your local machine

set PLUGIN_NAME="LDMP"
set QGIS_VERSION_TAG=master_2
 
set DOCKER_RUN_COMMAND=docker exec -it trendsearth_qgis-testing-environment_1 sh -c

docker-compose down -v
docker-compose up -d
docker-compose ps
timeout 2

REM Setup docker instance
%DOCKER_RUN_COMMAND% "pip install pip==9.0.1"
%DOCKER_RUN_COMMAND% "qgis_setup.sh %PLUGIN_NAME%"
%DOCKER_RUN_COMMAND% "cd /tests_directory && git submodule update --init --recursive"
%DOCKER_RUN_COMMAND% "pip install paver"
%DOCKER_RUN_COMMAND% "pip install boto3"
%DOCKER_RUN_COMMAND% "cd /tests_directory && paver setup && paver package --tests"

REM Run the tests
%DOCKER_RUN_COMMAND% "DISPLAY=:99 QT_X11_NO_MITSHM=1 GSHOSTNAME=boundless-test qgis_testrunner.sh LDMP.test.dialog_settings_tests"