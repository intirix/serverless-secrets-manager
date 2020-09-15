Feature: Users can manage their secrets

    Scenario: A user with no secrets can get an empty list of secrets back
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And path parameter "username" is set to "myuser"
        And "myuser" will log in with password "password"
        When I "GET" "/v1/users/{username}/secrets"
        Then I get a "200" response code

    Scenario: A user can create a secret
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And I will create a secret
        And the secret field "website" is set to "www.google.com"
        And user "myuser" encrypts the secret into the POST data
        And "myuser" will log in with password "password"
        When I "POST" "/v1/secrets"
        Then I get a "201" response code

    Scenario: A user can get a secret that they should have access to
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And user "myuser" has created a secret
        And path parameter "sid" is the secret id
        And "myuser" will log in with password "password"
        When I "GET" "/v1/secrets/{sid}"
        Then I get a "200" response code

    Scenario: A user list secrets if they have one
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And user "myuser" has created a secret
        And path parameter "username" is set to "myuser"
        And "myuser" will log in with password "password"
        When I "GET" "/v1/users/{username}/secrets"
        Then I get a "200" response code

    Scenario: A user cannot get a secret that they don't have access to
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And user "myuser" has created a secret
        And path parameter "sid" is the secret id
        And "admin" will log in with password "password"
        When I "GET" "/v1/secrets/{sid}"
        Then I get a "403" response code

    Scenario: A user can update a secret that they have access to
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And user "myuser" has created a secret
        And the secret field "website" is set to "www.google.com"
        And user "myuser" re-encrypts the secret into the POST data
        And path parameter "sid" is the secret id
        And "myuser" will log in with password "password"
        When I "PUT" "/v1/secrets/{sid}"
        Then I get a "200" response code

    Scenario: A user cannot update a secret that they don't have access to
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And user "myuser" has created a secret
        And the secret field "website" is set to "www.google.com"
        And user "myuser" re-encrypts the secret into the POST data
        And path parameter "sid" is the secret id
        And "admin" will log in with password "password"
        When I "PUT" "/v1/secrets/{sid}"
        Then I get a "403" response code
