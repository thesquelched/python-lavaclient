0.2.4
-----
* Add `service_users` methods
* `clusters.create` now displays ambari read-only user info, if available

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
