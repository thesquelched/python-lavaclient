0.2.10
------
* CLI
    * Fix unformatted output for single-item requests, e.g. `clusters get`

0.2.9
-----
* CLI
    * Fixed --version flag
    * Updated cluster node groups format to show component names instead of
      raw JSON
    * Sort cluster nodes by name
* You may now SSH to any cluster not in ERROR status, including IMPAIRED
  clusters

0.2.8
-----
* CLI
    * Add update_credentials and delete_ssh_credentials commands
    * Remove restrictions on credential names in type=name pairs
* Add configurable request timeouts and retries on network errors and 503 responses

0.2.7
-----
* CLI
    * Improve stacks display
    * Add --force options to delete methods to skip confirm dialog

0.2.6
-----
* Fix SSH methods bug in which ambari node is targeted

0.2.5
-----
* General
    * Add ambari credential management methods
    * Re-enabled stacks create/delete

0.2.4
-----
* General
    * Add ssh_tunnel method/command to help set up SSH tunnels to a cluster
    * Add additional debugging levels
    * Get V2 API endpoints from service catalog

* CLI
    * Improve display for node components
    * Add confirmations for delete methods, e.g. `clusters delete`
    * Piping output to another command disables pretty printing so that it is
      easier to parse

0.2.3
-----
* Fix cluster create bug in CLI in which missing credentials are not detected
  properly
* Update dependencies for keystoneclient and oslo.i18n to avoid library
  conflict issue

0.2.2
-----
* Client
    * Let `node_groups` argument be a nested dict, in addition to the original
      list of dicts format
* CLI
    * Add prompt to `cluster create` to confirm whether ssh credential should
      automatically be created from `$HOME/.ssh/id_rsa.pub`

0.2.1
-----
* Initial release
