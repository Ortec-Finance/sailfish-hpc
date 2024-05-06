
# Start all s2i build commands in the background
s2i build gateway registry.access.redhat.com/ubi9/python-311:latest gateway &
s2i build run-manager registry.access.redhat.com/ubi9/python-311:latest run-manager &
s2i build runner registry.access.redhat.com/ubi9/python-311:latest runner &

# Wait for all background jobs to finish
wait