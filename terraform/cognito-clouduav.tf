################################################################
## This file creates a Cognito Identity pool                   #
## named clouduav.                                             #
################################################################

// todo:  create cognito identity_pool and user_pool

resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = "clouduav identity pool"
  allow_unauthenticated_identities = false
}