echo off

docker tag busking yujiwen/busking
docker login
docker push yujiwen/busking
