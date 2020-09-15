Feature: Users can login with a password

    Scenario: A user cannot login using a password if password authentication is disabled
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And "myuser" will log in with password "password"
        When I "GET" "/v1/users"
        Then I get a "401" response code

    Scenario: A user can login with a password if it is enabled
        Given I have installed the system
        And user "myuser" exists
        And user "myuser" has a keypair with password "password"
        And user "myuser" can login with a password
        And "myuser" will log in with password "password"
        When I "GET" "/v1/users"
        Then I get a "200" response code
