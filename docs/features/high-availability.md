# High Availabilty
While Sailfish Runners and Managers already are resilient as they run across multiple availability zones and can spin back up upon failures, The broker does not.

By enabling this component you instead spin up two to three instances of the Sailfish-Broker. The `messageMigration` feature is enabled which will handle the migration of messages in the case of a Broker shutting down in a certain zone.

## Compatibility
This feature is not compatible with the `ephemeral-broker` as the `messageMigration` feature requires the use of PersistentVolumes.

