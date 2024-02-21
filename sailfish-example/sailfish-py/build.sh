docker build ./run-manager -t zeidaof/sailfish-runmanager
docker push zeidaof/sailfish-runmanager

docker build ./runner -t zeidaof/sailfish-runner
docker push zeidaof/sailfish-runner

docker build ./gateway -t zeidaof/sailfish-gateway
docker push zeidaof/sailfish-gateway
