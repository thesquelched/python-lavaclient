0.2.5
-----
* General
    * Add ambari credential management methods

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
