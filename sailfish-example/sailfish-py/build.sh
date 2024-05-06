
# Start all s2i build commands in the background
s2i build gateway registry.access.redhat.com/ubi9/python-311:latest gateway &
s2i build manager registry.access.redhat.com/ubi9/python-311:latest manager &
s2i build worker registry.access.redhat.com/ubi9/python-311:latest worker &

# Wait for all background jobs to finish
wait